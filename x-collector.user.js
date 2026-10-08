// ==UserScript==
// @name         万能媒体下载器 - 本地版
// @namespace    http://127.0.0.1:8000/
// @version      4.5
// @description  采集 Likes/Bookmarks，上传本地服务（手动控制：开始/停止/上传）
// @author       浮生若夢
// @match        https://x.com/*
// @match        https://twitter.com/*
// @run-at       document-end
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @connect      localhost
// ==/UserScript==

(function () {

    'use strict';

    if (window.__XID_UNIVERSAL_MEDIA_COLLECTOR__) {
        return;
    }
    window.__XID_UNIVERSAL_MEDIA_COLLECTOR__ = true;


    /* =====================================================
     * 基础设置（本地版：上传到本机服务）
     * ===================================================== */

    const STORAGE_KEY = 'xid_universal_media_v080';
    const API_BASE = 'http://127.0.0.1:8000';
    const IMPORT_API = API_BASE + '/api/import-media';
    const MIN_SPEED = 0.5;
    const MAX_SPEED = 2.0;
    const SPEED_STEP = 0.25;
    const BASE_SCROLL_DELAY = 450;
    const BASE_SCROLL_RATIO = 0.9;
    const MAX_NO_GROWTH_LIKES = 8;
    const MAX_NO_GROWTH_BOOKMARKS = 16;


    /* =====================================================
     * 状态
     * ===================================================== */

    let speedMultiplier = 1.0;
    let records = {};
    let panel = null;
    let controls = null;
    let running = false;


    /* =====================================================
     * 网络拦截：X 改版后真实视频地址不在 DOM，改为 hook 请求
     * 按 amplify_video_id 关联 poster 与真实 m3u8/mp4
     * ===================================================== */
    const capturedVideoUrls = {};

    function captureVideoUrl(url) {
        try {
            if (!url) return;
            const m = String(url).match(/video\.twimg\.com\/amplify_video\/(\d+)\//);
            if (!m) return;
            const aid = m[1];
            if (!capturedVideoUrls[aid]) capturedVideoUrls[aid] = {};
            const u = String(url);

            // 1) 主 m3u8：/pl/{hash}.m3u8?tag=xx —— 不含 avc1/mp4a 子目录，ffmpeg 能合成完整带声音视频
            //    子列表 /pl/avc1/... /pl/mp4a/... 单独转不出来，跳过，不要覆盖主列表
            if (u.indexOf('.m3u8') !== -1 && u.indexOf('/pl/') !== -1
                && u.indexOf('/avc1/') === -1 && u.indexOf('/mp4a/') === -1) {
                if (!capturedVideoUrls[aid].m3u8) {
                    capturedVideoUrls[aid].m3u8 = u;  // 保留完整 query（?tag=xx）
                }
            }

            // 2) 完整视频 mp4：/vid/avc1/0/0/{WxH}/{hash}.mp4（纯视频流，没声音，作为备选）
            //    排除 .m4s 分片、排除 /aud/ 纯音频
            if (u.indexOf('/vid/') !== -1 && u.indexOf('.m4s') === -1 && u.indexOf('.mp4') !== -1) {
                if (!capturedVideoUrls[aid].mp4Variants) capturedVideoUrls[aid].mp4Variants = [];
                if (capturedVideoUrls[aid].mp4Variants.indexOf(u) === -1) {
                    capturedVideoUrls[aid].mp4Variants.push(u);
                }
            }
        } catch (e) {}
    }

    // 从多个 mp4 变体里选码率最高的一个
    function pickBestMp4(variants) {
        if (!variants || !variants.length) return '';
        let best = variants[0];
        let bestScore = -1;
        variants.forEach(function (u) {
            // URL 里 /vid/avc1/900... 这种数字近似码率，越大越清晰
            const m = u.match(/\/vid\/[^/]+\/(\d+)/);
            const score = m ? parseInt(m[1], 10) : 0;
            if (score > bestScore) { bestScore = score; best = u; }
        });
        return best;
    }

    function hookNetwork() {
        if (window.__xidHooked) return;
        window.__xidHooked = true;
        const origFetch = window.fetch;
        window.fetch = function () {
            try {
                const u = arguments[0];
                captureVideoUrl(typeof u === 'string' ? u : (u && u.url) || '');
            } catch (e) {}
            return origFetch.apply(this, arguments);
        };
        const origOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function (method, url) {
            try { captureVideoUrl(url); } catch (e) {}
            return origOpen.apply(this, arguments);
        };
    }
    let uploading = false;
    let scrollTimer = null;
    let lastHeight = 0;
    let noGrowthCount = 0;
    let speedStartTime = 0;
    let lastSpeedTime = 0;
    let startMediaCount = 0;
    let lastMediaCount = 0;
    let currentSpeed = 0;
    let averageSpeed = 0;


    /* =====================================================
     * 页面模式（支持：/likes、/i/history/likes、/bookmarks、/i/history）
     * ===================================================== */

    function getPageMode() {
        const path = location.pathname;
        // 喜欢：/likes、/i/history/likes
        if (path.endsWith('/likes') || path.includes('/likes/')) return 'likes';
        // 书签：/bookmarks、/i/history（X 新版书签路径）
        if (path.endsWith('/bookmarks') || path.includes('/bookmarks/') ||
            path.endsWith('/history') || path.includes('/history/')) return 'bookmarks';
        return null;
    }

    function isSupportedPage() {
        return !!getPageMode();
    }


    /* =====================================================
     * LocalStorage
     * ===================================================== */

    function loadRecords() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (!saved) { records = {}; return; }
            const parsed = JSON.parse(saved);
            records = parsed && typeof parsed === 'object' ? parsed : {};
        } catch (error) {
            console.log('[XID] load error', error);
            records = {};
        }
    }

    function saveRecords() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
        } catch (error) {
            console.log('[XID] save error', error);
        }
    }


    /* =====================================================
     * Tweet
     * ===================================================== */

    function getTweetArticles() {
        return Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
    }

    function getTweetUrl(article) {
        const links = article.querySelectorAll('a[href*="/status/"]');
        for (const link of links) {
            const href = link.href || '';
            if (/\/status\/\d+/.test(href)) return href.split('?')[0];
        }
        return '';
    }

    function getTweetId(url) {
        const match = url.match(/\/status\/(\d+)/);
        return match ? match[1] : '';
    }

    function getAuthor(article) {
        const links = article.querySelectorAll('a[href^="/"]');
        for (const link of links) {
            const href = link.getAttribute('href') || '';
            if (/^\/[^/]+$/.test(href) && !['/home', '/explore', '/notifications', '/messages', '/bookmarks', '/settings'].includes(href)) {
                return href.substring(1);
            }
        }
        return '';
    }

    function getImageMedia(article) {
        const images = [];
        const containers = article.querySelectorAll('[data-testid="tweetPhoto"]');
        containers.forEach(function (container) {
            const imgs = container.querySelectorAll('img');
            imgs.forEach(function (img) {
                const src = img.currentSrc || img.src || '';
                if (!src || !src.includes('pbs.twimg.com')) return;
                const clean = src.split('?')[0];
                if (clean.includes('profile_images') || clean.includes('profile_banners') ||
                    clean.includes('avatar') || clean.includes('emoji') ||
                    clean.includes('ext_tw_video_thumb') || clean.includes('amplify_video_thumb')) return;
                if (images.some(function (item) { return item.url === clean; })) return;
                images.push({
                    type: 'image',
                    url: clean,
                    originalUrl: clean + '?format=jpg&name=orig',
                    thumbnail: clean
                });
            });
        });
        return images;
    }

    function getVideoElements(article) {
        return Array.from(article.querySelectorAll('video'));
    }

    function getVideoElementUrls(article) {
        const result = [];
        getVideoElements(article).forEach(function (video) {
            const urls = [];
            if (video.src) urls.push(video.src);
            const source = video.querySelector('source');
            if (source && source.src) urls.push(source.src);
            urls.forEach(function (url) {
                if (url && url.includes('video.twimg.com') && !result.includes(url)) {
                    result.push(url);
                }
            });
        });
        return result;
    }

    function isMp4(url) {
        return !!url && (url.includes('.mp4') || url.includes('video/mp4'));
    }

    function isM3u8(url) {
        return !!url && (url.includes('.m3u8') || url.includes('mpegURL'));
    }

    function parseResolution(url) {
        const match = url ? url.match(/\/(\d{2,5})x(\d{2,5})\//) : null;
        if (!match) return { width: 0, height: 0 };
        return { width: Number(match[1]), height: Number(match[2]) };
    }

    function chooseBestVideo(urls) {
        if (!urls.length) return null;
        const mp4s = urls.filter(isMp4);
        if (mp4s.length) {
            const variants = mp4s.map(function (url) {
                const resolution = parseResolution(url);
                return { url: url, width: resolution.width, height: resolution.height, pixels: resolution.width * resolution.height };
            });
            variants.sort(function (a, b) { return b.pixels - a.pixels; });
            const best = variants[0];
            return { type: 'video', url: best.url, streamType: 'mp4', width: best.width, height: best.height, bitrate: 0 };
        }
        const m3u8 = urls.find(isM3u8);
        if (!m3u8) return null;
        return { type: 'video', url: m3u8, streamType: 'hls', width: 0, height: 0, bitrate: 0 };
    }

    function findVideoPoster(article) {
        const videos = article.querySelectorAll('video');
        for (const video of videos) {
            if (video.poster) return video.poster;
        }
        const thumbs = article.querySelectorAll('img[src*="ext_tw_video_thumb"], img[src*="amplify_video_thumb"]');
        for (const img of thumbs) {
            const src = img.currentSrc || img.src || '';
            if (src) return src;
        }
        return '';
    }

    function hasVideoIndicator(article) {
        if (article.querySelector('video')) return true;
        if (article.querySelector('[data-testid="videoPlayer"]')) return true;
        const html = article.innerHTML || '';
        return html.includes('video.twimg.com') || html.includes('ext_tw_video_thumb') || html.includes('amplify_video_thumb');
    }

    function getVideoMedia(article) {
        const result = [];
        const urls = getVideoElementUrls(article);
        const best = chooseBestVideo(urls);
        if (best) {
            best.thumbnail = findVideoPoster(article);
            result.push(best);
            return result;
        }
        // X 改版后 DOM 里没有真实地址，从封面提取 amplify_id 查网络拦截池
        const poster = findVideoPoster(article);
        const pm = poster.match(/amplify_video_thumb\/(\d+)\//);
        if (pm) {
            const cap = capturedVideoUrls[pm[1]];
            if (cap) {
                // 优先主 m3u8（ffmpeg 合成完整带声音视频）
                if (cap.m3u8) {
                    result.push({ type: 'video', url: cap.m3u8, streamType: 'hls', width: 0, height: 0, bitrate: 0, thumbnail: poster });
                    return result;
                }
                // 备选：完整 mp4（纯视频，可能没声音）
                const bestMp4 = pickBestMp4(cap.mp4Variants);
                if (bestMp4) {
                    result.push({ type: 'video', url: bestMp4, streamType: 'mp4', width: 0, height: 0, bitrate: 0, thumbnail: poster });
                    return result;
                }
            }
        }
        if (hasVideoIndicator(article)) {
            result.push({
                type: 'video',
                url: '',
                streamType: 'pending',
                width: 0,
                height: 0,
                bitrate: 0,
                thumbnail: poster
            });
        }
        return result;
    }

    function getTweetMedia(article) {
        return [...getImageMedia(article), ...getVideoMedia(article)];
    }

    function mergeMedia(oldMedia, newMedia) {
        const result = Array.isArray(oldMedia) ? [...oldMedia] : [];
        for (const item of newMedia) {
            if (item.type === 'video' && item.url) {
                const pendingIndex = result.findIndex(function (old) {
                    return old.type === 'video' && !old.url;
                });
                if (pendingIndex >= 0) {
                    result[pendingIndex] = item;
                    continue;
                }
            }
            if (item.url) {
                const exists = result.some(function (old) {
                    return old.url === item.url;
                });
                if (exists) continue;
            }
            if (item.type === 'video' && !item.url) {
                const pendingExists = result.some(function (old) {
                    return old.type === 'video' && !old.url;
                });
                if (pendingExists) continue;
            }
            result.push(item);
        }
        return result;
    }

    /* =====================================================
     * extractTweet 提取真实发布时间
     * ===================================================== */
    function extractTweet(article) {
        const url = getTweetUrl(article);
        if (!url) return null;
        const id = getTweetId(url);
        if (!id) return null;

        // 获取真实发布时间（从 <time> 元素提取）
        let createdAt = '';
        const timeEl = article.querySelector('time');
        if (timeEl) {
            // 优先使用 datetime 属性（ISO 格式）
            createdAt = timeEl.getAttribute('datetime') || timeEl.textContent.trim() || '';
        }

        return {
            id: id,
            url: url,
            author: getAuthor(article),
            media: getTweetMedia(article),
            createdAt: createdAt,
            updatedAt: Date.now()
        };
    }

    /* =====================================================
     * 自动唤醒 pending 视频（静音触发，让 X 加载真实流地址）
     * ===================================================== */
    function collect() {
        const mode = getPageMode();
        if (!mode) return;
        const articles = getTweetArticles();
        let changed = false;
        for (const article of articles) {
            const tweet = extractTweet(article);
            if (!tweet) continue;
            tweet.source = mode;
            const old = records[tweet.id];
            if (!old) {
                records[tweet.id] = tweet;
                changed = true;
                continue;
            }
            if (old.source !== mode) {
                old.source = mode;
                changed = true;
            }
            const oldMedia = Array.isArray(old.media) ? old.media : [];
            const merged = mergeMedia(oldMedia, tweet.media);
            if (merged.length !== oldMedia.length) {
                old.media = merged;
                old.updatedAt = Date.now();
                if (!old.createdAt && tweet.createdAt) {
                    old.createdAt = tweet.createdAt;
                }
                changed = true;
            }
        }
        if (changed) saveRecords();
        updateSpeed();
        updatePanel();
    }


    /* =====================================================
     * 统计与速度
     * ===================================================== */

    function getStats() {
        const tweets = Object.values(records);
        let images = 0, videos = 0, pendingVideos = 0, totalMedia = 0;
        tweets.forEach(function (tweet) {
            const media = Array.isArray(tweet.media) ? tweet.media : [];
            media.forEach(function (item) {
                totalMedia++;
                if (item.type === 'image') images++;
                if (item.type === 'video') {
                    if (item.url) videos++;
                    else pendingVideos++;
                }
            });
        });
        return { tweets: tweets.length, images: images, videos: videos, pendingVideos: pendingVideos, totalMedia: totalMedia };
    }

    function resetSpeedStats() {
        const stats = getStats();
        const now = Date.now();
        startMediaCount = stats.totalMedia;
        lastMediaCount = stats.totalMedia;
        speedStartTime = now;
        lastSpeedTime = now;
        currentSpeed = 0;
        averageSpeed = 0;
    }

    function updateSpeed() {
        const stats = getStats();
        const now = Date.now();
        const deltaTime = (now - lastSpeedTime) / 1000;
        if (deltaTime >= 0.5) {
            const deltaMedia = stats.totalMedia - lastMediaCount;
            currentSpeed = deltaMedia / deltaTime;
            lastMediaCount = stats.totalMedia;
            lastSpeedTime = now;
        }
        const totalTime = (now - speedStartTime) / 1000;
        if (totalTime > 1) {
            averageSpeed = (stats.totalMedia - startMediaCount) / totalTime;
        }
    }


    /* =====================================================
     * 速度控制
     * ===================================================== */

    function changeSpeed(amount) {
        speedMultiplier = Math.round((speedMultiplier + amount) * 100) / 100;
        speedMultiplier = Math.max(MIN_SPEED, Math.min(MAX_SPEED, speedMultiplier));
        updateSpeedButton();
        updatePanel();
    }

    function getScrollDelay() {
        return Math.max(120, Math.round(BASE_SCROLL_DELAY / speedMultiplier));
    }

    function getScrollDistance() {
        return Math.floor(window.innerHeight * Math.min(1.15, BASE_SCROLL_RATIO * speedMultiplier));
    }


    /* =====================================================
     * 上传数据（含 tweetCreatedAt）
     * ===================================================== */

    function getUploadItems() {
        return Object.values(records)
            .filter(function (tweet) {
                return tweet && Array.isArray(tweet.media) &&
                    tweet.media.some(function (media) { return media && media.type && media.url; });
            })
            .map(function (tweet) {
                return {
                    tweetId: tweet.id || '',
                    tweetUrl: tweet.url || '',
                    author: tweet.author || '',
                    source: tweet.source || 'likes',
                    tweetCreatedAt: tweet.createdAt || '',
                    media: (function () {
                        let list = tweet.media.filter(function (media) {
                            if (!media || (media.type !== 'image' && media.type !== 'video') || !media.url) return false;
                            // 兜底：图片类型中凡是视频封面图（amplify/ext_tw_video_thumb）一律不上传
                            if (media.type === 'image' &&
                                (media.url.indexOf('amplify_video_thumb') !== -1 ||
                                 media.url.indexOf('ext_tw_video_thumb') !== -1)) return false;
                            return true;
                        });
                        // 视频去重：同一条视频同时抓到 MP4 和 HLS 时，只保留 MP4（直链更好用）
                        const hasMp4 = list.some(function (m) {
                            return m.type === 'video' &&
                                (m.url.indexOf('.mp4') !== -1 || m.url.indexOf('video/mp4') !== -1);
                        });
                        if (hasMp4) {
                            list = list.filter(function (m) {
                                if (m.type !== 'video') return true;
                                return m.url.indexOf('.m3u8') === -1 && m.url.indexOf('mpegURL') === -1;
                            });
                        }
                        return list;
                    })()
                };
            });
    }


    /* =====================================================
     * 上传（GM_xmlhttpRequest）
     * ===================================================== */

    function gmUpload(payload) {
        return new Promise(function (resolve, reject) {
            if (typeof GM_xmlhttpRequest !== 'function') {
                alert('GM_xmlhttpRequest 不可用，请使用 Tampermonkey 或 Kiwi Browser。');
                reject(new Error('GM_xmlhttpRequest 不可用'));
                return;
            }
            GM_xmlhttpRequest({
                method: 'POST',
                url: IMPORT_API,
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                data: JSON.stringify(payload),
                timeout: 60000,
                onload: function (response) {
                    let data = null;
                    try {
                        data = JSON.parse(response.responseText);
                    } catch (e) {
                        reject(new Error('服务器返回的不是有效 JSON。HTTP ' + response.status));
                        return;
                    }
                    if (response.status < 200 || response.status >= 300) {
                        reject(new Error(data && data.detail ? data.detail : 'HTTP ' + response.status));
                        return;
                    }
                    if (!data || data.ok !== true) {
                        reject(new Error(data && data.detail ? data.detail : '服务器返回异常'));
                        return;
                    }
                    resolve(data);
                },
                onerror: function () {
                    reject(new Error('网络错误，请检查网络或服务器状态。'));
                },
                ontimeout: function () {
                    reject(new Error('请求超时，请检查网络或稍后重试。'));
                },
                onabort: function () {
                    reject(new Error('上传请求被取消。'));
                }
            });
        });
    }

    async function uploadRecords() {
        if (uploading) return;
        const items = getUploadItems();
        if (!items.length) {
            alert('目前没有可以上传的媒体。');
            return;
        }
        const stats = getStats();
        const ok = confirm(
            '确定上传当前采集到的媒体吗？\n\n' +
            '帖子：' + stats.tweets + '\n' +
            '图片：' + stats.images + '\n' +
            '视频：' + stats.videos + '\n\n' +
            '服务器会自动去重。'
        );
        if (!ok) return;

        uploading = true;
        updateUploadButton();
        updatePanel();

        try {
            const payload = { items: items };
            const data = await gmUpload(payload);
            alert(
                '✅ 上传完成！\n\n' +
                '本次提交：' + (data.imported || 0) + '\n' +
                '新增：' + (data.added || 0) + '\n' +
                '重复：' + (data.duplicates || 0) + '\n' +
                '更新：' + (data.updated || 0) + '\n\n' +
                '服务器媒体总数：' + (data.total || 0)
            );
        } catch (error) {
            console.error('[XID] upload error:', error);
            alert('❌ 上传失败\n\n原因：' + (error.message || error));
        } finally {
            uploading = false;
            updateUploadButton();
            updatePanel();
        }
    }


    /* =====================================================
     * 面板
     * ===================================================== */

    function createPanel() {
        if (!document.body) return null;
        if (panel) return panel;
        panel = document.createElement('div');
        panel.id = 'xid-universal-panel';
        Object.assign(panel.style, {
            position: 'fixed',
            left: '10px',
            right: '10px',
            bottom: '15px',
            zIndex: '2147483647',
            background: 'rgba(0,0,0,.94)',
            color: '#fff',
            padding: '14px',
            borderRadius: '15px',
            font: '14px -apple-system,BlinkMacSystemFont,sans-serif',
            lineHeight: '1.6',
            boxShadow: '0 4px 20px rgba(0,0,0,.4)'
        });
        document.body.appendChild(panel);
        return panel;
    }

    function updatePanel() {
        const box = createPanel();
        if (!box) return;
        const stats = getStats();
        const mode = getPageMode();
        const modeName = mode === 'likes' ? '❤️ Likes' : mode === 'bookmarks' ? '🔖 Bookmarks' : 'X';
        const status = running ? '🟢 采集中' : '⚪ 已停止';
        const uploadStatus = uploading ? '⏫ 上传中...' : '';
        box.innerHTML =
            '<b>🖼️ 万能媒体下载器</b><br>' +
            '🎯 ' + API_BASE +
            '<br><br>' +
            modeName + '<br><br>' +
            status + '<br>' +
            uploadStatus + (uploadStatus ? '<br>' : '') +
            '速度：' + speedMultiplier.toFixed(2) + '×<br>' +
            '帖子：' + stats.tweets + '<br>' +
            '🖼 图片：' + stats.images + '<br>' +
            '🎬 视频：' + stats.videos + '<br>' +
            (stats.pendingVideos > 0 ? '⏳ 待解析视频：' + stats.pendingVideos + '<br>' : '') +
            '媒体总数：' + stats.totalMedia + '<br>' +
            '当前速度：' + currentSpeed.toFixed(1) + ' 媒体/秒<br>' +
            '平均速度：' + averageSpeed.toFixed(1) + ' 媒体/秒<br><br>' +
            '<small>无增长容忍：' + (mode === 'bookmarks' ? MAX_NO_GROWTH_BOOKMARKS : MAX_NO_GROWTH_LIKES) + ' 次</small>';
    }


    /* =====================================================
     * 控制按钮
     * ===================================================== */

    function createControls() {
        if (!document.body) return;
        if (document.getElementById('xid-universal-controls')) return;
        controls = document.createElement('div');
        controls.id = 'xid-universal-controls';
        Object.assign(controls.style, {
            position: 'fixed',
            right: '12px',
            bottom: '125px',
            zIndex: '2147483647',
            display: 'flex',
            gap: '7px',
            flexWrap: 'wrap',
            justifyContent: 'flex-end'
        });

        function styleButton(button) {
            Object.assign(button.style, {
                border: 'none',
                borderRadius: '999px',
                padding: '7px 11px',
                background: 'rgba(0,0,0,.9)',
                color: '#fff',
                fontSize: '13px',
                fontWeight: '600',
                boxShadow: '0 3px 12px rgba(0,0,0,.3)',
                cursor: 'pointer'
            });
        }

        const minus = document.createElement('button');
        minus.textContent = '−';
        styleButton(minus);
        minus.style.fontSize = '20px';
        minus.onclick = function () { changeSpeed(-SPEED_STEP); };

        const speed = document.createElement('button');
        speed.id = 'xid-speed-display';
        styleButton(speed);
        speed.style.minWidth = '58px';
        speed.onclick = function () { speedMultiplier = 1.0;
            updateSpeedButton();
            updatePanel(); };

        const plus = document.createElement('button');
        plus.textContent = '+';
        styleButton(plus);
        plus.style.fontSize = '20px';
        plus.onclick = function () { changeSpeed(SPEED_STEP); };

        const start = document.createElement('button');
        start.textContent = '▶';
        styleButton(start);
        start.onclick = function () { startCollector(); };

        const stop = document.createElement('button');
        stop.textContent = '⏸';
        styleButton(stop);
        stop.onclick = function () { stopCollector(); };

        const upload = document.createElement('button');
        upload.id = 'xid-upload-button';
        upload.textContent = '⬆ 上传';
        styleButton(upload);
        upload.style.background = 'rgba(0,120,255,.9)';
        upload.onclick = function () { uploadRecords(); };

        const clear = document.createElement('button');
        clear.textContent = '🗑';
        styleButton(clear);
        clear.onclick = function () {
            if (!confirm('确定清空本地所有采集数据吗？')) return;
            stopCollector();
            records = {};
            saveRecords();
            resetSpeedStats();
            updatePanel();
        };

        controls.appendChild(minus);
        controls.appendChild(speed);
        controls.appendChild(plus);
        controls.appendChild(start);
        controls.appendChild(stop);
        controls.appendChild(upload);
        controls.appendChild(clear);
        document.body.appendChild(controls);
        updateSpeedButton();
        updateUploadButton();
    }

    function updateSpeedButton() {
        const button = document.getElementById('xid-speed-display');
        if (!button) return;
        button.textContent = speedMultiplier.toFixed(2) + '×';
    }

    function updateUploadButton() {
        const button = document.getElementById('xid-upload-button');
        if (!button) return;
        button.textContent = uploading ? '⏫ 上传中' : '⬆ 上传';
        button.disabled = uploading;
        button.style.opacity = uploading ? '0.6' : '1';
    }


    /* =====================================================
     * 开始/停止
     * ===================================================== */

    function startCollector() {
        if (running) return;
        if (!isSupportedPage()) {
            alert('请先打开 X 的 Likes 或 Bookmarks 页面。');
            return;
        }
        running = true;
        noGrowthCount = 0;
        lastHeight = document.documentElement.scrollHeight;
        resetSpeedStats();
        collect();
        updatePanel();
        fastLoop();
    }

    function stopCollector() {
        running = false;
        if (scrollTimer) {
            clearTimeout(scrollTimer);
            scrollTimer = null;
        }
        updatePanel();
    }

    function fastLoop() {
        if (!running) return;
        if (!isSupportedPage()) {
            stopCollector();
            return;
        }
        collect();
        window.scrollBy({ top: getScrollDistance(), left: 0, behavior: 'auto' });
        scrollTimer = setTimeout(function () {
            if (!running) return;
            collect();
            checkPageGrowth();
            fastLoop();
        }, getScrollDelay());
    }

    function checkPageGrowth() {
        const height = document.documentElement.scrollHeight;
        const mode = getPageMode();
        const maxNoGrowth = mode === 'bookmarks' ? MAX_NO_GROWTH_BOOKMARKS : MAX_NO_GROWTH_LIKES;
        if (height <= lastHeight + 50) {
            noGrowthCount++;
        } else {
            noGrowthCount = 0;
            lastHeight = height;
        }
        if (noGrowthCount >= maxNoGrowth) {
            stopCollector();
            const name = mode === 'likes' ? 'Likes' : 'Bookmarks';
            alert(name + ' 采集完成。');
        }
    }


    /* =====================================================
     * 初始化
     * ===================================================== */

    function start() {
        hookNetwork();
        loadRecords();
        setTimeout(function () {
            createPanel();
            createControls();
            collect();
            updatePanel();
        }, 2500);
    }

    start();

})();
