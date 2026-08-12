(() => {
    "use strict";

    /*
     * X Image Downloader
     * v3.2 X Import Assistant
     *
     * 作用：
     * 1. 在 x.com 页面运行
     * 2. 监听 X Web App 自己发出的 GraphQL 请求
     * 3. 提取 Likes / Bookmarks 中出现的帖子
     * 4. 只把公开的帖子/媒体信息发送给我们的下载器
     *
     * 注意：
     * - 不读取密码
     * - 不读取 auth_token
     * - 不读取 Cookie
     * - 不把登录凭证发送给服务器
     */

    const VERSION = "3.2.0";

    const STORAGE_KEY = "x_image_downloader_import_state";

    let mode = null;
    let running = false;
    let captured = new Map();

    function log(...args) {
        console.log(
            "[X Image Downloader]",
            ...args
        );
    }

    function getApiBase() {
        /*
         * 当前脚本默认认为：
         * x-import.js 是由你的 X 图片找图器提供。
         *
         * bookmarklet 加载它时，会把当前页面的数据
         * 发送回你的站点。
         */

        const script =
            document.currentScript;

        if (
            script &&
            script.src
        ) {
            try {
                return new URL(
                    script.src
                ).origin;
            } catch (_) {}
        }

        return "";
    }

    function showMessage(
        message,
        type = "info"
    ) {
        let box =
            document.getElementById(
                "xid-import-box"
            );

        if (!box) {
            box =
                document.createElement(
                    "div"
                );

            box.id =
                "xid-import-box";

            box.style.position =
                "fixed";

            box.style.left = "12px";
            box.style.right = "12px";
            box.style.bottom = "20px";

            box.style.zIndex =
                "2147483647";

            box.style.padding =
                "14px 16px";

            box.style.borderRadius =
                "14px";

            box.style.background =
                "rgba(20,20,20,.94)";

            box.style.color =
                "white";

            box.style.fontSize =
                "14px";

            box.style.lineHeight =
                "1.5";

            box.style.fontFamily =
                "-apple-system,BlinkMacSystemFont,sans-serif";

            box.style.boxShadow =
                "0 5px 30px rgba(0,0,0,.35)";

            document.body.appendChild(
                box
            );
        }

        box.textContent =
            message;

        if (type === "error") {
            box.style.background =
                "rgba(180,30,30,.96)";
        } else if (
            type === "success"
        ) {
            box.style.background =
                "rgba(20,120,70,.96)";
        } else {
            box.style.background =
                "rgba(20,20,20,.94)";
        }
    }

    function getModeFromUrl() {
        const path =
            location.pathname;

        if (
            path.includes(
                "/bookmarks"
            )
        ) {
            return "bookmarks";
        }

        if (
            path.includes(
                "/likes"
            )
        ) {
            return "likes";
        }

        return null;
    }

    function extractTweetObjects(
        value,
        result = []
    ) {
        if (!value) {
            return result;
        }

        if (
            typeof value !==
            "object"
        ) {
            return result;
        }

        if (
            Array.isArray(value)
        ) {
            for (
                const item of value
            ) {
                extractTweetObjects(
                    item,
                    result
                );
            }

            return result;
        }

        /*
         * X 不同版本可能使用：
         *
         * tweet
         * tweet_results
         * result
         * legacy
         *
         * 所以这里不绑定单一结构。
         */

        if (
            value.rest_id &&
            (
                value.legacy ||
                value.core
            )
        ) {
            result.push(value);
        }

        if (
            value.__typename ===
                "Tweet" &&
            (
                value.rest_id ||
                value.legacy
            )
        ) {
            result.push(value);
        }

        for (
            const key of Object.keys(
                value
            )
        ) {
            try {
                extractTweetObjects(
                    value[key],
                    result
                );
            } catch (_) {}
        }

        return result;
    }

    function normalizeTweet(
        tweet
    ) {
        if (!tweet) {
            return null;
        }

        const legacy =
            tweet.legacy ||
            tweet;

        const id =
            String(
                tweet.rest_id ||
                legacy.id_str ||
                legacy.id ||
                ""
            );

        if (!id) {
            return null;
        }

        let username = "";

        try {
            username =
                tweet.core
                    ?.user_results
                    ?.result
                    ?.legacy
                    ?.screen_name ||
                tweet.core
                    ?.user_results
                    ?.result
                    ?.core
                    ?.screen_name ||
                "";
        } catch (_) {}

        if (!username) {
            try {
                username =
                    legacy.user
                        ?.screen_name ||
                    "";
            } catch (_) {}
        }

        const text =
            legacy.full_text ||
            legacy.text ||
            "";

        const createdAt =
            legacy.created_at ||
            "";

        const entities =
            legacy.entities ||
            {};

        const media =
            entities.media ||
            [];

        const photos = [];

        for (
            const item of media
        ) {
            if (
                !item ||
                !item.media_url_https
            ) {
                continue;
            }

            const type =
                item.type || "";

            if (
                type === "photo"
            ) {
                photos.push({
                    url:
                        item.media_url_https,
                    media_url:
                        item.media_url_https,
                    type: "photo",
                    width:
                        item.original_info
                            ?.width ||
                        null,
                    height:
                        item.original_info
                            ?.height ||
                        null,
                    alt:
                        item.ext_alt_text ||
                        ""
                });
            }
        }

        return {
            tweet_id: id,

            tweet_url:
                username
                    ? `https://x.com/${username}/status/${id}`
                    : `https://x.com/i/status/${id}`,

            username,

            text,

            created_at:
                createdAt,

            photos
        };
    }

    function collectFromJson(
        json
    ) {
        const tweets =
            extractTweetObjects(
                json
            );

        let added = 0;

        for (
            const tweet of tweets
        ) {
            const normalized =
                normalizeTweet(
                    tweet
                );

            if (
                !normalized
            ) {
                continue;
            }

            if (
                captured.has(
                    normalized.tweet_id
                )
            ) {
                continue;
            }

            captured.set(
                normalized.tweet_id,
                normalized
            );

            added++;
        }

        if (added > 0) {
            log(
                "捕获新帖子：",
                added,
                "当前总数：",
                captured.size
            );

            updateCounter();
        }
    }

    function updateCounter() {
        showMessage(
            `正在读取 X ${mode === "likes" ? "喜欢" : "书签"}…… 已发现 ${captured.size} 条帖子`
        );
    }

    function tryParseText(
        text
    ) {
        if (
            !text ||
            typeof text !==
                "string"
        ) {
            return;
        }

        const trimmed =
            text.trim();

        if (
            !trimmed.startsWith(
                "{"
            ) &&
            !trimmed.startsWith(
                "["
            )
        ) {
            return;
        }

        try {
            const json =
                JSON.parse(
                    trimmed
                );

            collectFromJson(
                json
            );
        } catch (_) {}
    }

    function installFetchHook() {
        if (
            window
                .__XID_FETCH_HOOKED
        ) {
            return;
        }

        window
            .__XID_FETCH_HOOKED =
            true;

        const originalFetch =
            window.fetch;

        window.fetch =
            async function (
                ...args
            ) {
                const response =
                    await originalFetch.apply(
                        this,
                        args
                    );

                try {
                    const requestUrl =
                        typeof args[0] ===
                        "string"
                            ? args[0]
                            : args[0]
                                ?.url ||
                              "";

                    if (
                        requestUrl.includes(
                            "/graphql/"
                        )
                    ) {
                        const clone =
                            response.clone();

                        clone
                            .text()
                            .then(
                                text => {
                                    tryParseText(
                                        text
                                    );
                                }
                            )
                            .catch(
                                () => {}
                            );
                    }
                } catch (_) {}

                return response;
            };
    }

    function installXhrHook() {
        if (
            window
                .__XID_XHR_HOOKED
        ) {
            return;
        }

        window
            .__XID_XHR_HOOKED =
            true;

        const originalOpen =
            XMLHttpRequest
                .prototype
                .open;

        const originalSend =
            XMLHttpRequest
                .prototype
                .send;

        XMLHttpRequest
            .prototype
            .open =
            function (
                method,
                url,
                ...rest
            ) {
                this.__xid_url =
                    String(
                        url || ""
                    );

                return originalOpen.call(
                    this,
                    method,
                    url,
                    ...rest
                );
            };

        XMLHttpRequest
            .prototype
            .send =
            function (...args) {
                try {
                    this.addEventListener(
                        "load",
                        function () {
                            try {
                                const url =
                                    this.__xid_url ||
                                    "";

                                if (
                                    !url.includes(
                                        "/graphql/"
                                    )
                                ) {
                                    return;
                                }

                                tryParseText(
                                    this.responseText
                                );
                            } catch (_) {}
                        }
                    );
                } catch (_) {}

                return originalSend.apply(
                    this,
                    args
                );
            };
    }

    async function sendToServer() {
        const base =
            getApiBase();

        if (!base) {
            throw new Error(
                "无法确定 X 图片找图器地址"
            );
        }

        const items =
            Array.from(
                captured.values()
            );

        const response =
            await fetch(
                `${base}/api/x-import`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            mode,
                            items
                        })
                }
            );

        if (
            !response.ok
        ) {
            throw new Error(
                `服务器返回 ${response.status}`
            );
        }

        return response.json();
    }

    function createButton() {
        if (
            document.getElementById(
                "xid-import-button"
            )
        ) {
            return;
        }

        const button =
            document.createElement(
                "button"
            );

        button.id =
            "xid-import-button";

        button.textContent =
            "导入到 X 图片找图器";

        button.style.position =
            "fixed";

        button.style.right =
            "14px";

        button.style.bottom =
            "95px";

        button.style.zIndex =
            "2147483647";

        button.style.border =
            "0";

        button.style.borderRadius =
            "999px";

        button.style.padding =
            "12px 16px";

        button.style.background =
            "#111";

        button.style.color =
            "#fff";

        button.style.fontSize =
            "14px";

        button.style.fontWeight =
            "600";

        button.style.boxShadow =
            "0 4px 18px rgba(0,0,0,.3)";

        button.addEventListener(
            "click",
            async () => {
                if (
                    running
                ) {
                    return;
                }

                running = true;

                try {
                    showMessage(
                        `正在读取 X ${mode === "likes" ? "喜欢" : "书签"}……`
                    );

                    /*
                     * 重新加载当前页面。
                     *
                     * fetch/XHR hook 会在页面重新加载后失效，
                     * 所以这里不立即 reload。
                     *
                     * 用户继续向下滚动，
                     * X 会加载新的 GraphQL 数据，
                     * 我们会自动捕获。
                     */

                    await new Promise(
                        resolve =>
                            setTimeout(
                                resolve,
                                800
                            )
                    );

                    const result =
                        await sendToServer();

                    showMessage(
                        `已导入 ${result.count || 0} 条帖子，其中图片 ${result.photo_count || 0} 张`,
                        "success"
                    );
                } catch (
                    error
                ) {
                    console.error(
                        error
                    );

                    showMessage(
                        "导入失败：" +
                            error.message,
                        "error"
                    );
                } finally {
                    running =
                        false;
                }
            }
        );

        document.body.appendChild(
            button
        );
    }

    function start() {
        mode =
            getModeFromUrl();

        if (!mode) {
            alert(
                "请先打开 X 的「喜欢」或「书签」页面，再运行 X 图片找图器导入助手。"
            );

            return;
        }

        installFetchHook();

        installXhrHook();

        createButton();

        showMessage(
            `X 图片找图器已连接：${mode === "likes" ? "❤️ 喜欢" : "🔖 书签"}。请继续向下滚动 X，数据会自动捕获。`
        );

        log(
            "v" +
                VERSION +
                " started",
            mode
        );
    }

    start();
})();
