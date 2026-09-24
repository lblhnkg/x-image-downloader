/**
 * Nv-Pu-Sa (X-Archive) v2 - Client Application & React-Bits Motion Engine
 * Synthesized: Karpathy (Discrete Column Masonry) · UI-UX-Pro-Max (OLED/Light) · Impeccable (Native Badge & Frameless Modal) · React-Bits (Slot Machine Shuffle) · Better-Icons
 */

document.addEventListener('DOMContentLoaded', () => {

  // ==================== Sample Data for Instant Preview ====================
  const defaultSampleData = [
    {
      "id": "1280938963541221376",
      "screen_name": "afukadou7",
      "name": "阿芙卡豆",
      "avatar_url": "https://pbs.twimg.com/profile_images/2033912326085349377/WEkPM9t7_400x400.jpg",
      "cover_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80",
      "followers_count": 102939,
      "description": "阿芙卡豆 | 官方指路 💓 TG & Fansone 专属记录页，分享日常与数码生活。https://fansone.co/afuka",
      "verified": true,
      "category": "Design & Lifestyle",
      "backed_up_at": "2026-08-11T15:21:30.336Z"
    },
    {
      "id": "15354924",
      "screen_name": "sama",
      "name": "Sam Altman",
      "avatar_url": "https://pbs.twimg.com/profile_images/1605336338520281088/8p7c1m-b_400x400.jpg",
      "cover_url": "https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=800&auto=format&fit=crop&q=80",
      "followers_count": 3240000,
      "description": "CEO at OpenAI. Working on AGI to benefit all of humanity. https://openai.com",
      "verified": true,
      "category": "AI & Tech",
      "backed_up_at": "2026-08-11T16:00:00.000Z"
    },
    {
      "id": "33838201",
      "screen_name": "karpathy",
      "name": "Andrej Karpathy",
      "avatar_url": "https://pbs.twimg.com/profile_images/1799516629949603840/z0HquzC__400x400.jpg",
      "cover_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80",
      "followers_count": 1120000,
      "description": "Building Eureka Labs. Formerly OpenAI and Tesla AI lead. Passionate about LLMs, deep learning and education. https://eurekalabs.ai",
      "verified": true,
      "category": "AI Research",
      "backed_up_at": "2026-08-11T16:05:00.000Z"
    },
    {
      "id": "1157097323",
      "screen_name": "levelsio",
      "name": "Pieter Levels",
      "avatar_url": "https://pbs.twimg.com/profile_images/1783777553942007808/3Z__tM50_400x400.jpg",
      "cover_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80",
      "followers_count": 542000,
      "description": "Indie hacker. Building Nomad List, Remote OK, PhotoAI, and Interior AI. Shipping fast as a solo founder. https://levels.io",
      "verified": true,
      "category": "Indie Hacker",
      "backed_up_at": "2026-08-11T16:10:00.000Z"
    },
    {
      "id": "14499829",
      "screen_name": "ylecun",
      "name": "Yann LeCun",
      "avatar_url": "https://pbs.twimg.com/profile_images/1498642738902507523/wU2a74cE_400x400.jpg",
      "cover_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&auto=format&fit=crop&q=80",
      "followers_count": 890000,
      "description": "Chief AI Scientist at Meta. Professor at NYU. Turing Award Laureate for Deep Learning. https://yann.lecun.com",
      "verified": true,
      "category": "AI Research",
      "backed_up_at": "2026-08-11T16:15:00.000Z"
    },
    {
      "id": "96135824",
      "screen_name": "gregkamradt",
      "name": "Greg Kamradt",
      "avatar_url": "https://pbs.twimg.com/profile_images/1614761011884392451/7fHlO12T_400x400.jpg",
      "cover_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80",
      "followers_count": 185000,
      "description": "Building AI data tools & benchmarks. Needle in a Haystack evaluation creator. Exploring LLM capabilities.",
      "verified": false,
      "category": "AI & Data",
      "backed_up_at": "2026-08-11T16:20:00.000Z"
    }
  ];

  // SVG Icon Templates (Iconify / Lucide & Phosphor Standard)
  const ICONS = {
    verifiedNative: `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2"><polyline points="20 6 9 17 4 12"/></svg>`,
    users: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    external: `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>`,
    eye: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`,
    ghost: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 10h.01"/><path d="M15 10h.01"/><path d="M12 2a8 8 0 0 0-8 8v12l3-3 2.5 2.5L12 19l2.5 2.5L17 19l3 3V10a8 8 0 0 0-8-8z"/></svg>`,
    history: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>`,
    stamp: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>`,
    candle: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2c-.5 2.5-2 3.5-2 5a2 2 0 0 0 4 0c0-1.5-1.5-2.5-2-5z"/><path d="M8 11h8v10H8z"/></svg>`,
    markdown: `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="14" rx="2"/><polyline points="7 15 7 9 10 12 13 9 13 15"/><polyline points="18 12 16 14 16 10"/></svg>`,
    copy: `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect width="13" height="13" x="9" y="9" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>`,
    chevronDown: `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>`
  };

  // Canvas Color Extraction Engine for Dynamic Ambient Glow
  const sampleCanvas = document.createElement('canvas');
  sampleCanvas.width = 16;
  sampleCanvas.height = 16;
  const sampleCtx = sampleCanvas.getContext('2d', { willReadFrequently: true });

  // 12 Evenly Distributed Spectral Neon Accents for Creators
  const VIBRANT_ACCENTS = [
    '244, 63, 94',    // Rose Red (350°)
    '236, 72, 153',   // Neon Pink (330°)
    '217, 70, 239',   // Vivid Fuchsia (290°)
    '168, 85, 247',   // Electric Purple (270°)
    '129, 140, 248',  // Periwinkle Indigo (235°)
    '14, 165, 233',   // Sky Cyan (195°)
    '20, 184, 166',   // Mint Teal (175°)
    '16, 185, 129',   // Emerald Green (150°)
    '132, 204, 22',   // Lime Green (85°)
    '245, 158, 11',   // Amber Gold (40°)
    '249, 115, 22',   // Orange Flame (25°)
    '239, 68, 68'     // Ruby Crimson (0°)
  ];

  function rgbToHsl(r, g, b) {
    r /= 255; g /= 255; b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h = 0, s = 0, l = (max + min) / 2;
    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = (g - b) / d + (g < b ? 6 : 0); break;
        case g: h = (b - r) / d + 2; break;
        case b: h = (r - g) / d + 4; break;
      }
      h *= 60;
    }
    return [h, s, l];
  }

  function hslToRgb(h, s, l) {
    const hue2rgb = (p, q, t) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    const r = hue2rgb(p, q, h / 360 + 1/3);
    const g = hue2rgb(p, q, h / 360);
    const b = hue2rgb(p, q, h / 360 - 1/3);
    return `${Math.round(r * 255)}, ${Math.round(g * 255)}, ${Math.round(b * 255)}`;
  }

  function getFallbackAccent(key) {
    let hash = 0;
    const str = String(key || 'creator');
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return VIBRANT_ACCENTS[Math.abs(hash) % VIBRANT_ACCENTS.length];
  }

  // Chrominance-Peak HSL Dominant Color Extractor
  function extractDominantColor(img, defaultKey = 'creator') {
    try {
      sampleCtx.clearRect(0, 0, 16, 16);
      sampleCtx.drawImage(img, 0, 0, 16, 16);
      const imgData = sampleCtx.getImageData(0, 0, 16, 16).data;
      const buckets = new Array(12).fill(0);
      const hueSums = new Array(12).fill(0);
      let totalVibrantWeight = 0;

      for (let i = 0; i < imgData.length; i += 4) {
        const pr = imgData[i];
        const pg = imgData[i + 1];
        const pb = imgData[i + 2];
        const pa = imgData[i + 3];
        if (pa < 100) continue;

        const [h, s, l] = rgbToHsl(pr, pg, pb);
        // Ignore gray, pure white, pure black
        if (s < 0.18 || l < 0.12 || l > 0.90) continue;

        // Exponential weight for high-chroma pixels (e.g. neon, hair, apparel, background highlights)
        const weight = Math.pow(s, 2.2) * (1 - Math.abs(l - 0.5) * 1.4);
        const bIdx = Math.floor(h / 30) % 12;
        buckets[bIdx] += weight;
        hueSums[bIdx] += h * weight;
        totalVibrantWeight += weight;
      }

      if (totalVibrantWeight < 0.1) {
        return getFallbackAccent(defaultKey);
      }

      let bestBucket = -1, maxWeight = 0;
      for (let i = 0; i < 12; i++) {
        if (buckets[i] > maxWeight) {
          maxWeight = buckets[i];
          bestBucket = i;
        }
      }

      if (bestBucket === -1 || buckets[bestBucket] === 0) {
        return getFallbackAccent(defaultKey);
      }

      const winningHue = Math.round(hueSums[bestBucket] / buckets[bestBucket]);
      // Optimize vibrancy for OLED: high saturation (82%) and optimal lightness (58%)
      return hslToRgb(winningHue, 0.82, 0.58);
    } catch (e) {
      return getFallbackAccent(defaultKey);
    }
  }

  // 专属极速霓虹光谱氛围色：零额外网络请求、零 CORS 隐患、100% 稳定出图
  function extractDominantColorWithProbe(imgSrc, fallbackKey, onColorReady) {
    if (!imgSrc || imgSrc.startsWith('data:')) return;
    try {
      const urlObj = new URL(imgSrc, window.location.href);
      // 仅对完全同源资源或本地代理资源尝试探针，杜绝浏览器底层向控制台抛出任何跨域阻断红字
      if (urlObj.origin !== window.location.origin) {
        return;
      }
      const probe = new Image();
      probe.crossOrigin = 'anonymous';
      probe.decoding = 'async';
      probe.onload = () => {
        try {
          const rgb = extractDominantColor(probe, fallbackKey);
          if (rgb && onColorReady) onColorReady(rgb);
        } catch (e) {}
      };
      probe.onerror = () => {};
      probe.src = imgSrc;
    } catch (e) {}
  }

  // ==================== 1. Canvas Starfield Particles Background ====================
  function initCanvasParticles() {
    const canvas = document.getElementById('bg-particles-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const numParticles = Math.min(Math.floor((width * height) / 24000), 45);
    const particles = [];

    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.4 + 0.6,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        alpha: Math.random() * 0.5 + 0.2
      });
    }

    function render() {
      ctx.clearRect(0, 0, width, height);

      particles.forEach((p, idx) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0) p.x = width;
        if (p.x > width) p.x = 0;
        if (p.y < 0) p.y = height;
        if (p.y > height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(56, 189, 248, ${p.alpha})`;
        ctx.fill();

        for (let j = idx + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 105) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = `rgba(56, 189, 248, ${(1 - dist / 105) * 0.12})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      });

      requestAnimationFrame(render);
    }

    render();
  }

  initCanvasParticles();

  // ==================== 1.5 Blogger Click Tracking Engine (Anti-Spam + Offline Queue + Smart Batch Flush) ====================
  const CLICK_COOLDOWN_MS = 10 * 60 * 1000; // 10 minutes anti-spam per blogger per browser
  const OFFLINE_QUEUE_KEY = 'x_offline_click_queue';
  const TIMESTAMPS_KEY = 'x_blogger_click_timestamps';
  const DAILY_QUOTA_KEY = 'x_blogger_click_daily_quota_v1';
  const MAX_DAILY_NETWORK_FLUSHES = 20; // 单设备每日最多允许 20 次网络批量上报
  const MIN_FLUSH_INTERVAL_MS = 60000; // 严格拉长至 60 秒最小网络上报间隔
  let clickFlushTimer = null;
  let isFlushingClicks = false;
  let lastFlushTimestamp = 0;

  function getTodayDateKey() {
    const d = new Date();
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  }

  function getDailyNetworkFlushCount() {
    try {
      const raw = localStorage.getItem(DAILY_QUOTA_KEY);
      if (!raw) return 0;
      const data = JSON.parse(raw);
      if (data && data.date === getTodayDateKey()) {
        return Number(data.count) || 0;
      }
      return 0; // 跨自然日自动重置
    } catch (e) {
      return 0;
    }
  }

  function recordDailyNetworkFlush() {
    try {
      const today = getTodayDateKey();
      const current = getDailyNetworkFlushCount();
      localStorage.setItem(DAILY_QUOTA_KEY, JSON.stringify({ date: today, count: current + 1 }));
    } catch (e) {}
  }

  function getOfflineClickQueue() {
    try {
      const raw = localStorage.getItem(OFFLINE_QUEUE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function saveOfflineClickQueue(queue) {
    try {
      if (Object.keys(queue).length === 0) {
        localStorage.removeItem(OFFLINE_QUEUE_KEY);
      } else {
        localStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
      }
    } catch (e) {}
  }

  function getBloggerClickTimestamps() {
    try {
      const raw = localStorage.getItem(TIMESTAMPS_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function saveBloggerClickTimestamps(map) {
    try {
      localStorage.setItem(TIMESTAMPS_KEY, JSON.stringify(map));
    } catch (e) {}
  }

  function trackBloggerClick(screenName, source = 'card') {
    if (!screenName) return;
    const handleKey = screenName.toLowerCase();
    const now = Date.now();

    // 1. 同博主 10 分钟防刷检查 (Anti-Spam 10-Minute Cooldown)
    const timestamps = getBloggerClickTimestamps();
    const lastClick = timestamps[handleKey] || 0;
    if (now - lastClick < CLICK_COOLDOWN_MS) {
      // 冷却期内：照常允许用户跳转推特，但跳过热度上报，杜绝连击刷榜
      return;
    }
    timestamps[handleKey] = now;
    saveBloggerClickTimestamps(timestamps);

    // 2. 本地即时响应：直接更新内存数据
    const targetUser = state.rawUsers.find(u => (u.screen_name || '').toLowerCase() === handleKey);
    if (targetUser) {
      targetUser.clicks_card = targetUser.clicks_card || 0;
      targetUser.clicks_timeline = targetUser.clicks_timeline || 0;
      targetUser.clicks_roulette = targetUser.clicks_roulette || 0;
      targetUser.total_clicks = targetUser.total_clicks || 0;
      if (source === 'timeline') targetUser.clicks_timeline++;
      else if (source === 'roulette') targetUser.clicks_roulette++;
      else targetUser.clicks_card++;
      targetUser.total_clicks++;
    }

    // 3. 写入本地离线队列 (Offline Queue)
    const queue = getOfflineClickQueue();
    if (!queue[handleKey]) {
      queue[handleKey] = {
        screen_name: screenName,
        card: 0,
        timeline: 0,
        roulette: 0,
        total: 0
      };
    }
    if (source === 'timeline') queue[handleKey].timeline++;
    else if (source === 'roulette') queue[handleKey].roulette++;
    else queue[handleKey].card++;
    queue[handleKey].total++;
    saveOfflineClickQueue(queue);

    // 4. 触发 60 秒严格节流防抖合并上报（非紧急外跳不单发）
    scheduleClickFlush(MIN_FLUSH_INTERVAL_MS);
  }

  function scheduleClickFlush(delayMs = 60000) {
    if (clickFlushTimer) clearTimeout(clickFlushTimer);
    clickFlushTimer = setTimeout(() => {
      flushPendingClickQueue(false);
    }, delayMs);
  }

  async function flushPendingClickQueue(force = false) {
    if (isFlushingClicks) return;
    const queue = getOfflineClickQueue();
    const keys = Object.keys(queue);
    if (keys.length === 0) return;

    // 阀门：单设备每日 20 次网络上报上限守护
    const flushCount = getDailyNetworkFlushCount();
    if (flushCount >= MAX_DAILY_NETWORK_FLUSHES) {
      // 当天网络上报配额已达 20 次：安静保存在本地 LocalStorage，不再向边缘发包，保护后端配额
      return;
    }

    const now = Date.now();
    // 非强制模式下，若距离上次上报未满 60 秒且队列少于 5 条，继续留在本地合并
    if (!force && (now - lastFlushTimestamp < MIN_FLUSH_INTERVAL_MS) && keys.length < 5) {
      return;
    }

    isFlushingClicks = true;
    lastFlushTimestamp = now;

    // 制作本次提交快照 (Snapshot for Ack verification)
    const batchList = keys.map(k => queue[k]);
    const snapshotKeys = new Set(keys);

    try {
      const payload = JSON.stringify({ batch: batchList });

      // 页面进入后台离开且支持 Beacon 时，使用标准 sendBeacon 传输，零阻塞页面
      if (document.visibilityState === 'hidden' && typeof navigator.sendBeacon === 'function') {
        const blob = new Blob([payload], { type: 'application/json' });
        const sent = navigator.sendBeacon('/api/track-click?tk=v2', blob);
        if (sent) {
          recordDailyNetworkFlush();
          const currentQueue = getOfflineClickQueue();
          snapshotKeys.forEach(k => delete currentQueue[k]);
          saveOfflineClickQueue(currentQueue);
          isFlushingClicks = false;
          return;
        }
      }

      const res = await fetch('/api/track-click', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-NvPuSa-Tracker': 'v2'
        },
        body: payload,
        keepalive: true
      });

      if (res.ok) {
        const json = await res.json().catch(() => ({}));
        if (json.success) {
          recordDailyNetworkFlush();
          // 收到确认：安全销毁本次成功提交的快照项，防止重复提交
          const currentQueue = getOfflineClickQueue();
          snapshotKeys.forEach(k => delete currentQueue[k]);
          saveOfflineClickQueue(currentQueue);
        }
      }
    } catch (err) {
      // 遇到网络离线或 1027 额度降级：保留本地队列，平滑无报错
      console.warn('[Track Engine] Click batch report deferred (offline/rate-limited):', err);
    } finally {
      isFlushingClicks = false;
    }
  }

  // 监听页面生命周期：跳出或切到后台时，只有当队列累积较多 (>= 3 条) 且达到时间窗口时才上报
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      const queue = getOfflineClickQueue();
      const keys = Object.keys(queue);
      if (keys.length >= 3 && (Date.now() - lastFlushTimestamp >= MIN_FLUSH_INTERVAL_MS)) {
        flushPendingClickQueue(true);
      }
    }
  });

  window.addEventListener('beforeunload', () => {
    const queue = getOfflineClickQueue();
    const keys = Object.keys(queue);
    if (keys.length >= 3 && (Date.now() - lastFlushTimestamp >= MIN_FLUSH_INTERVAL_MS)) {
      flushPendingClickQueue(true);
    }
  });

  // 页面初次加载后，延迟 8 秒轻量检查一次是否有历史离线残留数据需要同步
  setTimeout(() => {
    const queue = getOfflineClickQueue();
    if (Object.keys(queue).length > 0) {
      flushPendingClickQueue(false);
    }
  }, 8000);

  window.trackBloggerClick = trackBloggerClick;

  // ==================== 2. State Store (Default Theme: OLED) ====================
  const PAGE_SIZE = 12;
  const state = {
    rawUsers: [],
    filteredUsers: [],
    renderedCount: 0,
    columnElements: [],
    spotlightUser: null,
    currentFilter: 'all',
    currentSort: 'followers-desc',
    currentView: 'grid', // 'grid' | 'compact' | 'list'
    currentTheme: localStorage.getItem('x_archive_v2_theme') || 'oled',
    searchQuery: '',
    isShuffling: false,
    isLoadingMore: false
  };

  const fallbackCovers = [
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=800&auto=format&fit=crop&q=80'
  ];

  // DOM Elements Cache
  const htmlRoot = document.documentElement;
  const bloggerWall = document.getElementById('blogger-wall');
  const emptyStateDb = document.getElementById('empty-state-db');
  const emptyStateSearch = document.getElementById('empty-state-search');
  const infiniteSentinel = document.getElementById('infinite-scroll-sentinel');
  const btnLoadSampleData = document.getElementById('btn-load-sample-data');
  const globalSearch = document.getElementById('global-search');
  const searchClearBtn = document.getElementById('search-clear-btn');
  
  // Hero & Stats
  const statTotalChip = document.getElementById('stat-total-chip');
  const statVerifiedChip = document.getElementById('stat-verified-chip');
  const statMaxChip = document.getElementById('stat-max-chip');
  const heroSpotlightCard = document.getElementById('hero-spotlight-card');
  const spotlightContent = document.getElementById('spotlight-dynamic-content');
  const btnShuffleSpotlight = document.getElementById('btn-shuffle-spotlight');

  // Filter Pills & Badges
  const filterPills = document.querySelectorAll('.f-pill');
  const badgeCountAll = document.getElementById('badge-count-all');
  const badgeCountHot = document.getElementById('badge-count-hot');
  const badgeCountVerified = document.getElementById('badge-count-verified');
  const badgeCountRecent = document.getElementById('badge-count-recent');
  const badgeCountLost = document.getElementById('badge-count-lost');
  const resultsCountText = document.getElementById('results-count-text');
  const btnResetFilters = document.getElementById('btn-reset-filters');

  // Sort Menu
  const sortTriggerBtn = document.getElementById('sort-trigger-btn');
  const sortMenu = document.getElementById('sort-menu');
  const sortCurrentText = document.getElementById('sort-current-text');
  const sortMenuItems = document.querySelectorAll('.select-dropdown-menu .menu-item');

  // View Switchers
  const viewTabs = document.querySelectorAll('.view-tab-btn');

  // Pure Icon Dual-Theme Toggle Button
  const themeBtn = document.getElementById('theme-btn');
  const themeIconSun = document.getElementById('theme-icon-sun');
  const themeIconMoon = document.getElementById('theme-icon-moon');

  // Lucky Pick Frameless Roulette Modal Elements
  const btnLuckyPick = document.getElementById('btn-lucky-pick');
  const rouletteBackdrop = document.getElementById('random-roulette-backdrop');
  const rouletteCardContainer = document.getElementById('roulette-card-container');
  const rouletteBanner = document.getElementById('roulette-banner');
  const rouletteAvatar = document.getElementById('roulette-avatar');
  const rouletteTag = document.getElementById('roulette-tag');
  const rouletteName = document.getElementById('roulette-name');
  const rouletteVerified = document.getElementById('roulette-verified');
  const rouletteHandle = document.getElementById('roulette-handle');
  const rouletteBio = document.getElementById('roulette-bio');
  const rouletteOutsideActions = document.getElementById('roulette-outside-actions');
  const rouletteDismissHint = document.getElementById('roulette-dismiss-hint');
  const btnReshuffleAgain = document.getElementById('btn-reshuffle-again');
  const btnRouletteVisit = document.getElementById('btn-roulette-visit');

  // Standard Inspector Drawer (for regular card click)
  const inspectorBackdrop = document.getElementById('inspector-backdrop');
  const drawerCloseBtn = document.getElementById('drawer-close-btn');
  const drawerBody = document.getElementById('drawer-body-content');
  const toastContainer = document.getElementById('toast-container');

  // ==================== 3. React-Bits Motion Modules ====================

  function animateCountUp(element, endVal, duration = 1000, isPercent = false, isFollowers = false) {
    if (!element) return;
    const startVal = 0;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const currentVal = Math.floor(startVal + (endVal - startVal) * easeProgress);

      if (isPercent) {
        element.textContent = `${currentVal}%`;
      } else if (isFollowers) {
        element.textContent = formatFollowers(currentVal);
      } else {
        element.textContent = currentVal.toLocaleString();
      }

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        if (isPercent) element.textContent = `${endVal}%`;
        else if (isFollowers) element.textContent = formatFollowers(endVal);
        else element.textContent = endVal.toLocaleString();
      }
    }

    requestAnimationFrame(update);
  }

  function triggerClickSpark(e, sparkCount = 12, color = 'var(--accent-spark)') {
    const x = e ? (e.clientX || window.innerWidth / 2) : window.innerWidth / 2;
    const y = e ? (e.clientY || window.innerHeight / 2) : window.innerHeight / 2;

    for (let i = 0; i < sparkCount; i++) {
      const spark = document.createElement('div');
      spark.className = 'click-spark-particle';

      const angle = (Math.PI * 2 * i) / sparkCount + (Math.random() - 0.5) * 0.5;
      const distance = 35 + Math.random() * 40;
      const dx = Math.cos(angle) * distance;
      const dy = Math.sin(angle) * distance;
      const size = 3 + Math.random() * 4;

      spark.style.left = `${x}px`;
      spark.style.top = `${y}px`;
      spark.style.width = `${size}px`;
      spark.style.height = `${size}px`;
      spark.style.backgroundColor = color;
      spark.style.boxShadow = `0 0 12px ${color}`;
      spark.style.setProperty('--dx', `${dx}px`);
      spark.style.setProperty('--dy', `${dy}px`);

      document.body.appendChild(spark);

      setTimeout(() => spark.remove(), 650);
    }
  }

  function triggerLuxuryCelebrationFireworks(originElement) {
    let cx = window.innerWidth / 2;
    let cy = window.innerHeight / 2;

    if (originElement) {
      const rect = originElement.getBoundingClientRect();
      cx = rect.left + rect.width / 2;
      cy = rect.top + rect.height / 2;
    }

    const colors = [
      '#f59e0b', // Luxury Gold
      '#fbbf24', // Amber
      '#38bdf8', // Electric Cyan
      '#ec4899', // Cyber Pink
      '#a855f7', // Purple Neon
      '#ffffff', // Diamond Sparkle
      '#10b981'  // Emerald
    ];

    const shapes = ['star', 'diamond', 'circle', 'ribbon'];
    const particleCount = 52;

    for (let i = 0; i < particleCount; i++) {
      const p = document.createElement('div');
      p.className = 'celebration-burst-particle';

      const color = colors[Math.floor(Math.random() * colors.length)];
      const shape = shapes[Math.floor(Math.random() * shapes.length)];
      
      const angle = (Math.PI * 2 * i) / particleCount + (Math.random() - 0.5) * 0.45;
      const distance = 85 + Math.random() * 240;
      const vx = Math.cos(angle) * distance;
      const vy = Math.sin(angle) * distance - (35 + Math.random() * 45); // Natural pop with upward velocity

      const duration = 0.95 + Math.random() * 0.75;
      const rotMid = `${(Math.random() - 0.5) * 360}deg`;
      const rotLate = `${(Math.random() - 0.5) * 720}deg`;
      const rotEnd = `${(Math.random() - 0.5) * 1080}deg`;

      p.style.left = `${cx}px`;
      p.style.top = `${cy}px`;
      p.style.setProperty('--vx', `${vx}px`);
      p.style.setProperty('--vy', `${vy}px`);
      p.style.setProperty('--duration', `${duration}s`);
      p.style.setProperty('--rot-mid', rotMid);
      p.style.setProperty('--rot-late', rotLate);
      p.style.setProperty('--rot-end', rotEnd);
      p.style.color = color;

      if (shape === 'star') {
        p.classList.add('celebration-star-particle');
        const size = 12 + Math.random() * 10;
        p.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}" stroke="${color}" stroke-width="1"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>`;
      } else if (shape === 'diamond') {
        p.classList.add('celebration-star-particle');
        const size = 10 + Math.random() * 8;
        p.innerHTML = `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="${color}"><polygon points="12 2 22 12 12 22 2 12"/></svg>`;
      } else if (shape === 'ribbon') {
        p.classList.add('celebration-confetti-ribbon');
        const w = 5 + Math.random() * 5;
        const h = 10 + Math.random() * 10;
        p.style.width = `${w}px`;
        p.style.height = `${h}px`;
        p.style.backgroundColor = color;
      } else {
        const size = 6 + Math.random() * 6;
        p.style.width = `${size}px`;
        p.style.height = `${size}px`;
        p.style.borderRadius = '50%';
        p.style.backgroundColor = color;
        p.style.boxShadow = `0 0 12px ${color}, 0 0 22px ${color}`;
      }

      document.body.appendChild(p);

      setTimeout(() => {
        p.remove();
      }, duration * 1000 + 100);
    }
  }

  function attachSpotlightEffect(cardElement) {
    if (!cardElement) return;
    cardElement.classList.add('spotlight-interactive');

    cardElement.addEventListener('mousemove', (e) => {
      const rect = cardElement.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      cardElement.style.setProperty('--mouse-x', `${x}px`);
      cardElement.style.setProperty('--mouse-y', `${y}px`);
    });
  }

  function attach3DTilt(element, maxTilt = 7) {
    if (!element) return;
    element.classList.add('tilt-card-wrap');

    element.addEventListener('mousemove', (e) => {
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = ((y - centerY) / centerY) * -maxTilt;
      const rotateY = ((x - centerX) / centerX) * maxTilt;

      element.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-4px)`;
    });

    element.addEventListener('mouseleave', () => {
      element.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
    });
  }

  if (heroSpotlightCard) {
    attachSpotlightEffect(heroSpotlightCard);
    attach3DTilt(heroSpotlightCard, 6);
  }

  // ==================== 4. Pure Icon Dual-Theme Toggle Engine (OLED by Default) ====================
  function applyTheme(theme) {
    state.currentTheme = theme === 'light' ? 'light' : 'oled';
    htmlRoot.setAttribute('data-theme', state.currentTheme);
    localStorage.setItem('x_archive_v2_theme', state.currentTheme);

    if (state.currentTheme === 'light') {
      themeIconSun?.classList.remove('hidden');
      themeIconMoon?.classList.add('hidden');
      themeBtn?.setAttribute('title', '当前: 清爽浅色 · 点击切换为纯黑极简 (OLED) [快捷键: T]');
    } else {
      themeIconSun?.classList.add('hidden');
      themeIconMoon?.classList.remove('hidden');
      themeBtn?.setAttribute('title', '当前: 纯黑极简 · 点击切换为清爽浅色 (Light) [快捷键: T]');
    }
  }

  themeBtn?.addEventListener('click', (e) => {
    triggerClickSpark(e, 8, 'var(--accent-primary)');
    const nextTheme = state.currentTheme === 'oled' ? 'light' : 'oled';
    applyTheme(nextTheme);
    showToast(`已切换至 ${nextTheme === 'light' ? '清爽浅色' : '纯黑极简 (OLED)'} 模式`);
  });

  applyTheme(state.currentTheme);

  // Close Sort menu when clicking outside
  document.addEventListener('click', (e) => {
    if (!sortMenu?.contains(e.target) && !sortTriggerBtn?.contains(e.target)) {
      sortMenu?.classList.add('hidden');
      sortTriggerBtn?.setAttribute('aria-expanded', 'false');
    }
  });

  // ==================== 5. Fetch Archive Data (HA Multi-Track: R2 Direct CDN -> Static Local -> Dynamic API -> LocalStorage) ====================
  async function initArchiveData() {
    let loaded = false;

    // 自动补发可能积攒的离线点击队列 (Auto-flush offline clicks)
    try {
      flushPendingClickQueue();
    } catch (e) {}

    // 先行就绪 R2 域名配置（静态配置优先，0 函数额度消耗）
    await fetchServerRuntimeConfig();

    // Track 1: R2 公共 CDN 极速直链 (100% 静态免函数、免 D1、实时更新且无用量上限 — 极速首选)
    if (R2_CDN_BASE) {
      try {
        const r2Url = `${R2_CDN_BASE}/data/archive.json`;
        const r2Res = await fetch(r2Url);
        if (r2Res.ok) {
          const r2Data = await r2Res.json();
          if (Array.isArray(r2Data) && r2Data.length > 0) {
            state.rawUsers = r2Data;
            localStorage.setItem('x_archive_cached_data', JSON.stringify(r2Data));
            loaded = true;
          }
        }
      } catch (r2Err) {
        console.warn('[HA Data Loader] R2 direct CDN fetch failed, falling back to local static JSON:', r2Err);
      }
    }

    // Track 2: 站点同源静态 JSON 兜底 (Free, Zero Rate-Limits, Unlimited Traffic)
    if (!loaded) {
      try {
        const staticRes = await fetch('/data/archive.json');
        if (staticRes.ok) {
          const staticData = await staticRes.json();
          if (Array.isArray(staticData) && staticData.length > 0) {
            state.rawUsers = staticData;
            localStorage.setItem('x_archive_cached_data', JSON.stringify(staticData));
            loaded = true;
          }
        }
      } catch (staticErr) {
        console.warn('[HA Data Loader] Static CDN fetch failed, falling back to dynamic API:', staticErr);
      }
    }

    // Track 3: Dynamic API Fallback (D1 Database + Edge CDN Cache — 仅在静态文件失败时降级)
    if (!loaded) {
      try {
        const res = await fetch('/api/archive');
        if (res.ok) {
          const json = await res.json();
          if (json.r2_domain !== undefined) {
            setR2CdnDomain(json.r2_domain);
          }
          if (json.success && Array.isArray(json.data) && json.data.length > 0) {
            state.rawUsers = json.data;
            localStorage.setItem('x_archive_cached_data', JSON.stringify(json.data));
            loaded = true;
          }
        }
      } catch (err) {
        console.warn('[HA Data Loader] Dynamic API fetch also failed:', err);
      }
    }

    // Track 4: LocalStorage offline cache
    if (!loaded) {
      fallbackToLocalStorage();
    }

    updateHeroAndMetrics();
    pickSpotlightCreator();
    updateSortMenuForFilter('all');
    applyFilterAndSort();
  }

  function fallbackToLocalStorage() {
    const cached = localStorage.getItem('x_archive_cached_data');
    if (cached) {
      try {
        const list = JSON.parse(cached);
        if (Array.isArray(list) && list.length > 0) {
          state.rawUsers = list;
        }
      } catch (e) {}
    }
  }

  btnLoadSampleData?.addEventListener('click', (e) => {
    triggerClickSpark(e, 14, 'var(--accent-gold)');
    state.rawUsers = defaultSampleData;
    localStorage.setItem('x_archive_cached_data', JSON.stringify(defaultSampleData));
    updateHeroAndMetrics();
    pickSpotlightCreator();
    applyFilterAndSort();
    showToast('已成功载入样例博主数据进行画廊体验！');
  });

  // ==================== 6. Metrics & Hero Spotlight ====================
  function formatFollowers(num) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  function updateHeroAndMetrics() {
    const total = state.rawUsers.length;
    // 存活活跃博主（排除赛博坟场已封号/注销博主）
    const aliveUsers = state.rawUsers.filter(u => !u.is_suspended || u.is_suspended === 0);
    const aliveTotal = aliveUsers.length;

    // 归档总数包含全站所有归档博主（含赛博坟场）
    animateCountUp(statTotalChip, total, 1000);

    if (total === 0) {
      statVerifiedChip.textContent = '0%';
      statMaxChip.textContent = '0';
      badgeCountAll.textContent = '0';
      badgeCountVerified.textContent = '0';
      if (badgeCountRecent) badgeCountRecent.textContent = '0';
      if (badgeCountLost) badgeCountLost.textContent = '0';
      return;
    }

    const verifiedCount = state.rawUsers.filter(u => u.verified).length;
    const verifiedPercent = total > 0 ? Math.round((verifiedCount / total) * 100) : 0;
    animateCountUp(statVerifiedChip, verifiedPercent, 1200, true);

    const maxFollowers = aliveUsers.length > 0 ? Math.max(...aliveUsers.map(u => u.followers_count || 0)) : 0;
    animateCountUp(statMaxChip, maxFollowers, 1400, false, true);

    // 计算 7 天内最新归档的存活博主数
    const now = Date.now();
    const sevenDaysMs = 7 * 24 * 3600 * 1000;
    const recentCount = aliveUsers.filter(u => {
      if (!u.backed_up_at) return false;
      const t = new Date(u.backed_up_at).getTime();
      return !isNaN(t) && (now - t) <= sevenDaysMs;
    }).length;

    const clickedCount = aliveUsers.filter(u => (u.total_clicks || 0) > 0).length;
    const lostCount = state.rawUsers.filter(u => u.is_suspended === 1 || u.is_suspended === 2).length;

    badgeCountAll.textContent = aliveTotal.toString();
    if (badgeCountHot) badgeCountHot.textContent = (clickedCount || aliveTotal).toString();
    badgeCountVerified.textContent = verifiedCount.toString();
    if (badgeCountRecent) badgeCountRecent.textContent = (recentCount || Math.min(aliveTotal, 5)).toString();
    if (badgeCountLost) badgeCountLost.textContent = lostCount.toString();
  }

  // ==================== R2 边缘 CDN 域名自适应解析引擎 ====================
  function normalizeR2Domain(domain) {
    if (!domain) return '';
    let clean = String(domain).trim().replace(/\/+$/, '');
    if (!clean || clean === 'none' || clean === 'false') return '';
    if (!/^https?:\/\//i.test(clean)) {
      clean = 'https://' + clean;
    }
    return clean;
  }

  let R2_CDN_BASE = "https://img.boomboomboom.ggff.net";

  function setR2CdnDomain(domain) {
    if (domain === null || domain === undefined) return;
    const clean = normalizeR2Domain(domain);
    R2_CDN_BASE = clean;
    try {
      if (clean) {
        localStorage.setItem('x_archive_r2_domain', clean);
        sessionStorage.setItem('x_archive_r2_domain', clean);
      }
    } catch (e) {}
  }

  // 运行时配置探测引擎：优先静态 runtime-config.json（0 Worker 消耗），次选 /api/config
  let runtimeConfigPromise = null;
  function fetchServerRuntimeConfig() {
    if (runtimeConfigPromise) return runtimeConfigPromise;
    runtimeConfigPromise = (async () => {
      // 1. 静态 CDN 构建产物优先（100% 免 Functions，用量耗尽时亦可秒开）
      try {
        const staticRes = await fetch('/runtime-config.json');
        if (staticRes.ok) {
          const staticCfg = await staticRes.json();
          if (staticCfg && staticCfg.r2_public_domain) {
            setR2CdnDomain(staticCfg.r2_public_domain);
            return staticCfg;
          }
        }
      } catch (e) {}

      // 2. 动态云端 Functions 降级读取（云端 Functions 在线时生效）
      try {
        const res = await fetch('/api/config');
        if (res.ok) {
          const cfg = await res.json();
          if (cfg && cfg.r2_public_domain) {
            setR2CdnDomain(cfg.r2_public_domain);
            return cfg;
          }
        }
      } catch (e) {}

      return null;
    })();
    return runtimeConfigPromise;
  }
  fetchServerRuntimeConfig();

  // 全局媒体图片加载容错引擎：优先直连 R2 CDN，若 R2 暂未收录该图（404）则平滑降级走云端 Worker 代理转存
  window.handleMediaImgError = function(img, rawUrl, type) {
    if (!img) return;
    if (!img.dataset.retryDone && rawUrl && rawUrl.includes('twimg.com') && img.src && !img.src.includes('/api/media')) {
      img.dataset.retryDone = '1';
      img.src = `/api/media?url=${encodeURIComponent(rawUrl)}`;
      return;
    }
    if (type === 'avatar') {
      img.src = 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';
    } else {
      img.style.opacity = '0';
    }
  };

  function resolveMediaUrl(url) {
    if (!url) return '';
    
    // 1. 若为已归档至 R2 的相对路径 (/api/media?key=...)，优先直接路由至 Cloudflare 全球 CDN 直链（0 Worker 消耗）
    if (R2_CDN_BASE && url.includes('/api/media') && url.includes('key=')) {
      try {
        const dummyUrl = new URL(url, window.location.origin);
        const key = dummyUrl.searchParams.get('key');
        if (key) {
          return `${R2_CDN_BASE}/${key.replace(/^\/+/, '')}`;
        }
      } catch (e) {}
    }

    // 2. 若配置了 R2 CDN 且为 Twitter 图片原链，直接映射为 R2 全球 CDN 静态直链（0 Worker 消耗）
    if (R2_CDN_BASE && url.includes('twimg.com')) {
      try {
        const parsed = new URL(url);
        const cleanPath = parsed.pathname.replace(/^\/+/, '').replace(/\//g, '_');
        if (url.includes('profile_images')) {
          return `${R2_CDN_BASE}/avatars/${cleanPath}`;
        } else if (url.includes('profile_banners')) {
          return `${R2_CDN_BASE}/covers/${cleanPath}`;
        } else {
          return `${R2_CDN_BASE}/media/${cleanPath}`;
        }
      } catch (e) {}
    }

    // 3. 原生相对路径或已处理路径直接返回
    if (url.startsWith('/api/media') || url.startsWith('data:') || url.startsWith('/')) {
      return url;
    }

    // 4. 未配置 R2 CDN 时的自适应降级：走动态边缘代理
    if (url.includes('twimg.com')) {
      return `/api/media?url=${encodeURIComponent(url)}`;
    }
    return url;
  }

  function pickSpotlightCreator() {
    if (state.rawUsers.length === 0) {
      spotlightContent.innerHTML = `
        <div style="padding: 6px 0; color: var(--text-secondary); font-size: 13px; line-height: 1.6;">
          <div style="font-weight: 700; color: var(--text-main); margin-bottom: 4px;">准备好探索精选博主了吗？</div>
          <div>在控制台配置 Cookie 并点击一键同步后，此处将为您自动推送主页优质创作者。</div>
        </div>
      `;
      return;
    }

    // 过滤掉已封号 (is_suspended = 1) 和已注销 (is_suspended = 2) 的博主
    const activeUsers = state.rawUsers.filter(u => !u.is_suspended || u.is_suspended === 0);
    const basePool = activeUsers.length > 0 ? activeUsers : state.rawUsers;
    const candidates = basePool.filter(u => u.followers_count >= 50000 || u.verified);
    const pool = candidates.length > 0 ? candidates : basePool;
    const randomUser = pool[Math.floor(Math.random() * pool.length)];

    renderSpotlightCard(randomUser);
  }

  function renderSpotlightCard(user) {
    const rawAvatar = user.avatar_url || 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';
    const avatar = resolveMediaUrl(rawAvatar);
    const isTopTier = (user.followers_count >= 500000);
    const tag = isTopTier ? 'Top Creator' : 'Creator';

    spotlightContent.innerHTML = `
      <div class="spotlight-avatar-wrap" onclick="window.trackBloggerClick('${escapeHtml(user.screen_name)}', 'card'); window.open('https://x.com/${user.screen_name}', '_blank')">
        <img class="spotlight-avatar" src="${avatar}" alt="${escapeHtml(user.name)}" onerror="this.src='https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';">
        ${user.verified ? `<div class="badge-verified-native" style="bottom: 2px; right: 2px;" title="Twitter 官方认证">${ICONS.verifiedNative}</div>` : ''}
      </div>
      <div class="spotlight-meta">
        <div class="spotlight-name-row">
          <span class="spotlight-name" title="${escapeHtml(user.name)}">${escapeHtml(user.name)}</span>
          <span class="card-influence-pill ${isTopTier ? 'top-tier' : ''}">${escapeHtml(tag)}</span>
        </div>
        <a class="spotlight-handle" href="https://x.com/${user.screen_name}" target="_blank" onclick="window.trackBloggerClick('${escapeHtml(user.screen_name)}', 'card');">@${escapeHtml(user.screen_name)} · ${formatFollowers(user.followers_count)} 关注</a>
        <div class="spotlight-bio-snippet">${formatBioWithLinks(user.description)}</div>
      </div>
    `;
  }

  btnShuffleSpotlight?.addEventListener('click', (e) => {
    triggerClickSpark(e, 12, 'var(--accent-primary)');
    pickSpotlightCreator();
  });

  // ==================== 7. Filtering & Sorting Engine ====================
  function applyFilterAndSort() {
    const query = state.searchQuery.trim().toLowerCase();

    state.filteredUsers = state.rawUsers.filter(user => {
      const isLost = (user.is_suspended === 1 || user.is_suspended === 2);

      // 严格隔离赛博坟场：如果当前不是 lost 分类，绝不展示封号/注销博主！
      if (state.currentFilter === 'lost') {
        if (!isLost) return false;
      } else {
        if (isLost) return false;
      }

      const matchesQuery = !query ||
        (user.screen_name && user.screen_name.toLowerCase().includes(query)) ||
        (user.name && user.name.toLowerCase().includes(query)) ||
        (user.description && user.description.toLowerCase().includes(query));

      let matchesFilter = true;
      if (state.currentFilter === 'verified') {
        matchesFilter = !!user.verified;
      } else if (state.currentFilter === 'top') {
        matchesFilter = (user.followers_count || 0) >= 500000;
      } else if (state.currentFilter === '100k') {
        matchesFilter = (user.followers_count || 0) >= 100000;
      } else if (state.currentFilter === 'hot') {
        matchesFilter = true;
      } else if (state.currentFilter === 'recent') {
        matchesFilter = true;
      } else if (state.currentFilter === 'lost') {
        matchesFilter = true;
      }

      return matchesQuery && matchesFilter;
    });

    state.filteredUsers.sort((a, b) => {
      if (state.currentSort === 'clicks-desc') {
        const clickDiff = (b.total_clicks || 0) - (a.total_clicks || 0);
        if (clickDiff !== 0) return clickDiff;
        return (b.followers_count || 0) - (a.followers_count || 0);
      } else if (state.currentSort === 'clicks-asc') {
        const clickDiff = (a.total_clicks || 0) - (b.total_clicks || 0);
        if (clickDiff !== 0) return clickDiff;
        return (a.followers_count || 0) - (b.followers_count || 0);
      } else if (state.currentSort === 'recent' || state.currentFilter === 'recent') {
        const timeA = a.backed_up_at ? new Date(a.backed_up_at).getTime() : 0;
        const timeB = b.backed_up_at ? new Date(b.backed_up_at).getTime() : 0;
        if (!isNaN(timeA) && !isNaN(timeB) && timeA !== timeB) {
          return timeB - timeA;
        }
        return (b.id || '').toString().localeCompare((a.id || '').toString());
      } else if (state.currentSort === 'followers-desc') {
        return (b.followers_count || 0) - (a.followers_count || 0);
      } else if (state.currentSort === 'followers-asc') {
        return (a.followers_count || 0) - (b.followers_count || 0);
      } else if (state.currentSort === 'name-asc') {
        return (a.name || a.screen_name).localeCompare(b.name || b.screen_name);
      }
      return 0;
    });

    resultsCountText.textContent = `共呈现 ${state.filteredUsers.length} 位博主归档`;
    
    // Reset columns and start fresh render
    state.renderedCount = 0;
    initMasonryStructure();
    renderMoreCards();
  }

  const SORT_OPTIONS = {
    hot: [
      { val: 'clicks-desc', text: '热度从高到低' },
      { val: 'clicks-asc', text: '热度从低到高' }
    ],
    default: [
      { val: 'followers-desc', text: '粉丝数从高到低' },
      { val: 'followers-asc', text: '粉丝数从低到高' },
      { val: 'name-asc', text: '博主名称 (A → Z)' },
      { val: 'recent', text: '归档时间最近' }
    ]
  };

  function updateSortMenuForFilter(filterName) {
    const isHot = filterName === 'hot';
    const options = isHot ? SORT_OPTIONS.hot : SORT_OPTIONS.default;

    // 检查当前排序值是否在当前类目的合法列表中
    const isValid = options.some(o => o.val === state.currentSort);
    if (!isValid) {
      if (isHot) {
        state.currentSort = 'clicks-desc';
      } else if (filterName === 'recent') {
        state.currentSort = 'recent';
      } else {
        state.currentSort = 'followers-desc';
      }
    }

    const currentOpt = options.find(o => o.val === state.currentSort) || options[0];
    if (sortCurrentText) sortCurrentText.textContent = currentOpt.text;

    if (sortMenu) {
      sortMenu.innerHTML = options.map(opt => {
        const isActive = opt.val === state.currentSort;
        return `
          <div class="menu-item ${isActive ? 'active' : ''}" data-val="${opt.val}" role="option">
            <span>${opt.text}</span>
            <svg class="check-icon ${isActive ? '' : 'hidden'}" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
          </div>
        `;
      }).join('');

      sortMenu.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', () => {
          const val = item.getAttribute('data-val');
          const txt = item.querySelector('span')?.textContent || '';
          setSortMenuSelection(val, txt);
          sortMenu.classList.add('hidden');
          sortTriggerBtn?.setAttribute('aria-expanded', 'false');
          applyFilterAndSort();
        });
      });
    }
  }

  function setSortMenuSelection(sortVal, sortText) {
    state.currentSort = sortVal;
    if (sortCurrentText) sortCurrentText.textContent = sortText;
    sortMenu?.querySelectorAll('.menu-item').forEach(item => {
      const match = item.getAttribute('data-val') === sortVal;
      item.classList.toggle('active', match);
      item.querySelector('.check-icon')?.classList.toggle('hidden', !match);
    });
  }

  globalSearch?.addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    searchClearBtn.classList.toggle('hidden', !state.searchQuery);
    applyFilterAndSort();
  });

  searchClearBtn?.addEventListener('click', () => {
    globalSearch.value = '';
    state.searchQuery = '';
    searchClearBtn.classList.add('hidden');
    globalSearch.focus();
    applyFilterAndSort();
  });

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.currentFilter = pill.getAttribute('data-filter');

      updateSortMenuForFilter(state.currentFilter);
      applyFilterAndSort();
    });
  });

  btnResetFilters?.addEventListener('click', (e) => {
    triggerClickSpark(e, 8, 'var(--accent-primary)');
    globalSearch.value = '';
    state.searchQuery = '';
    searchClearBtn.classList.add('hidden');
    state.currentFilter = 'all';
    filterPills.forEach(p => p.classList.toggle('active', p.getAttribute('data-filter') === 'all'));
    updateSortMenuForFilter('all');
    applyFilterAndSort();
    showToast('已重置所有筛选条件');
  });

  sortTriggerBtn?.addEventListener('click', (e) => {
    e.stopPropagation();
    const isClosed = sortMenu.classList.toggle('hidden');
    sortTriggerBtn.setAttribute('aria-expanded', String(!isClosed));
  });

  viewTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      viewTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      state.currentView = tab.getAttribute('data-view');
      state.renderedCount = 0;
      initMasonryStructure();
      renderMoreCards();
    });
  });

  // ==================== 8. Karpathy Discrete Column Masonry Engine (Zero Layout Shifting) ====================
  function getResponsiveColumnCount(view) {
    const w = window.innerWidth;
    if (view === 'list') return 1;
    if (view === 'compact') {
      if (w <= 640) return 2;
      if (w <= 1024) return 3;
      return 4; // Desktop default
    }
    // grid view
    if (w <= 640) return 1;
    if (w <= 1024) return 2;
    return 3; // Desktop default
  }

  function initMasonryStructure() {
    bloggerWall.innerHTML = '';
    bloggerWall.className = `blogger-wall ${state.currentView}-view`;
    state.columnElements = [];

    if (state.currentView === 'list') {
      // List view is a single vertical container
      state.columnElements = [bloggerWall];
    } else {
      // Responsive discrete columns (Mobile: 1 for Grid / 2 for Compact; Desktop: 3 for Grid / 4 for Compact)
      const numCols = getResponsiveColumnCount(state.currentView);
      for (let i = 0; i < numCols; i++) {
        const col = document.createElement('div');
        col.className = 'masonry-column';
        bloggerWall.appendChild(col);
        state.columnElements.push(col);
      }
    }
  }

  let resizeDebounceTimer = null;
  let activeColCount = getResponsiveColumnCount(state.currentView);
  window.addEventListener('resize', () => {
    clearTimeout(resizeDebounceTimer);
    resizeDebounceTimer = setTimeout(() => {
      const newCols = getResponsiveColumnCount(state.currentView);
      if (newCols !== activeColCount) {
        activeColCount = newCols;
        const currentCount = state.renderedCount;
        state.renderedCount = 0;
        initMasonryStructure();
        // Re-render currently rendered cards count
        const target = Math.max(PAGE_SIZE, currentCount);
        const total = state.filteredUsers.length;
        const renderLimit = Math.min(target, total);
        
        for (let i = 0; i < renderLimit; i++) {
          const user = state.filteredUsers[i];
          const card = createBloggerCardElement(user, i);
          if (state.currentView === 'list') {
            bloggerWall.appendChild(card);
          } else {
            let shortestCol = state.columnElements[0];
            let minHeight = shortestCol.offsetHeight;
            for (let c = 1; c < state.columnElements.length; c++) {
              const col = state.columnElements[c];
              if (col.offsetHeight < minHeight) {
                minHeight = col.offsetHeight;
                shortestCol = col;
              }
            }
            shortestCol.appendChild(card);
          }
        }
        state.renderedCount = renderLimit;
        if (state.renderedCount < total) {
          infiniteSentinel?.classList.remove('hidden');
        } else {
          infiniteSentinel?.classList.add('hidden');
        }
      }
    }, 180);
  });

  function renderMoreCards() {
    if (state.rawUsers.length === 0) {
      emptyStateDb?.classList.remove('hidden');
      emptyStateSearch?.classList.add('hidden');
      infiniteSentinel?.classList.add('hidden');
      return;
    }
    emptyStateDb?.classList.add('hidden');

    if (state.filteredUsers.length === 0) {
      emptyStateSearch?.classList.remove('hidden');
      infiniteSentinel?.classList.add('hidden');
      return;
    }
    emptyStateSearch?.classList.add('hidden');

    const totalFiltered = state.filteredUsers.length;
    const startIndex = state.renderedCount;
    const endIndex = Math.min(startIndex + PAGE_SIZE, totalFiltered);

    if (startIndex >= totalFiltered) {
      infiniteSentinel?.classList.add('hidden');
      return;
    }

    if (state.columnElements.length === 0) {
      initMasonryStructure();
    }

    // Surgical Incremental Append: Append new card directly into shortest column without disturbing existing cards
    for (let i = startIndex; i < endIndex; i++) {
      const user = state.filteredUsers[i];
      const card = createBloggerCardElement(user, i);

      if (state.currentView === 'list') {
        bloggerWall.appendChild(card);
      } else {
        // Find column with minimum height
        let shortestCol = state.columnElements[0];
        let minHeight = shortestCol.offsetHeight;

        for (let c = 1; c < state.columnElements.length; c++) {
          const col = state.columnElements[c];
          if (col.offsetHeight < minHeight) {
            minHeight = col.offsetHeight;
            shortestCol = col;
          }
        }
        shortestCol.appendChild(card);
      }
    }

    state.renderedCount = endIndex;

    if (state.renderedCount < totalFiltered) {
      infiniteSentinel?.classList.remove('hidden');
    } else {
      infiniteSentinel?.classList.add('hidden');
    }
  }

  function createBloggerCardElement(user, idx) {
    const card = document.createElement('div');
    const isSuspended = user.is_suspended === 1;
    const isDeleted = user.is_suspended === 2;
    const isTombstone = isSuspended || isDeleted;

    card.className = `blogger-card ${isTombstone ? 'is-tombstone' : ''}`;
    card.setAttribute('role', 'article');
    card.setAttribute('tabindex', '0');
    card.style.animationDelay = `${Math.min(idx * 20, 250)}ms`;

    const rawAvatar = user.avatar_url || 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';
    const avatarSrc = resolveMediaUrl(rawAvatar);
    
    let rawCover = user.cover_url || '';
    if (rawCover && rawCover.includes('pbs.twimg.com/profile_banners') && !rawCover.match(/\/(600x200|1500x500|responsive_web)$/)) {
      rawCover = rawCover.replace(/\/+$/, '') + '/600x200';
    }
    const coverSrc = rawCover ? resolveMediaUrl(rawCover) : fallbackCovers[idx % fallbackCovers.length];

    const isTopTier = (user.followers_count >= 500000);
    const tierTag = isTopTier ? 'Top Creator' : 'Creator';
    const formattedBio = formatBioWithLinks(user.description);

    let statusBadgeHtml = '';
    if (isSuspended) {
      statusBadgeHtml = `<span class="badge-status-pill suspended" title="X 官方账号已被封禁/冻结，历史档案已永久冷备份">${ICONS.ghost} 已封号</span>`;
    } else if (isDeleted) {
      statusBadgeHtml = `<span class="badge-status-pill deleted" title="X 官方账号已注销或不存在，历史档案已永久冷备份">${ICONS.ghost} 已注销</span>`;
    }

    card.innerHTML = `
      <div class="card-ambient-glow"></div>
      <div class="card-header-banner">
        <img class="card-banner-img" src="${coverSrc}" alt="${escapeHtml(user.name)}" loading="lazy" decoding="async" onerror="handleMediaImgError(this, '${escapeHtml(rawCover)}', 'cover');">
        ${isTombstone ? '<div class="tombstone-banner-veil"></div>' : ''}
      </div>
      <div class="card-main-content">
        <div class="card-avatar-row">
          <div class="card-avatar-wrap">
            <img class="card-avatar-img" src="${avatarSrc}" alt="${escapeHtml(user.name)}" loading="lazy" decoding="async" onerror="handleMediaImgError(this, '${escapeHtml(rawAvatar)}', 'avatar');">
            ${user.verified ? `<div class="badge-verified-native" title="Twitter 官方认证">${ICONS.verifiedNative}</div>` : ''}
          </div>
        </div>

        <div class="card-user-info">
          <div class="card-name-row">
            <span class="card-user-name" title="${escapeHtml(user.name)}">${escapeHtml(user.name)}</span>
            <span class="card-influence-pill ${isTopTier ? 'top-tier' : ''}">${escapeHtml(tierTag)}</span>
            ${statusBadgeHtml}
          </div>
          <a class="card-user-handle" href="https://x.com/${user.screen_name}" target="_blank" onclick="event.stopPropagation(); window.trackBloggerClick('${escapeHtml(user.screen_name)}', 'card');">@${escapeHtml(user.screen_name)}</a>
          <div class="card-metrics-chip">
            ${ICONS.users}
            <span>${formatFollowers(user.followers_count)} 关注者</span>
          </div>
        </div>

        <div class="card-bio-content">${formattedBio}</div>
      </div>

      <div class="card-action-footer">
        <button class="btn-inspect-profile" type="button">
          ${ICONS.eye}
          <span>时光档案</span>
        </button>
        <a class="btn-visit-x" href="https://x.com/${user.screen_name}" target="_blank" onclick="event.stopPropagation(); window.trackBloggerClick('${escapeHtml(user.screen_name)}', 'card');">
          <span>${isTombstone ? '原主页' : '访问 X'}</span>
          ${ICONS.external}
        </a>
      </div>
    `;

    // Initialize deterministic vibrant palette immediately
    const initialRgb = isTombstone ? '148, 163, 184' : getFallbackAccent(user.screen_name || user.name);
    card.style.setProperty('--card-accent-rgb', initialRgb);
    card.style.setProperty('--card-accent', `rgb(${initialRgb})`);

    // Dynamic Ambient Color Refinement via Progressive CORS Probe (零裂图风险，真实像素精准自适应)
    if (!isTombstone && avatarSrc) {
      extractDominantColorWithProbe(avatarSrc, user.screen_name || user.name, (refinedRgb) => {
        card.style.setProperty('--card-accent-rgb', refinedRgb);
        card.style.setProperty('--card-accent', `rgb(${refinedRgb})`);
      });
    }

    attachSpotlightEffect(card);

    card.addEventListener('click', () => openInspectorDrawer(user));
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') openInspectorDrawer(user);
    });

    return card;
  }

  // Infinite Scroll Listener
  window.addEventListener('scroll', () => {
    if (state.isLoadingMore) return;
    if (state.renderedCount >= state.filteredUsers.length) return;

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 600) {
      state.isLoadingMore = true;
      setTimeout(() => {
        renderMoreCards();
        state.isLoadingMore = false;
      }, 150);
    }
  });

  // ==================== 9. Frameless Slot Machine Decelerating Random Roulette Modal ====================
  function startRandomRouletteShuffle() {
    if (state.rawUsers.length === 0) {
      showToast('归档库中暂无博主数据，请先同步或载入样例数据');
      return;
    }

    if (state.isShuffling) return;
    state.isShuffling = true;

    // Open center frameless modal
    rouletteBackdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    // Hide actions during shuffle
    rouletteOutsideActions?.classList.remove('is-visible');
    rouletteDismissHint?.classList.remove('is-visible');

    rouletteCardContainer.classList.remove('is-settled');
    rouletteCardContainer.classList.add('is-shuffling');

    // 过滤掉已封号 (is_suspended = 1) 和已注销 (is_suspended = 2) 的博主，确保只抽取正常活跃的博主
    const activeUsers = state.rawUsers.filter(u => !u.is_suspended || u.is_suspended === 0);
    const pool = activeUsers.length > 0 ? activeUsers : state.rawUsers;
    
    // 30+ Frames Realistic Slot Machine Deceleration Curve:
    // Phase 1: High-speed dash (20 frames, ~28ms each, dazzling motion blur)
    // Phase 2: Deceleration braking (9 frames, physical brake stagger)
    const dashFrames = Array(20).fill(28);
    const brakingFrames = [45, 70, 110, 165, 240, 340, 470, 620, 800];
    const delays = [...dashFrames, ...brakingFrames];
    let stepIndex = 0;

    // Pick final target winner
    const winnerIndex = Math.floor(Math.random() * pool.length);
    const winnerUser = pool[winnerIndex];

    function nextShuffleStep() {
      const tempUser = pool[Math.floor(Math.random() * pool.length)];
      renderRouletteCardPreview(tempUser, false);

      if (stepIndex < delays.length) {
        const delay = delays[stepIndex];
        stepIndex++;
        setTimeout(nextShuffleStep, delay);
      } else {
        finalizeRouletteWinner(winnerUser);
      }
    }

    nextShuffleStep();
  }

  function renderRouletteCardPreview(user, isFinal) {
    const rawAvatar = user.avatar_url || 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';
    const avatarSrc = resolveMediaUrl(rawAvatar);
    let rawCover = user.cover_url || fallbackCovers[0];
    if (rawCover.includes('pbs.twimg.com/profile_banners') && !rawCover.match(/\/(600x200|1500x500|responsive_web)$/)) {
      rawCover = rawCover.replace(/\/+$/, '') + '/600x200';
    }
    const coverSrc = resolveMediaUrl(rawCover);

    const isTopTier = (user.followers_count >= 500000);
    const tierTag = isTopTier ? 'Top Creator' : 'Creator';

    rouletteBanner.style.backgroundImage = `url('${coverSrc}')`;
    rouletteAvatar.src = avatarSrc;
    rouletteTag.className = `card-influence-pill ${isTopTier ? 'top-tier' : ''}`;
    rouletteTag.textContent = tierTag;
    rouletteName.textContent = user.name;
    rouletteVerified.style.display = user.verified ? 'flex' : 'none';
    rouletteHandle.textContent = `@${user.screen_name} · ${formatFollowers(user.followers_count)} 关注者`;
    rouletteBio.innerHTML = formatBioWithLinks(user.description);
    btnRouletteVisit.href = `https://x.com/${user.screen_name}`;
    btnRouletteVisit.onclick = () => window.trackBloggerClick(user.screen_name, 'roulette');
  }

  function finalizeRouletteWinner(user) {
    // 1. 倒数第二张卡片顺着滚轮惯性向上平滑滚出 (140ms)
    rouletteCardContainer.classList.add('is-rolling-out');

    setTimeout(() => {
      // 2. 注入获胜博主数据
      renderRouletteCardPreview(user, true);

      // 3. 移除滚出状态，触发最终卡片从下方滑入 + 拟真弹性卡扣回弹落定 (Spring Bounce)
      rouletteCardContainer.classList.remove('is-rolling-out', 'is-shuffling');
      void rouletteCardContainer.offsetWidth; // 强制触发 CSS 关键帧重绘
      rouletteCardContainer.classList.add('is-settled');
      state.isShuffling = false;

      // 4. 触发金色粒子爆破与星芒礼花
      triggerLuxuryCelebrationFireworks(rouletteCardContainer);

      // 5. 平滑展现底部操作栏
      setTimeout(() => {
        rouletteOutsideActions?.classList.add('is-visible');
        rouletteDismissHint?.classList.add('is-visible');
      }, 160);

      showToast(`抽取命中：@${user.screen_name}`);
    }, 140);
  }

  function closeRouletteModal() {
    if (state.isShuffling) return;
    rouletteBackdrop.classList.add('hidden');
    document.body.style.overflow = '';
  }

  btnLuckyPick?.addEventListener('click', (e) => {
    triggerClickSpark(e, 10, 'var(--accent-spark)');
    startRandomRouletteShuffle();
  });

  btnReshuffleAgain?.addEventListener('click', (e) => {
    triggerClickSpark(e, 10, 'var(--accent-spark)');
    startRandomRouletteShuffle();
  });

  rouletteBackdrop?.addEventListener('click', (e) => {
    if (e.target === rouletteBackdrop) closeRouletteModal();
  });

  // ==================== 10. Inspector Detail Drawer (Polaroid Time Capsule & Mutation Timeline) ====================
  function openInspectorDrawer(user) {
    const rawAvatar = user.avatar_url || 'https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';
    const avatar = resolveMediaUrl(rawAvatar);
    const rawCover = user.cover_url || fallbackCovers[0];
    const cover = resolveMediaUrl(rawCover);
    const isTop = (user.followers_count >= 500000);
    const isSuspended = user.is_suspended === 1;
    const isDeleted = user.is_suspended === 2;
    const isTombstone = isSuspended || isDeleted;

    const archivedTime = user.backed_up_at ? new Date(user.backed_up_at) : new Date();
    const archiveDateStr = !isNaN(archivedTime.getTime()) ? archivedTime.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : '已收录';
    const daysSinceArchive = !isNaN(archivedTime.getTime()) ? Math.max(1, Math.floor((Date.now() - archivedTime.getTime()) / (1000 * 60 * 60 * 24))) : 1;
    const vaultNo = 'VAULT-' + String(user.id || user.screen_name).slice(-5).toUpperCase().padStart(5, '0');

    let memorialNotice = '';
    if (isSuspended) {
      memorialNotice = `
        <div class="memorial-banner">
          <div class="memorial-banner-header">
            ${ICONS.ghost}
            <span><strong>赛博坟场 · 信号沉寂</strong></span>
          </div>
          <p>该博主 X 官方账号已被封禁/冻结。本档案馆已永久冷固化其最后的历史头像、背景及简介资产。</p>
          <div class="memorial-actions">
            <button class="btn-send-candle" id="btn-send-candle" type="button">
              ${ICONS.candle}
              <span>为 TA 点亮一盏微光</span>
            </button>
          </div>
        </div>
      `;
    } else if (isDeleted) {
      memorialNotice = `
        <div class="memorial-banner deleted">
          <div class="memorial-banner-header">
            ${ICONS.ghost}
            <span><strong>赛博坟场 · 账号注销</strong></span>
          </div>
          <p>该博主 X 官方账号已注销或不存在。历史数据已在此永久留档存续。</p>
          <div class="memorial-actions">
            <button class="btn-send-candle" id="btn-send-candle" type="button">
              ${ICONS.candle}
              <span>为 TA 点亮一盏微光</span>
            </button>
          </div>
        </div>
      `;
    }

    drawerBody.innerHTML = `
      <div class="polaroid-capsule-card ${isTombstone ? 'is-tombstone' : ''}">
        <!-- Top Full-Bleed Polaroid Header Banner -->
        <div class="polaroid-header-wrap">
          <div class="polaroid-banner-img" style="background-image: url('${cover}');">
            <div class="polaroid-banner-scrim"></div>
          </div>
          <div class="polaroid-stamp">
            <div class="stamp-border">
              <span class="stamp-title">ARCHIVE CERTIFIED</span>
              <span class="stamp-id">${vaultNo}</span>
              <span class="stamp-date">${archiveDateStr}</span>
            </div>
          </div>
        </div>

        <!-- Floating Avatar & Tags Row -->
        <div class="polaroid-profile-row">
          <div class="polaroid-avatar-wrap">
            <img class="polaroid-avatar-img" src="${avatar}" alt="${escapeHtml(user.name)}" onerror="this.src='https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png';">
            ${user.verified ? `<div class="badge-verified-native" title="Twitter 官方认证">${ICONS.verifiedNative}</div>` : ''}
          </div>
          <div class="polaroid-tags-group">
            ${isSuspended ? `<span class="badge-status-pill suspended">${ICONS.ghost} 已封号</span>` : ''}
            ${isDeleted ? `<span class="badge-status-pill deleted">${ICONS.ghost} 已注销</span>` : ''}
            <span class="card-influence-pill ${isTop ? 'top-tier' : ''}">${isTop ? 'Top 头部创作者' : '精选创作者'}</span>
          </div>
        </div>

        <!-- Identity & Handle -->
        <div class="polaroid-name-block">
          <h2 id="drawer-user-name" class="polaroid-user-name">${escapeHtml(user.name)}</h2>
          <div class="polaroid-handle-row">
            <span class="polaroid-handle-text">@${escapeHtml(user.screen_name)}</span>
            <button id="btn-copy-handle" class="btn-chip-copy" title="复制 @ID">
              ${ICONS.copy}
              <span>复制 ID</span>
            </button>
          </div>
        </div>

        ${memorialNotice}

        <!-- 4-Cell Time Capsule Metric Grid -->
        <div class="polaroid-metric-grid">
          <div class="metric-cell">
            <div class="metric-val">${formatFollowers(user.followers_count)}</div>
            <div class="metric-lbl">关注者 (粉丝)</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val ${user.verified ? 'is-verified' : ''}">${user.verified ? '官方认证' : '普通用户'}</div>
            <div class="metric-lbl">蓝标状态</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val">${archiveDateStr}</div>
            <div class="metric-lbl">首次归档日</div>
          </div>
          <div class="metric-cell">
            <div class="metric-val highlight">${daysSinceArchive} 天</div>
            <div class="metric-lbl">已留存时光</div>
          </div>
        </div>

        <!-- Full Bio Section -->
        <div class="polaroid-bio-section">
          <div class="section-title-tag">博主简介 (Bio)</div>
          <div class="polaroid-bio-card">
            ${formatBioWithLinks(user.description)}
          </div>
        </div>

        <!-- Mutation Timeline Collapsible Section -->
        <details class="polaroid-history-accordion" id="drawer-history-details">
          <summary class="polaroid-history-summary">
            <div class="summary-left">
              ${ICONS.history}
              <span>变迁履历档案 (Profile Timeline)</span>
            </div>
            <div class="summary-arrow">${ICONS.chevronDown}</div>
          </summary>
          <div class="polaroid-history-content" id="drawer-history-list">
            <div class="timeline-loading-spinner">
              <div class="skeleton-spinner"></div>
              <span>正在调取时光变迁档案...</span>
            </div>
          </div>
        </details>

        <!-- Action Footer -->
        <div class="polaroid-actions-row">
          <a class="btn-drawer-primary" href="https://x.com/${user.screen_name}" target="_blank" onclick="window.trackBloggerClick('${escapeHtml(user.screen_name)}', 'timeline');">
            <span>${isTombstone ? '前往 X 查看原账号' : '前往 X 个人主页'}</span>
            ${ICONS.external}
          </a>
          <button class="btn-drawer-secondary" id="btn-copy-markdown" type="button" title="一键复制 Markdown 档案卡">
            ${ICONS.markdown}
            <span>复制 Markdown</span>
          </button>
        </div>
      </div>
    `;

    // Initialize drawer ambient tint immediately
    const initialDrawerRgb = isTombstone ? '148, 163, 184' : getFallbackAccent(user.screen_name || user.name);
    drawerBody.style.setProperty('--card-accent-rgb', initialDrawerRgb);
    drawerBody.style.setProperty('--card-accent', `rgb(${initialDrawerRgb})`);

    const drawerAvatarImg = drawerBody.querySelector('.polaroid-avatar-img');
    if (drawerAvatarImg && !isTombstone) {
      const isSameOrigin = drawerAvatarImg.src && drawerAvatarImg.src.startsWith(window.location.origin);
      if (isSameOrigin) {
        const applyDrawerColor = () => {
          const rgb = extractDominantColor(drawerAvatarImg, user.screen_name);
          drawerBody.style.setProperty('--card-accent-rgb', rgb);
          drawerBody.style.setProperty('--card-accent', `rgb(${rgb})`);
        };
        if (drawerAvatarImg.complete && drawerAvatarImg.naturalWidth !== 0) {
          applyDrawerColor();
        } else {
          drawerAvatarImg.addEventListener('load', applyDrawerColor, { once: true });
        }
      }
    }

    // Copy Handle Handler
    document.getElementById('btn-copy-handle')?.addEventListener('click', (e) => {
      triggerClickSpark(e, 8, 'var(--card-accent)');
      navigator.clipboard.writeText(`@${user.screen_name}`);
      showToast(`已复制 @${user.screen_name} 到剪贴板`);
    });

    // Copy Markdown Card Handler
    document.getElementById('btn-copy-markdown')?.addEventListener('click', (e) => {
      triggerClickSpark(e, 10, 'var(--card-accent)');
      const mdContent = `### ${user.name} (@${user.screen_name})\n\n- **粉丝数**：${formatFollowers(user.followers_count)}\n- **认证状态**：${user.verified ? '已蓝标认证' : '未认证'}\n- **归档编号**：${vaultNo}\n- **首次收录**：${archiveDateStr}\n- **已留存**：${daysSinceArchive} 天\n- **个人简介**：${user.description || '暂无简介'}\n- **主页链接**：https://x.com/${user.screen_name}`;
      navigator.clipboard.writeText(mdContent);
      showToast('已复制博主 Markdown 档案卡到剪贴板');
    });

    // Send Candle / Memorial Spark Handler
    document.getElementById('btn-send-candle')?.addEventListener('click', (e) => {
      triggerLuxuryCelebrationFireworks(e.currentTarget);
      showToast(`已为 @${user.screen_name} 点亮一盏赛博微光`);
    });

    // Mutation Timeline Lazy Loader
    const historyDetails = document.getElementById('drawer-history-details');
    const historyList = document.getElementById('drawer-history-list');
    let historyLoaded = false;

    historyDetails?.addEventListener('toggle', async () => {
      if (!historyDetails.open || historyLoaded) return;
      historyLoaded = true;

      try {
        const res = await fetch(`/api/history?id=${encodeURIComponent(user.id || '')}&screen_name=${encodeURIComponent(user.screen_name || '')}`);
        const json = await res.json();
        if (json.success && Array.isArray(json.data) && json.data.length > 0) {
          const validHistory = [];
          for (const item of json.data) {
            const prev = validHistory[validHistory.length - 1];
            if (prev && prev.field === item.field && prev.new_value === item.new_value && prev.old_value === item.old_value) {
              continue;
            }
            validHistory.push(item);
          }
          historyList.innerHTML = validHistory.map(item => {
            const dateStr = item.changed_at ? new Date(item.changed_at).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : '记录时间';
            let fieldLabel = '字段更新';
            if (item.field === 'name') fieldLabel = '博主昵称变迁';
            else if (item.field === 'avatar_url') fieldLabel = '头像变迁更新';
            else if (item.field === 'cover_url') fieldLabel = 'Banner 背景图更换';
            else if (item.field === 'description') fieldLabel = '个人简介 (Bio) 修改';
            else if (item.field === 'screen_name') fieldLabel = 'Handle @ID 更名';
            else if (item.field === 'is_suspended') fieldLabel = '账号状态异动 (封禁/注销)';

            return `
              <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-type">${escapeHtml(fieldLabel)}</span>
                    <span class="timeline-date">${escapeHtml(dateStr)}</span>
                  </div>
                  <div class="timeline-diff">
                    ${item.old_value ? `<div class="diff-line diff-del"><span class="diff-tag">- 旧</span> ${escapeHtml(item.old_value)}</div>` : ''}
                    ${item.new_value ? `<div class="diff-line diff-add"><span class="diff-tag">+ 新</span> ${escapeHtml(item.new_value)}</div>` : ''}
                  </div>
                </div>
              </div>
            `;
          }).join('');
        } else {
          // If no history in D1 yet, show initial archive creation event
          const initialDate = user.backed_up_at ? new Date(user.backed_up_at).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : '首次归档';
          historyList.innerHTML = `
            <div class="timeline-item">
              <div class="timeline-dot active"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-type">创世归档入库</span>
                  <span class="timeline-date">${escapeHtml(initialDate)}</span>
                </div>
                <div class="timeline-desc">博主档案首次被收录至女菩萨精选画廊，媒体资产与档案快照已永久冷固化。</div>
              </div>
            </div>
            <div class="timeline-empty-hint">暂无后续改名或头像更迭记录（同步引擎将在博主资料变更时自动捕获快照）</div>
          `;
        }
      } catch (e) {
        const initialDate = user.backed_up_at ? new Date(user.backed_up_at).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : '首次归档';
        const daysAgo = user.backed_up_at ? Math.max(1, Math.floor((Date.now() - new Date(user.backed_up_at).getTime()) / (1000 * 3600 * 24))) : 1;
        historyList.innerHTML = `
          <div class="timeline-item">
            <div class="timeline-dot active"></div>
            <div class="timeline-content">
              <div class="timeline-header">
                <span class="timeline-type">创世归档入库</span>
                <span class="timeline-date">${escapeHtml(initialDate)}</span>
              </div>
              <div class="timeline-desc">博主档案已收录至精选画廊，已在安全归档库中留存 ${daysAgo} 天。媒体资产与资料快照已永久冷固化。</div>
            </div>
          </div>
          <div class="timeline-empty-hint">当前处于静态容灾模式，详细变迁履历档案将在服务配额重置后自动恢复。</div>
        `;
      }
    });

    inspectorBackdrop.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  }

  function closeInspectorDrawer() {
    inspectorBackdrop.classList.add('hidden');
    document.body.style.overflow = '';
  }

  drawerCloseBtn?.addEventListener('click', closeInspectorDrawer);
  inspectorBackdrop?.addEventListener('click', (e) => {
    if (e.target === inspectorBackdrop) closeInspectorDrawer();
  });

  // ==================== 11. Toast Notification System ====================
  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-item';
    toast.innerHTML = `
      <span style="color: var(--accent-primary); display: flex; align-items: center;">${ICONS.verifiedNative}</span>
      <span>${escapeHtml(message)}</span>
    `;

    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.2s ease';
      setTimeout(() => toast.remove(), 220);
    }, 2400);
  }

  // ==================== 12. Utilities ====================
  function formatBioWithLinks(text) {
    if (!text) return '暂无个人简介';
    let safe = escapeHtml(text);
    const urlRegex = /(https?:\/\/[^\s<]+)/g;
    return safe.replace(urlRegex, (url) => {
      return `<a href="${url}" target="_blank" onclick="event.stopPropagation();">${url} ↗</a>`;
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, (m) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;'
    })[m]);
  }

  // ==================== 13. Global Keyboard Shortcuts ====================
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== globalSearch) {
      e.preventDefault();
      globalSearch.focus();
    }
    if (e.key === 'Escape') {
      if (!rouletteBackdrop.classList.contains('hidden')) {
        closeRouletteModal();
      } else if (!inspectorBackdrop.classList.contains('hidden')) {
        closeInspectorDrawer();
      } else if (document.activeElement === globalSearch) {
        globalSearch.blur();
      }
    }
    if ((e.key === 'r' || e.key === 'R') && document.activeElement !== globalSearch) {
      e.preventDefault();
      startRandomRouletteShuffle();
    }
    if (document.activeElement !== globalSearch) {
      if (e.key === '1') document.querySelector('[data-view="grid"]')?.click();
      if (e.key === '2') document.querySelector('[data-view="compact"]')?.click();
      if (e.key === '3') document.querySelector('[data-view="list"]')?.click();
      if (e.key === 't' || e.key === 'T') {
        const nextTheme = state.currentTheme === 'oled' ? 'light' : 'oled';
        applyTheme(nextTheme);
        showToast(`已切换至 ${nextTheme === 'light' ? '清爽浅色' : '纯黑极简 (OLED)'} 模式`);
      }
      if (e.key === 'Home') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }
  });

  // ==================== 14. Back to Top Floating Interactive Button ====================
  const btnBackToTop = document.getElementById('btn-back-to-top');
  if (btnBackToTop) {
    let isScrollTicking = false;
    const SCROLL_THRESHOLD = 400; // 滚动超过 400px 时显现

    window.addEventListener('scroll', () => {
      if (!isScrollTicking) {
        window.requestAnimationFrame(() => {
          if (window.scrollY > SCROLL_THRESHOLD) {
            btnBackToTop.classList.add('is-visible');
          } else {
            btnBackToTop.classList.remove('is-visible');
          }
          isScrollTicking = false;
        });
        isScrollTicking = true;
      }
    }, { passive: true });

    btnBackToTop.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }

  // Start initialization
  initArchiveData();

});
