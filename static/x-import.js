(() => {
    "use strict";

    /*
     * =========================================================
     * X Image Downloader
     * V3.2 X Import Assistant
     *
     * 修正版
     *
     * 功能：
     * 1. 在 X Likes / Bookmarks 页面运行
     * 2. 监听 X GraphQL 请求
     * 3. 自动捕获帖子
     * 4. 提取图片
     * 5. 转换为 X Media Finder V3.2 媒体库格式
     * 6. 上传到 Render
     * =========================================================
     */

    const VERSION = "3.2.1";

    /*
     * =========================================================
     * Render 后端
     *
     * 不再依赖 document.currentScript
     * 防止 Safari / Via / Violentmonkey 环境下地址获取失败
     * =========================================================
     */

    const API_BASE =
        "https://x-v1.onrender.com";

    const IMPORT_API =
        API_BASE + "/api/import-media";


    /*
     * =========================================================
     * 状态
     * =========================================================
     */

    let mode = null;

    let running = false;

    const captured = new Map();


    /*
     * =========================================================
     * 日志
     * =========================================================
     */

    function log(...args) {

        console.log(
            "[X Image Downloader]",
            ...args
        );

    }


    /*
     * =========================================================
     * 提示框
     * =========================================================
     */

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

            Object.assign(
                box.style,
                {
                    position: "fixed",
                    left: "12px",
                    right: "12px",
                    bottom: "20px",
                    zIndex: "2147483647",
                    padding: "14px 16px",
                    borderRadius: "14px",
                    color: "white",
                    fontSize: "14px",
                    lineHeight: "1.5",
                    fontFamily:
                        "-apple-system,BlinkMacSystemFont,sans-serif",
                    boxShadow:
                        "0 5px 30px rgba(0,0,0,.35)"
                }
            );

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


    /*
     * =========================================================
     * 判断当前页面
     * =========================================================
     */

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


    /*
     * =========================================================
     * 递归寻找 Tweet 对象
     * =========================================================
     */

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
         * X 可能使用：
         *
         * tweet
         * tweet_results
         * result
         * legacy
         */

        if (
            value.rest_id &&
            (
                value.legacy ||
                value.core
            )
        ) {

            result.push(
                value
            );
        }

        if (
            value.__typename ===
                "Tweet" &&
            (
                value.rest_id ||
                value.legacy
            )
        ) {

            result.push(
                value
            );
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


    /*
     * =========================================================
     * Tweet 标准化
     * =========================================================
     */

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

        /*
         * 用户名
         */

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


        /*
         * 文本
         */

        const text =
            legacy.full_text ||
            legacy.text ||
            "";


        /*
         * 时间
         */

        const createdAt =
            legacy.created_at ||
            "";


        /*
         * 媒体
         */

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
                item.type ||
                "";


            /*
             * 当前阶段先导入图片
             */

            if (
                type === "photo"
            ) {

                const mediaUrl =
                    item.media_url_https;


                const originalUrl =
                    mediaUrl +
                    "?format=jpg&name=orig";


                photos.push({

                    type: "image",

                    url:
                        mediaUrl,

                    originalUrl:
                        originalUrl,

                    thumbnail:
                        mediaUrl,

                    width:
                        item.original_info
                            ?.width ||
                        0,

                    height:
                        item.original_info
                            ?.height ||
                        0,

                    bitrate: 0,

                    streamType:
                        ""

                });
            }
        }


        /*
         * 没有图片就暂时不加入
         */

        if (
            photos.length === 0
        ) {

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

                media: []

            };
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

            media:
                photos

        };
    }


    /*
     * =========================================================
     * 从 JSON 捕获
     * =========================================================
     */

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

            /*
             * 没有媒体的不保存
             */

            if (
                !normalized.media ||
                normalized.media.length === 0
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


        if (
            added > 0
        ) {

            log(
                "捕获新帖子：",
                added,
                "当前总数：",
                captured.size
            );

            updateCounter();
        }
    }


    /*
     * =========================================================
     * 解析文本
     * =========================================================
     */

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


    /*
     * =========================================================
     * Fetch Hook
     * =========================================================
     */

    function installFetchHook() {

        if (
            window.__XID_FETCH_HOOKED
        ) {

            return;
        }

        window.__XID_FETCH_HOOKED =
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


    /*
     * =========================================================
     * XHR Hook
     * =========================================================
     */

    function installXhrHook() {

        if (
            window.__XID_XHR_HOOKED
        ) {

            return;
        }

        window.__XID_XHR_HOOKED =
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
            function (
                ...args
            ) {

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


    /*
     * =========================================================
     * 转换成 app.py 所需要的格式
     *
     * app.py:
     *
     * POST /api/import-media
     *
     * {
     *   items: [...]
     * }
     * =========================================================
     */

    function buildUploadItems() {

        const items = [];


        for (
            const tweet of
            captured.values()
        ) {

            if (
                !tweet.media ||
                tweet.media.length === 0
            ) {

                continue;
            }


            items.push({

                tweet_id:
                    tweet.tweet_id,

                tweet_url:
                    tweet.tweet_url,

                author:
                    tweet.username,

                source:
                    mode,

                media:
                    tweet.media
            });
        }


        return items;
    }


    /*
     * =========================================================
     * 上传到 Render
     * =========================================================
     */

    async function sendToServer() {

        const items =
            buildUploadItems();


        if (
            items.length === 0
        ) {

            throw new Error(
                "目前没有捕获到可上传的媒体，请先继续向下滚动页面。"
            );
        }


        showMessage(
            `正在上传 ${items.length} 条帖子……`
        );


        let response;


        try {

            response =
                await fetch(
                    IMPORT_API,
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                items:
                                    items
                            })
                    }
                );

        } catch (error) {

            throw new Error(
                "无法连接 Render："
                +
                (
                    error.message ||
                    "网络请求失败"
                )
            );
        }


        let result = null;


        try {

            result =
                await response.json();

        } catch (_) {

            result = null;
        }


        if (
            !response.ok
        ) {

            const detail =
                result?.detail ||
                `服务器返回 HTTP ${response.status}`;

            throw new Error(
                detail
            );
        }


        return (
            result || {}
        );
    }


    /*
     * =========================================================
     * 统计提示
     * =========================================================
     */

    function updateCounter() {

        showMessage(
            `正在读取 X ${
                mode === "likes"
                    ? "喜欢"
                    : "书签"
            }…… 已发现 ${
                captured.size
            } 条含媒体帖子`
        );
    }


    /*
     * =========================================================
     * 创建上传按钮
     * =========================================================
     */

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
            "上传到媒体库";


        Object.assign(
            button.style,
            {
                position: "fixed",
                right: "14px",
                bottom: "95px",
                zIndex: "2147483647",
                border: "0",
                borderRadius: "999px",
                padding: "12px 16px",
                background: "#111",
                color: "#fff",
                fontSize: "14px",
                fontWeight: "600",
                boxShadow:
                    "0 4px 18px rgba(0,0,0,.3)"
            }
        );


        button.addEventListener(
            "click",
            async () => {

                if (running) {
                    return;
                }


                running = true;


                try {

                    if (
                        captured.size === 0
                    ) {

                        throw new Error(
                            "还没有捕获到媒体，请先向下滚动 Likes / Bookmarks 页面。"
                        );
                    }


                    showMessage(
                        `正在上传 ${captured.size} 条帖子……`
                    );


                    const result =
                        await sendToServer();


                    showMessage(
                        `上传成功！新增 ${result.added || 0} 条，重复 ${result.duplicates || 0} 条，媒体库共 ${result.total || 0} 条。`,
                        "success"
                    );


                    log(
                        "上传成功：",
                        result
                    );


                } catch (
                    error
                ) {

                    console.error(
                        "[XID] 上传失败",
                        error
                    );


                    showMessage(
                        "上传失败："
                        +
                        (
                            error.message ||
                            "未知错误"
                        ),
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


    /*
     * =========================================================
     * 启动
     * =========================================================
     */

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
            `X 图片找图器已连接：${
                mode === "likes"
                    ? "❤️ 喜欢"
                    : "🔖 书签"
            }。请继续向下滚动 X，数据会自动捕获。`
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
