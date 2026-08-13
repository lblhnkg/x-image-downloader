(() => {
    "use strict";

    /*
     * ==========================================
     * X Image Downloader
     * V3.2 X Import Assistant
     *
     * 功能：
     *
     * 1. 运行在 X.com
     * 2. 监听 X GraphQL 请求
     * 3. 自动捕获 Likes / Bookmarks 中出现的 Tweet
     * 4. 提取图片
     * 5. 提取 MP4 视频
     * 6. 自动去重
     * 7. 上传到 /api/import-media
     *
     * 注意：
     * 不读取密码
     * 不读取 auth_token
     * 不读取 Cookie
     * 不向服务器发送登录凭证
     * ==========================================
     */

    const VERSION = "3.2.1";

    /*
     * Render 后端
     *
     * 直接固定项目地址。
     * 这样即使 document.currentScript
     * 在 Via / Safari 注入脚本环境中为空，
     * 也不会出现无法确定服务器地址的问题。
     */

    const API_BASE =
        "https://x-v1.onrender.com";

    let mode = null;

    let running = false;

    /*
     * tweet_id -> tweet
     */

    const captured = new Map();


    /* ==========================================
     * 日志
     * ========================================== */

    function log(...args) {

        console.log(
            "[X Image Downloader]",
            ...args
        );

    }


    /* ==========================================
     * 消息提示
     * ========================================== */

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
                    background:
                        "rgba(20,20,20,.94)",
                    color: "#fff",
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


    /* ==========================================
     * 判断 Likes / Bookmarks
     * ========================================== */

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


    /* ==========================================
     * 递归寻找 Tweet
     * ========================================== */

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
         * X 不同 GraphQL 版本
         * 结构可能不同。
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


    /* ==========================================
     * 获取用户名
     * ========================================== */

    function getUsername(
        tweet,
        legacy
    ) {

        let username = "";

        try {

            username =
                tweet
                    ?.core
                    ?.user_results
                    ?.result
                    ?.legacy
                    ?.screen_name ||
                "";

        } catch (_) {}

        if (!username) {

            try {

                username =
                    tweet
                        ?.core
                        ?.user_results
                        ?.result
                        ?.core
                        ?.screen_name ||
                    "";

            } catch (_) {}
        }

        if (!username) {

            try {

                username =
                    legacy
                        ?.user
                        ?.screen_name ||
                    "";

            } catch (_) {}
        }

        return username;
    }


    /* ==========================================
     * 视频最佳地址
     * ========================================== */

    function chooseBestVideo(
        variants
    ) {

        if (
            !Array.isArray(
                variants
            )
        ) {

            return null;
        }

        const mp4s =
            variants.filter(
                item =>
                    item &&
                    item.url &&
                    (
                        !item.content_type ||
                        item.content_type
                            .includes(
                                "video/mp4"
                            )
                    )
            );

        if (!mp4s.length) {
            return null;
        }

        mp4s.sort(
            function (a, b) {

                const aBitrate =
                    Number(
                        a.bitrate || 0
                    );

                const bBitrate =
                    Number(
                        b.bitrate || 0
                    );

                return (
                    bBitrate -
                    aBitrate
                );
            }
        );

        return mp4s[0];
    }


    /* ==========================================
     * 提取媒体
     * ========================================== */

    function extractMedia(
        legacy
    ) {

        const media = [];

        /*
         * 优先使用 extended_entities
         *
         * 因为它通常包含完整媒体信息。
         */

        const extended =
            legacy
                ?.extended_entities
                ?.media;

        const normal =
            legacy
                ?.entities
                ?.media;

        const rawMedia =
            Array.isArray(
                extended
            )
                ? extended
                : Array.isArray(
                    normal
                )
                    ? normal
                    : [];

        for (
            const item of rawMedia
        ) {

            if (!item) {
                continue;
            }

            const type =
                item.type || "";

            /*
             * ==============================
             * 图片
             * ==============================
             */

            if (
                type === "photo" &&
                item.media_url_https
            ) {

                const clean =
                    String(
                        item.media_url_https
                    ).split("?")[0];

                const exists =
                    media.some(
                        old =>
                            old.type ===
                                "image" &&
                            old.url ===
                                clean
                    );

                if (
                    !exists
                ) {

                    media.push({

                        type: "image",

                        url: clean,

                        originalUrl:
                            clean +
                            "?format=jpg&name=orig",

                        thumbnail:
                            clean,

                        streamType:
                            "",

                        width:
                            Number(
                                item
                                    ?.original_info
                                    ?.width ||
                                0
                            ),

                        height:
                            Number(
                                item
                                    ?.original_info
                                    ?.height ||
                                0
                            ),

                        bitrate: 0
                    });
                }

                continue;
            }


            /*
             * ==============================
             * 视频 / GIF
             * ==============================
             *
             * X 的 GIF 通常也属于 video。
             */

            if (
                (
                    type === "video" ||
                    type === "animated_gif"
                ) &&
                item.video_info
            ) {

                const best =
                    chooseBestVideo(
                        item
                            .video_info
                            .variants
                    );

                if (
                    !best ||
                    !best.url
                ) {

                    continue;
                }

                const videoUrl =
                    best.url;

                const exists =
                    media.some(
                        old =>
                            old.type ===
                                "video" &&
                            old.url ===
                                videoUrl
                    );

                if (
                    exists
                ) {

                    continue;
                }

                media.push({

                    type: "video",

                    url:
                        videoUrl,

                    originalUrl:
                        videoUrl,

                    thumbnail:
                        item
                            .media_url_https ||
                        "",

                    streamType:
                        "mp4",

                    width:
                        Number(
                            item
                                ?.original_info
                                ?.width ||
                            item
                                ?.video_info
                                ?.width ||
                            0
                        ),

                    height:
                        Number(
                            item
                                ?.original_info
                                ?.height ||
                            item
                                ?.video_info
                                ?.height ||
                            0
                        ),

                    bitrate:
                        Number(
                            best.bitrate ||
                            0
                        )
                });
            }
        }

        return media;
    }


    /* ==========================================
     * 标准化 Tweet
     * ========================================== */

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

        const username =
            getUsername(
                tweet,
                legacy
            );

        const text =
            legacy.full_text ||
            legacy.text ||
            "";

        const createdAt =
            legacy.created_at ||
            "";

        const media =
            extractMedia(
                legacy
            );

        /*
         * 没有媒体的 Tweet
         * 不进入媒体库。
         */

        if (!media.length) {
            return null;
        }

        return {

            tweet_id:
                id,

            tweet_url:
                username
                    ? `https://x.com/${username}/status/${id}`
                    : `https://x.com/i/status/${id}`,

            username:
                username,

            author:
                username,

            text:
                text,

            created_at:
                createdAt,

            source:
                mode,

            media:
                media
        };
    }


    /* ==========================================
     * 合并 Tweet
     *
     * 解决：
     *
     * 第一次 GraphQL：
     * 只有图片
     *
     * 第二次 GraphQL：
     * 出现视频
     *
     * 不能因为 Tweet 已经存在
     * 就把第二次数据丢掉。
     * ========================================== */

    function mergeTweet(
        oldTweet,
        newTweet
    ) {

        if (!oldTweet) {
            return newTweet;
        }

        const oldMedia =
            Array.isArray(
                oldTweet.media
            )
                ? oldTweet.media
                : [];

        const newMedia =
            Array.isArray(
                newTweet.media
            )
                ? newTweet.media
                : [];

        const merged =
            [
                ...oldMedia
            ];

        for (
            const item of newMedia
        ) {

            if (!item) {
                continue;
            }

            const exists =
                merged.some(
                    old =>
                        old.type ===
                            item.type &&
                        old.url ===
                            item.url
                );

            if (
                !exists
            ) {

                merged.push(
                    item
                );
            }
        }

        oldTweet.media =
            merged;

        if (
            !oldTweet.username &&
            newTweet.username
        ) {

            oldTweet.username =
                newTweet.username;
        }

        if (
            !oldTweet.author &&
            newTweet.author
        ) {

            oldTweet.author =
                newTweet.author;
        }

        if (
            !oldTweet.tweet_url &&
            newTweet.tweet_url
        ) {

            oldTweet.tweet_url =
                newTweet.tweet_url;
        }

        if (
            !oldTweet.text &&
            newTweet.text
        ) {

            oldTweet.text =
                newTweet.text;
        }

        return oldTweet;
    }


    /* ==========================================
     * 从 JSON 捕获
     * ========================================== */

    function collectFromJson(
        json
    ) {

        const tweets =
            extractTweetObjects(
                json
            );

        let addedTweets = 0;

        let addedMedia = 0;

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

            const old =
                captured.get(
                    normalized.tweet_id
                );

            if (!old) {

                captured.set(
                    normalized.tweet_id,
                    normalized
                );

                addedTweets += 1;

                addedMedia +=
                    normalized.media.length;

                continue;
            }

            const before =
                old.media.length;

            const merged =
                mergeTweet(
                    old,
                    normalized
                );

            captured.set(
                normalized.tweet_id,
                merged
            );

            addedMedia +=
                Math.max(
                    0,
                    merged.media.length -
                    before
                );
        }

        if (
            addedTweets ||
            addedMedia
        ) {

            log(
                "捕获：",
                addedTweets,
                "条新帖子，",
                addedMedia,
                "个新媒体，",
                "当前帖子：",
                captured.size
            );

            updateCounter();
        }
    }


    /* ==========================================
     * JSON 文本解析
     * ========================================== */

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


    /* ==========================================
     * Fetch Hook
     * ========================================== */

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


    /* ==========================================
     * XHR Hook
     * ========================================== */

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


    /* ==========================================
     * 统计媒体数量
     * ========================================== */

    function getMediaCount() {

        let count = 0;

        for (
            const tweet of
                captured.values()
        ) {

            count +=
                Array.isArray(
                    tweet.media
                )
                    ? tweet.media.length
                    : 0;
        }

        return count;
    }


    /* ==========================================
     * 更新计数
     * ========================================== */

    function updateCounter() {

        const mediaCount =
            getMediaCount();

        showMessage(
            `正在读取 X ${
                mode === "likes"
                    ? "喜欢"
                    : "书签"
            }…… 已发现 ${
                captured.size
            } 条帖子 / ${
                mediaCount
            } 个媒体`
        );
    }


    /* ==========================================
     * 读取后端错误
     * ========================================== */

    async function getResponseError(
        response
    ) {

        let message =
            `服务器返回 HTTP ${response.status}`;

        try {

            const text =
                await response.text();

            if (!text) {
                return message;
            }

            try {

                const data =
                    JSON.parse(
                        text
                    );

                if (
                    data.detail
                ) {

                    message +=
                        `：${data.detail}`;

                } else {

                    message +=
                        `：${text}`;
                }

            } catch (_) {

                message +=
                    `：${text}`;
            }

        } catch (_) {}

        return message;
    }


    /* ==========================================
     * 上传服务器
     * ========================================== */

    async function sendToServer() {

        const items =
            Array.from(
                captured.values()
            );

        if (!items.length) {

            throw new Error(
                "目前还没有捕获到包含媒体的帖子，请先继续向下滚动。"
            );
        }

        /*
         * 再次清理：
         *
         * 防止没有媒体的 Tweet
         * 被发送到服务器。
         */

        const cleanItems =
            items
                .map(
                    item => {

                        const media =
                            Array.isArray(
                                item.media
                            )
                                ? item.media.filter(
                                    media =>
                                        media &&
                                        (
                                            media.type ===
                                                "image" ||
                                            media.type ===
                                                "video"
                                        ) &&
                                        media.url
                                )
                                : [];

                        return {

                            tweet_id:
                                item.tweet_id,

                            tweet_url:
                                item.tweet_url,

                            author:
                                item.author ||
                                item.username ||
                                "",

                            source:
                                mode,

                            media:
                                media
                        };
                    }
                )
                .filter(
                    item =>
                        item.media.length > 0
                );

        if (!cleanItems.length) {

            throw new Error(
                "没有找到可以上传的图片或视频。"
            );
        }

        log(
            "准备上传：",
            cleanItems.length,
            "条帖子，",
            cleanItems.reduce(
                (
                    total,
                    item
                ) =>
                    total +
                    item.media.length,
                0
            ),
            "个媒体"
        );

        let response;

        try {

            response =
                await fetch(
                    `${API_BASE}/api/import-media`,
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                mode:
                                    mode,

                                items:
                                    cleanItems
                            })
                    }
                );

        } catch (error) {

            throw new Error(
                "无法连接 Render 服务器：" +
                (
                    error?.message ||
                    error
                )
            );
        }

        if (
            !response.ok
        ) {

            throw new Error(
                await getResponseError(
                    response
                )
            );
        }

        let result;

        try {

            result =
                await response.json();

        } catch (_) {

            throw new Error(
                "服务器返回的数据不是有效 JSON。"
            );
        }

        if (
            result &&
            result.ok === false
        ) {

            throw new Error(
                result.detail ||
                "服务器拒绝了上传。"
            );
        }

        return result;
    }


    /* ==========================================
     * 创建按钮
     * ========================================== */

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

                if (
                    running
                ) {

                    return;
                }

                running = true;

                button.disabled =
                    true;

                button.style.opacity =
                    "0.6";

                try {

                    const mediaCount =
                        getMediaCount();

                    if (
                        mediaCount === 0
                    ) {

                        throw new Error(
                            "目前没有捕获到媒体。请先在 Likes / Bookmarks 页面向下滚动，让 X 加载一些帖子。"
                        );
                    }

                    showMessage(
                        `正在上传 ${captured.size} 条帖子 / ${mediaCount} 个媒体……`
                    );

                    const result =
                        await sendToServer();

                    const imported =
                        Number(
                            result.imported ||
                            0
                        );

                    const added =
                        Number(
                            result.added ||
                            0
                        );

                    const duplicates =
                        Number(
                            result.duplicates ||
                            0
                        );

                    showMessage(
                        `上传成功：共处理 ${imported} 个媒体，新增 ${added} 个，重复 ${duplicates} 个。媒体库共 ${result.total || 0} 个媒体。`,
                        "success"
                    );

                } catch (
                    error
                ) {

                    console.error(
                        "[X Image Downloader] 上传失败",
                        error
                    );

                    showMessage(
                        "导入失败：" +
                        (
                            error?.message ||
                            String(error)
                        ),
                        "error"
                    );

                } finally {

                    running =
                        false;

                    button.disabled =
                        false;

                    button.style.opacity =
                        "1";
                }
            }
        );

        document.body.appendChild(
            button
        );
    }


    /* ==========================================
     * 初始化
     * ========================================== */

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
