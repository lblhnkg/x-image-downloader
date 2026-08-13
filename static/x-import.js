(() => {
    "use strict";

    /*
     * =========================================================
     * X Media Finder
     * X Import Assistant
     *
     * 作用：
     *
     * 1. 读取 V0.8 Userscript 保存的 LocalStorage
     * 2. 显示上传按钮
     * 3. 将 Likes / Bookmarks 数据上传到 Render
     * 4. 使用 /api/import-media
     *
     * 注意：
     * 本文件不再读取 X GraphQL。
     * 本文件不再 Hook fetch / XHR。
     * 本文件不读取 Cookie、auth_token 或密码。
     * =========================================================
     */

    const VERSION = "0.8";

    /*
     * =========================================================
     * 配置
     * =========================================================
     */

    const API_BASE =
        "https://x-v1.onrender.com";

    /*
     * 当前 V0.8 采集器使用的 LocalStorage。
     *
     * 你的采集器虽然版本已经是 0.8，
     * 但目前正常工作的代码仍然使用这个键。
     *
     * 不改它，保证能够直接读取你现在已经采集的数据。
     */

    const STORAGE_KEY =
        "xid_universal_media_v060";


    /*
     * =========================================================
     * 基础状态
     * =========================================================
     */

    let uploading = false;

    let messageBox = null;

    let uploadButton = null;


    /*
     * =========================================================
     * 日志
     * =========================================================
     */

    function log(...args) {

        console.log(
            "[X Media Finder]",
            ...args
        );

    }


    /*
     * =========================================================
     * 当前页面模式
     * =========================================================
     */

    function getPageMode() {

        const path =
            location.pathname;

        if (
            path.includes("/bookmarks")
        ) {

            return "bookmarks";

        }

        if (
            path.includes("/likes")
        ) {

            return "likes";

        }

        return null;

    }


    /*
     * =========================================================
     * 消息提示
     * =========================================================
     */

    function showMessage(
        message,
        type = "info"
    ) {

        if (!document.body) {
            return;
        }

        if (!messageBox) {

            messageBox =
                document.createElement(
                    "div"
                );

            messageBox.id =
                "xid-import-message";

            Object.assign(
                messageBox.style,
                {

                    position:
                        "fixed",

                    left:
                        "12px",

                    right:
                        "12px",

                    bottom:
                        "20px",

                    zIndex:
                        "2147483647",

                    padding:
                        "14px 16px",

                    borderRadius:
                        "14px",

                    color:
                        "#fff",

                    fontSize:
                        "14px",

                    lineHeight:
                        "1.5",

                    fontFamily:
                        "-apple-system,BlinkMacSystemFont,sans-serif",

                    boxShadow:
                        "0 5px 30px rgba(0,0,0,.35)"

                }
            );

            document.body.appendChild(
                messageBox
            );

        }

        messageBox.textContent =
            message;

        if (
            type === "error"
        ) {

            messageBox.style.background =
                "rgba(180,30,30,.96)";

        } else if (
            type === "success"
        ) {

            messageBox.style.background =
                "rgba(20,120,70,.96)";

        } else {

            messageBox.style.background =
                "rgba(20,20,20,.94)";

        }

    }


    /*
     * =========================================================
     * 读取 LocalStorage
     * =========================================================
     */

    function loadRecords() {

        let raw = null;

        try {

            raw =
                localStorage.getItem(
                    STORAGE_KEY
                );

        } catch (error) {

            throw new Error(
                "无法读取浏览器 LocalStorage"
            );

        }

        if (!raw) {

            return {};

        }

        try {

            const parsed =
                JSON.parse(raw);

            if (
                !parsed ||
                typeof parsed !== "object" ||
                Array.isArray(parsed)
            ) {

                throw new Error(
                    "LocalStorage 数据格式错误"
                );

            }

            return parsed;

        } catch (error) {

            throw new Error(
                "LocalStorage 中的采集数据无法解析"
            );

        }

    }


    /*
     * =========================================================
     * 统计本地数据
     * =========================================================
     */

    function getLocalStats(
        records
    ) {

        const tweets =
            Object.values(
                records
            );

        let imageCount = 0;

        let videoCount = 0;

        let pendingVideoCount = 0;

        let mediaCount = 0;

        tweets.forEach(
            function (tweet) {

                const media =
                    Array.isArray(
                        tweet.media
                    )
                        ? tweet.media
                        : [];

                media.forEach(
                    function (item) {

                        mediaCount++;

                        if (
                            item.type ===
                            "image"
                        ) {

                            imageCount++;

                        }

                        if (
                            item.type ===
                            "video"
                        ) {

                            if (
                                item.url
                            ) {

                                videoCount++;

                            } else {

                                pendingVideoCount++;

                            }

                        }

                    }
                );

            }
        );

        return {

            tweets:
                tweets.length,

            images:
                imageCount,

            videos:
                videoCount,

            pendingVideos:
                pendingVideoCount,

            media:
                mediaCount

        };

    }


    /*
     * =========================================================
     * 清理上传数据
     *
     * 只保留后端需要的数据。
     * =========================================================
     */

    function buildItems(
        records
    ) {

        const result = [];

        Object.values(
            records
        ).forEach(
            function (tweet) {

                if (
                    !tweet ||
                    typeof tweet !== "object"
                ) {

                    return;

                }

                const tweetId =
                    String(
                        tweet.id ||
                        tweet.tweetId ||
                        ""
                    );

                const tweetUrl =
                    tweet.url ||
                    tweet.tweetUrl ||
                    "";

                const author =
                    tweet.author ||
                    "";

                const source =
                    tweet.source ===
                    "bookmarks"
                        ? "bookmarks"
                        : "likes";

                const rawMedia =
                    Array.isArray(
                        tweet.media
                    )
                        ? tweet.media
                        : [];

                const media = [];

                rawMedia.forEach(
                    function (item) {

                        if (
                            !item ||
                            typeof item !==
                            "object"
                        ) {

                            return;

                        }

                        const type =
                            item.type;

                        if (
                            type !==
                                "image" &&
                            type !==
                                "video"
                        ) {

                            return;

                        }

                        /*
                         * Pending 视频没有真实 URL。
                         *
                         * 后端目前的媒体库设计要求媒体
                         * 有实际 URL，所以这里不上传
                         * pending 视频。
                         *
                         * 等采集器以后拿到真实 URL，
                         * 再上传即可。
                         */

                        if (
                            !item.url
                        ) {

                            return;

                        }

                        media.push({

                            type:
                                type,

                            url:
                                item.url,

                            originalUrl:
                                item.originalUrl ||
                                item.url,

                            thumbnail:
                                item.thumbnail ||
                                "",

                            streamType:
                                item.streamType ||
                                "",

                            width:
                                Number(
                                    item.width
                                ) || 0,

                            height:
                                Number(
                                    item.height
                                ) || 0,

                            bitrate:
                                Number(
                                    item.bitrate
                                ) || 0

                        });

                    }
                );

                /*
                 * 没有可上传媒体，
                 * 不发送这个 Tweet。
                 */

                if (
                    media.length === 0
                ) {

                    return;

                }

                result.push({

                    tweetId:
                        tweetId,

                    tweetUrl:
                        tweetUrl,

                    author:
                        author,

                    source:
                        source,

                    media:
                        media

                });

            }
        );

        return result;

    }


    /*
     * =========================================================
     * 上传
     * =========================================================
     */

    async function uploadToServer() {

        if (uploading) {

            return;

        }

        uploading = true;

        if (uploadButton) {

            uploadButton.disabled =
                true;

            uploadButton.textContent =
                "上传中…";

            uploadButton.style.opacity =
                "0.6";

        }

        try {

            /*
             * 读取本地数据
             */

            showMessage(
                "正在读取本地采集数据……"
            );

            const records =
                loadRecords();

            const stats =
                getLocalStats(
                    records
                );

            if (
                stats.tweets === 0
            ) {

                throw new Error(
                    "本地还没有采集到任何帖子"
                );

            }

            /*
             * 转换成后端格式
             */

            const items =
                buildItems(
                    records
                );

            if (
                items.length === 0
            ) {

                throw new Error(
                    "没有可上传的媒体。可能目前只有待解析视频。"
                );

            }

            let uploadMediaCount = 0;

            items.forEach(
                function (item) {

                    uploadMediaCount +=
                        item.media.length;

                }
            );

            showMessage(
                "正在上传 " +
                items.length +
                " 个帖子 / " +
                uploadMediaCount +
                " 个媒体……"
            );

            /*
             * =================================================
             * 核心：
             *
             * 直接调用真正存在的：
             *
             * POST /api/import-media
             * =================================================
             */

            const response =
                await fetch(
                    API_BASE +
                    "/api/import-media",
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

            /*
             * 尝试读取服务器返回内容。
             */

            let data = null;

            try {

                data =
                    await response.json();

            } catch (_) {

                data = null;

            }

            /*
             * HTTP 错误
             */

            if (
                !response.ok
            ) {

                let detail =
                    "服务器返回 HTTP " +
                    response.status;

                if (
                    data &&
                    data.detail
                ) {

                    detail +=
                        "：" +
                        data.detail;

                }

                throw new Error(
                    detail
                );

            }

            /*
             * 后端正常返回，
             * 但 ok 不正确。
             */

            if (
                !data ||
                data.ok !== true
            ) {

                throw new Error(
                    "服务器返回的数据格式异常"
                );

            }

            /*
             * 成功
             */

            const added =
                Number(
                    data.added
                ) || 0;

            const duplicates =
                Number(
                    data.duplicates
                ) || 0;

            const updated =
                Number(
                    data.updated
                ) || 0;

            const imported =
                Number(
                    data.imported
                ) || 0;

            showMessage(

                "上传完成！\n" +

                "本次提交：" +
                imported +
                " 个媒体\n" +

                "新增：" +
                added +
                "\n" +

                "重复：" +
                duplicates +
                "\n" +

                "更新：" +
                updated +
                "\n" +

                "媒体库总数：" +
                (
                    Number(
                        data.total
                    ) || 0
                ),

                "success"

            );

            log(
                "上传成功",
                data
            );

        } catch (error) {

            console.error(
                "[X Media Finder] 上传失败：",
                error
            );

            showMessage(

                "上传失败：\n" +
                (
                    error &&
                    error.message
                        ? error.message
                        : String(error)
                ),

                "error"

            );

        } finally {

            uploading =
                false;

            if (uploadButton) {

                uploadButton.disabled =
                    false;

                uploadButton.textContent =
                    "☁ 上传到媒体库";

                uploadButton.style.opacity =
                    "1";

            }

        }

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

        uploadButton =
            document.createElement(
                "button"
            );

        uploadButton.id =
            "xid-import-button";

        uploadButton.textContent =
            "☁ 上传到媒体库";

        Object.assign(
            uploadButton.style,
            {

                position:
                    "fixed",

                right:
                    "14px",

                bottom:
                    "95px",

                zIndex:
                    "2147483647",

                border:
                    "0",

                borderRadius:
                    "999px",

                padding:
                    "12px 16px",

                background:
                    "#111",

                color:
                    "#fff",

                fontSize:
                    "14px",

                fontWeight:
                    "600",

                boxShadow:
                    "0 4px 18px rgba(0,0,0,.3)",

                cursor:
                    "pointer"

            }
        );

        uploadButton.addEventListener(
            "click",
            uploadToServer
        );

        document.body.appendChild(
            uploadButton
        );

    }


    /*
     * =========================================================
     * 页面状态提示
     * =========================================================
     */

    function showLocalStatus() {

        try {

            const records =
                loadRecords();

            const stats =
                getLocalStats(
                    records
                );

            const mode =
                getPageMode();

            const modeName =
                mode === "likes"
                    ? "❤️ Likes"
                    : mode === "bookmarks"
                        ? "🔖 Bookmarks"
                        : "X";

            showMessage(

                "X Media Finder 已连接\n" +

                modeName +
                "\n" +

                "本地帖子：" +
                stats.tweets +
                "\n" +

                "图片：" +
                stats.images +
                "\n" +

                "视频：" +
                stats.videos +
                (
                    stats.pendingVideos
                        ? "\n待解析视频：" +
                          stats.pendingVideos
                        : ""
                ) +
                "\n" +

                "可上传媒体：" +
                stats.media,

                "info"

            );

        } catch (error) {

            showMessage(
                "无法读取采集数据：" +
                error.message,
                "error"
            );

        }

    }


    /*
     * =========================================================
     * 初始化
     * =========================================================
     */

    function start() {

        /*
         * 只在 X 页面运行。
         */

        if (
            location.hostname !==
                "x.com" &&
            location.hostname !==
                "www.x.com" &&
            location.hostname !==
                "twitter.com" &&
            location.hostname !==
                "www.twitter.com"
        ) {

            return;

        }

        /*
         * 页面可能还没有 body。
         */

        if (!document.body) {

            setTimeout(
                start,
                500
            );

            return;

        }

        createButton();

        showLocalStatus();

        log(
            "X Import Assistant v" +
            VERSION +
            " started"
        );

    }


    /*
     * =========================================================
     * 启动
     * =========================================================
     */

    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            start,
            {
                once: true
            }
        );

    } else {

        start();

    }

})();
