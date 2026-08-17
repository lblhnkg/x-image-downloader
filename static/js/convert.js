/**
 * convert.js — M3U8 → MP4 转换引擎 v3.4 (修复 mux.js 数据传递)
 * 修复：onSegment 中传入 data 而非 data.buffer，避免 subarray 错误
 */

// ============================================================
//  工具函数
// ============================================================

export function loadScript(src, globalKey, timeoutMs = 30000) {
  return new Promise((resolve, reject) => {
    if (globalKey && window[globalKey]) { resolve(window[globalKey]); return; }
    const s = document.createElement('script');
    s.src = src;
    s.async = true;
    s.crossOrigin = 'anonymous';
    let settled = false;
    const timer = setTimeout(() => {
      if (!settled) { settled = true; reject(new Error(`脚本加载超时(${timeoutMs}ms): ${src}`)); }
    }, timeoutMs);
    s.onload = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (globalKey && !window[globalKey]) {
        reject(new Error(`脚本已加载但全局变量 ${globalKey} 未定义: ${src}`));
        return;
      }
      resolve(globalKey ? window[globalKey] : true);
    };
    s.onerror = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      reject(new Error(`脚本加载失败(网络/CORS): ${src}`));
    };
    document.head.appendChild(s);
  });
}

function safeJsonParse(text, fallback) {
  try { return JSON.parse(text); } catch { return fallback; }
}

// ============================================================
//  M3U8 获取与解析
// ============================================================

export async function fetchM3U8(source, signal) {
  if (typeof source === 'string') {
    if (source.startsWith('http')) {
      const resp = await fetch(source, { signal });
      if (!resp.ok) throw new Error(
        `HTTP ${resp.status} — 无法获取 M3U8 文件。\n` +
        `解决方案：\n` +
        `  1. 检查 URL 是否可访问（浏览器直接打开试试）\n` +
        `  2. 用 Safari 打开（原生 HLS 不受 CORS 限制）\n` +
        `  3. 部分链接有时效性，重新获取最新地址`
      );
      const content = await resp.text();
      let baseUrl = '';
      if (!source.includes('/proxy/m3u8')) {
        baseUrl = source.substring(0, source.lastIndexOf('/') + 1);
      }
      return { content, baseUrl };
    }
    return { content: source, baseUrl: '' };
  }
  if (source instanceof File) {
    const content = await source.text();
    return { content, baseUrl: '' };
  }
  throw new Error('无效的 M3U8 来源类型（需 URL 字符串 / File 对象 / M3U8 文本）');
}

export function parseM3U8(content, baseUrl = '') {
  const lines = content.split('\n').map(l => l.trim());
  const manifest = {
    version: 3,
    duration: 0,
    segments: [],
    videoCodec: 'unknown',
    audioCodec: 'unknown',
    resolution: '-',
    bandwidth: '-',
    encrypted: false,
    encryptionType: null,
    isLive: !content.includes('#EXT-X-ENDLIST'),
    keyMethod: null,
    keyUri: null,
    iv: null,
    streams: [],
    isMaster: false,
    selectedStream: 0,
    initSegment: null,
    baseUrl: baseUrl,
    mediaSequence: 0,
  };

  let currentDuration = 0;
  let mediaSeq = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line) continue;

    if (line.startsWith('#EXT-X-VERSION:')) {
      manifest.version = parseInt(line.split(':')[1], 10) || 3;
    } else if (line.startsWith('#EXT-X-MEDIA-SEQUENCE:')) {
      mediaSeq = parseInt(line.split(':')[1], 10) || 0;
      manifest.mediaSequence = mediaSeq;
    } else if (line.startsWith('#EXTINF:')) {
      const m = line.match(/#EXTINF:([\d.]+)/);
      if (m) currentDuration = parseFloat(m[1]);
    } else if (line.startsWith('#EXT-X-KEY:')) {
      manifest.encrypted = true;
      manifest.keyInfo = line;
      const methodM = line.match(/METHOD=([^,]+)/);
      const uriM = line.match(/URI=["']?([^"'\s,]+)["']?/);
      const ivM = line.match(/IV=0x([^,]+)/i);
      manifest.keyMethod = methodM ? methodM[1] : 'NONE';
      manifest.keyUri = uriM ? uriM[1] : null;
      manifest.iv = ivM ? ivM[1] : null;
      manifest.encryptionType = manifest.keyMethod;
      if (manifest.keyMethod !== 'NONE' && !manifest.keyUri) {
        throw new Error(`加密流声明了 ${manifest.keyMethod} 方法，但缺少密钥 URI。\n解决方案：在转换设置中手动提供 32 位十六进制密钥。`);
      }
    } else if (line.startsWith('#EXT-X-STREAM-INF:')) {
      manifest.isMaster = true;
      const stream = { bandwidth: 0, resolution: '-', codecs: '', url: '', videoCodec: 'unknown', audioCodec: 'unknown' };
      const bwM = line.match(/BANDWIDTH=(\d+)/);
      if (bwM) stream.bandwidth = parseInt(bwM[1], 10);
      const resM = line.match(/RESOLUTION=(\d+x\d+)/);
      if (resM) stream.resolution = resM[1];
      const ccM = line.match(/CODECS="([^"]+)"/);
      if (ccM) {
        stream.codecs = ccM[1];
        ccM[1].split(',').forEach(c => {
          if (/avc|h264/i.test(c)) stream.videoCodec = 'H.264';
          else if (/hev|h265/i.test(c)) stream.videoCodec = 'H.265';
          else if (/av1/i.test(c)) stream.videoCodec = 'AV1';
          else if (/aac/i.test(c)) stream.audioCodec = 'AAC';
          else if (/mp3/i.test(c)) stream.audioCodec = 'MP3';
          else if (/ac-3/i.test(c)) stream.audioCodec = 'AC-3';
        });
      }
      if (i + 1 < lines.length && !lines[i + 1].startsWith('#')) {
        stream.url = lines[i + 1];
        if (!stream.url.startsWith('http') && baseUrl) stream.url = baseUrl + stream.url;
        i++;
      }
      manifest.streams.push(stream);
    } else if (line.startsWith('#EXT-X-MAP:')) {
      const uriM = line.match(/URI="([^"]+)"/);
      if (uriM) {
        let mapUrl = uriM[1];
        if (!mapUrl.startsWith('http') && baseUrl) mapUrl = baseUrl + mapUrl;
        manifest.initSegment = mapUrl;
      }
    } else if (line.startsWith('#EXT-X-SESSION-KEY:')) {
      const methodM = line.match(/METHOD=([^,]+)/);
      const uriM = line.match(/URI="([^"]+)"/);
      if (methodM) manifest.keyMethod = methodM[1];
      if (uriM) manifest.keyUri = uriM[1];
      manifest.encrypted = true;
    } else if (!line.startsWith('#')) {
      let segUrl = line;
      if (!segUrl.startsWith('http') && baseUrl) {
        segUrl = baseUrl + segUrl;
      }
      manifest.segments.push({ url: segUrl, duration: currentDuration });
      manifest.duration += currentDuration;
      currentDuration = 0;
    }
  }

  if (!manifest.isMaster && manifest.videoCodec === 'unknown' && manifest.segments.length > 0) {
    const u = manifest.segments[0].url;
    if (u.includes('.ts')) manifest.videoCodec = 'H.264 (推测)';
    else if (u.includes('.m4s') || u.includes('.cmfv')) manifest.videoCodec = 'H.264 (fMP4)';
  }

  return manifest;
}

// ============================================================
//  AES-128 解密（Web Crypto API）
// ============================================================

export function parseUserKey(userKeyInput) {
  if (!userKeyInput || typeof userKeyInput !== 'string') {
    throw new Error('密钥不能为空');
  }
  const trimmed = userKeyInput.trim();
  if (!/^[0-9a-fA-F]{32}$/.test(trimmed)) {
    throw new Error(
      `密钥格式无效。\n` +
      `要求：32 位十六进制字符（0-9, A-F），区分大小写，不含空格或其他字符。\n` +
      `当前输入长度：${trimmed.length}（应为 32）\n` +
      `示例有效密钥：1a2b3c4d5e6f7081a2b3c4d5e6f7081`
    );
  }
  const bytes = new Uint8Array(16);
  for (let i = 0; i < 16; i++) {
    bytes[i] = parseInt(trimmed.substr(i * 2, 2), 16);
  }
  return bytes;
}

export async function fetchDecryptionKey(keyUri, baseUrl = '', signal) {
  let fullUri = keyUri;
  if (!fullUri.startsWith('http') && baseUrl) fullUri = baseUrl + fullUri;

  const resp = await fetch(fullUri, { signal });
  if (!resp.ok) {
    throw new Error(
      `无法获取解密密钥 (HTTP ${resp.status})。\n` +
      `密钥 URI: ${fullUri}\n` +
      `解决方案：\n` +
      `  1. 确认你有权访问此视频内容\n` +
      `  2. 在"转换设置"中手动输入 32 位十六进制密钥\n` +
      `  3. 部分付费视频的密钥服务器会校验 Referer/Cookie`
    );
  }
  const keyBuffer = await resp.arrayBuffer();
  if (keyBuffer.byteLength !== 16) {
    throw new Error(`密钥长度异常：期望 16 字节，实际 ${keyBuffer.byteLength} 字节`);
  }
  return new Uint8Array(keyBuffer);
}

export async function decryptAES128(encryptedData, keyBytes, ivBytes) {
  const cryptoKey = await crypto.subtle.importKey(
    'raw', keyBytes.buffer, { name: 'AES-CBC' }, false, ['decrypt']
  );
  let iv = ivBytes;
  if (!iv || iv.length !== 16) iv = new Uint8Array(16);
  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-CBC', iv: iv.buffer.slice(iv.byteOffset, iv.byteOffset + 16) },
    cryptoKey,
    encryptedData.buffer.slice(encryptedData.byteOffset, encryptedData.byteOffset + encryptedData.byteLength)
  );
  return new Uint8Array(decrypted);
}

export function parseIV(ivHex, segmentIndex = 0) {
  if (ivHex) {
    const clean = ivHex.replace(/^0x/, '');
    if (!/^[0-9a-fA-F]{16}$|^[0-9a-fA-F]{32}$/.test(clean)) {
      throw new Error(`IV 格式无效："${ivHex}"。必须是 16 或 32 位十六进制字符（可带 0x 前缀）。`);
    }
    const bytes = new Uint8Array(16);
    const len = clean.length / 2;
    for (let i = 0; i < len; i++) {
      bytes[i] = parseInt(clean.substr(i * 2, 2), 16);
    }
    if (len < 16) {
      const shifted = new Uint8Array(16);
      shifted.set(bytes.subarray(0, len), 16 - len);
      return shifted;
    }
    return bytes;
  }
  const bytes = new Uint8Array(16);
  const dv = new DataView(bytes.buffer);
  dv.setUint32(12, segmentIndex, false);
  return bytes;
}

// ============================================================
//  分片下载（并发 + 流式回调 + AbortController）
// ============================================================

export async function downloadSegments(segments, options = {}) {
  const {
    concurrency = 3,
    decrypt: decryptInfo = null,
    signal = null,
    onProgress,
    onLog,
    onSegment,
  } = options;

  const log = (msg, level) => onLog?.(msg, level);

  if (signal && signal.aborted) throw new DOMException('下载已取消', 'AbortError');

  // 检测是否启用代理
  const useProxy = window.__useProxy === true;

  const results = new Array(segments.length);
  let done = 0;
  let failed = 0;
  let corsSeen = false;

  let nextIndex = 0;
  const getNext = () => {
    if (nextIndex >= segments.length) return -1;
    return nextIndex++;
  };

  async function fetchOne(idx) {
    const seg = segments[idx];
    const maxRetries = 3;
    let lastError = null;

    let targetUrl = seg.url;
    if (useProxy && targetUrl.startsWith('http')) {
      targetUrl = `/proxy/ts?url=${encodeURIComponent(targetUrl)}`;
      console.log('[调试] 代理分片:', targetUrl);
    } else {
      console.log('[调试] 直连分片:', targetUrl);
    }

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        if (signal && signal.aborted) throw new DOMException('下载已取消', 'AbortError');

        const resp = await fetch(targetUrl, { signal });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

        let data = new Uint8Array(await resp.arrayBuffer());

        if (decryptInfo && decryptInfo.key) {
          const iv = decryptInfo.iv || parseIV(decryptInfo.ivHex, idx);
          data = await decryptAES128(data, decryptInfo.key, iv);
        }

        results[idx] = data;
        done++;
        onProgress?.(done, segments.length, seg.url);
        onSegment?.(idx, data);
        return;
      } catch (e) {
        lastError = e;
        const isCors = e.name === 'TypeError' || /CORS|cross-origin|NetworkError/i.test(e.message);

        if (isCors && !corsSeen) {
          corsSeen = true;
          log('CORS 跨域错误！浏览器阻止了分片请求。', 'error');
          log('解决方案 1：启用代理（勾选"使用后端代理"）', 'info');
          log('解决方案 2：用 Safari 打开（原生 HLS 不受 CORS 限制）', 'info');
          log('解决方案 3：将分片下载到本地后上传', 'info');
        }

        if (attempt < maxRetries - 1) {
          await new Promise(r => setTimeout(r, 500 * Math.pow(2, attempt)));
        }
      }
    }

    failed++;
    done++;
    log(`分片 ${idx} 最终失败: ${lastError?.message || '未知错误'}`, 'warn');
    results[idx] = null;
    onProgress?.(done, segments.length, seg.url);
  }

  const workers = Array.from({ length: concurrency }, async () => {
    while (true) {
      if (signal && signal.aborted) break;
      const idx = getNext();
      if (idx === -1) break;
      await fetchOne(idx);
    }
  });

  await Promise.all(workers);

  const successCount = results.filter(Boolean).length;
  log(
    `下载完成：${successCount}/${segments.length} 成功${failed > 0 ? `，${failed} 个失败` : ''}`,
    failed > 0 ? 'warn' : 'success'
  );

  if (successCount === 0) {
    throw new Error(
      `所有分片下载失败。\n` +
      `常见原因：\n` +
      `  1. CORS 跨域限制（最常见）—— 启用代理或使用 Safari\n` +
      `  2. URL 已过期 —— 重新获取 M3U8 链接\n` +
      `  3. 需要 Referer/Cookie 鉴权 —— 在浏览器中先登录再试`
    );
  }

  return results;
}

// ============================================================
//  模式 1: Remux（mux.js 流式封装）
// ============================================================

export async function convertRemux(segments, options = {}) {
  const { onProgress, onLog, decrypt: decryptInfo = null, signal = null } = options;
  const log = (msg, level) => onLog?.(msg, level);

  if (signal && signal.aborted) throw new DOMException('已取消', 'AbortError');

  log('加载 mux.js...', 'debug');
  await loadScript('https://cdn.jsdelivr.net/npm/mux.js@6.2.0/dist/mux.js', 'muxjs');
  log('mux.js 就绪', 'success');

  const outputSegments = [];

  const muxer = new muxjs.mp4.Transmuxer({
    remux: true,
    keepOriginalTimestamps: true,
  });

  muxer.on('data', (data) => {
    if (data.data && data.data.byteLength > 0) {
      outputSegments.push(new Uint8Array(data.data));
    }
  });

  muxer.on('done', () => {
    log('mux.js 内部管线完成', 'debug');
  });

  await downloadSegments(segments, {
    concurrency: 3,
    decrypt: decryptInfo,
    signal,
    onProgress: (done, total) => {
      const pct = (done / total) * 0.85;
      onProgress?.(pct, `下载并封装 ${done}/${total}`);
    },
    onLog: log,
    onSegment: (idx, data) => {
      try {
        // 【修复】直接传入 data（Uint8Array），而非 data.buffer（ArrayBuffer）
        muxer.push(data);
      } catch (e) {
        log(`分片 ${idx} mux 失败: ${e.message}`, 'warn');
      }
    },
  });

  log('正在完成 MP4 封装...', 'info');
  onProgress?.(0.9, 'Finalizing MP4...');
  muxer.flush();

  if (outputSegments.length === 0) {
    throw new Error(
      'mux.js 未输出任何 MP4 数据。\n' +
      '可能原因：\n' +
      '  1. 分片全部下载失败（检查 CORS）\n' +
      '  2. 源编码不受支持（仅 H.264 + AAC 可纯 remux）\n' +
      '  3. 加密流密钥错误'
    );
  }

  const totalLen = outputSegments.reduce((s, b) => s + b.byteLength, 0);
  const result = new Uint8Array(totalLen);
  let off = 0;
  for (const seg of outputSegments) { result.set(seg, off); off += seg.byteLength; }
  outputSegments.length = 0;

  onProgress?.(1.0, '完成');
  log(`MP4 封装完成: ${(totalLen / 1024 / 1024).toFixed(2)} MB`, 'success');

  return new Blob([result], { type: 'video/mp4' });
}

// ============================================================
//  模式 2: WebCodecs GPU 转码（完整管线）
// ============================================================

export async function convertWebCodecs(segments, manifest, options = {}) {
  const { onProgress, onLog, decrypt: decryptInfo = null, signal = null } = options;
  const log = (msg, level) => onLog?.(msg, level);

  if (signal && signal.aborted) throw new DOMException('已取消', 'AbortError');

  if (!window.VideoDecoder || !window.VideoEncoder) {
    throw new Error(
      `当前浏览器不支持 WebCodecs API（缺少 VideoDecoder 或 VideoEncoder）。\n` +
      `需要：Chrome 94+ / Edge 94+ / Safari 26+ / Firefox 130+\n` +
      `当前 UA: ${navigator.userAgent}`
    );
  }

  const hasAudioDecoder = !!window.AudioDecoder;
  if (!hasAudioDecoder) {
    log('AudioDecoder 不可用（Safari < 26 常见），将跳过音频转码', 'warn');
  }

  log('WebCodecs GPU 转码管线启动', 'success');
  log(`源编码: ${manifest.videoCodec}`, 'info');
  if (decryptInfo?.key) log('AES-128 解密已启用', 'info');

  let useMediabunny = false;
  try {
    await loadScript('https://cdn.jsdelivr.net/npm/@mediabunny/core@1/dist/mediabunny.min.js', 'Mediabunny', 15000);
    if (window.Mediabunny && window.Mediabunny.HLSParser && window.Mediabunny.Mp4Muxer) {
      useMediabunny = true;
      log('Mediabunny 加载成功 — 使用完整管线', 'success');
    } else {
      throw new Error('Mediabunny 全局对象不完整');
    }
  } catch (e) {
    log(`Mediabunny 不可用 (${e.message})，回退到 remux 模式`, 'warn');
    return convertRemux(segments, { onProgress, onLog, decrypt: decryptInfo, signal });
  }

  if (useMediabunny) {
    return convertWithMediabunny(window.Mediabunny, segments, manifest, { onProgress, onLog, decrypt: decryptInfo, signal });
  }
}

async function convertWithMediabunny(Mediabunny, segments, manifest, options) {
  const { onProgress, onLog, decrypt, signal } = options;
  const log = (msg, level) => onLog?.(msg, level);

  const { HLSParser, Mp4Muxer } = Mediabunny;

  const total = segments.length;
  log(`开始下载 ${total} 个分片（并发 3）...`, 'info');

  const segResults = await downloadSegments(segments, {
    concurrency: 3,
    decrypt,
    signal,
    onProgress: (done, tot) => onProgress?.(done / tot * 0.4, `下载 ${done}/${tot}`),
    onLog: (msg, level) => log(msg, level),
  });

  const validBuffers = segResults.filter(Boolean);
  log(`下载完成: ${validBuffers.length}/${total}`, 'success');

  if (validBuffers.length === 0) {
    throw new Error('所有分片下载失败，无法继续转码。请检查 CORS 或网络连接。');
  }

  const totalLen = validBuffers.reduce((s, b) => s + b.length, 0);
  const combined = new Uint8Array(totalLen);
  let off = 0;
  validBuffers.forEach(b => { combined.set(b, off); off += b.length; });
  validBuffers.length = 0;

  onProgress?.(0.45, '初始化 GPU 解码器...');

  const isH265 = /H\.265|HEVC|hev1|hvc1/i.test(manifest.videoCodec);
  const decoderCodec = isH265 ? 'hev1.1.6.L93.B0' : 'avc1.640028';

  let width = 1920, height = 1080;
  const resM = String(manifest.resolution).match(/(\d+)x(\d+)/);
  if (resM) { width = parseInt(resM[1], 10); height = parseInt(resM[2], 10); }

  const decodedFrames = [];
  let decoderError = null;

  const decoder = new VideoDecoder({
    output: (frame) => { decodedFrames.push(frame); },
    error: (e) => { decoderError = e; log(`VideoDecoder 错误: ${e.message}`, 'error'); },
  });

  try {
    decoder.configure({
      codec: decoderCodec,
      codedWidth: width,
      codedHeight: height,
      optimizeForLatency: false,
    });
    log(`VideoDecoder 配置: ${decoderCodec} @ ${width}x${height}`, 'success');
  } catch (e) {
    throw new Error(`解码器配置失败: ${e.message}\n可能原因：浏览器不支持 ${isH265 ? 'H.265' : 'H.264'} 的 WebCodecs 解码`);
  }

  onProgress?.(0.5, 'Mediabunny 解析 HLS...');

  let encodedChunks = [];

  try {
    const parser = new HLSParser();
    if (typeof parser.feed === 'function') {
      if (typeof parser.on === 'function') {
        parser.on('segment', (segData) => { encodedChunks.push(segData); });
      }
      parser.feed(combined.buffer);
      if (encodedChunks.length === 0 && parser.segments) {
        encodedChunks = Array.from(parser.segments);
      }
      if (encodedChunks.length === 0 && typeof parser[Symbol.iterator] === 'function') {
        for (const item of parser) encodedChunks.push(item);
      }
    }
    log(`Mediabunny 解析出 ${encodedChunks.length} 个编码单元`, 'info');
  } catch (e) {
    throw new Error(
      `Mediabunny HLSParser 解析失败: ${e.message}\n` +
      `可能原因：\n` +
      `  1. Mediabunny API 版本不兼容（当前使用 @mediabunny/core@1）\n` +
      `  2. TS 流格式不标准\n` +
      `  3. 加密流密钥错误导致数据无法解析\n` +
      `建议：切换到 remux 模式（mux.js），或检查源编码格式。`
    );
  }

  if (encodedChunks.length === 0) {
    throw new Error(
      'Mediabunny 未能从流中提取任何编码数据。\n' +
      '可能原因：\n' +
      '  1. 源是 fMP4 格式（非 TS），Mediabunny 1.x 的 HLSParser 主要处理 TS\n' +
      '  2. 流已加密但密钥错误\n' +
      '建议：改用 remux 模式，或使用 Safari 原生播放后截图/录屏。'
    );
  }

  combined.fill(0);

  onProgress?.(0.55, 'GPU 解码中...');

  for (let i = 0; i < encodedChunks.length; i++) {
    if (signal && signal.aborted) {
      decoder.close();
      throw new DOMException('已取消', 'AbortError');
    }
    try {
      const chunkData = encodedChunks[i];
      const chunk = new EncodedVideoChunk({
        type: i === 0 ? 'key' : 'delta',
        timestamp: i * 33333,
        duration: 33333,
        data: chunkData.buffer || chunkData,
      });
      decoder.decode(chunk);
    } catch (e) {}
    if (i % 50 === 0) {
      onProgress?.(0.55 + (i / encodedChunks.length) * 0.2, `解码 ${i}/${encodedChunks.length}`);
    }
  }

  encodedChunks.length = 0;

  await decoder.flush();
  await decoder.close();
  if (decoderError) {
    throw new Error(`解码过程中发生错误: ${decoderError.message}`);
  }
  log(`GPU 解码完成: ${decodedFrames.length} 帧`, 'success');

  if (decodedFrames.length === 0) {
    throw new Error(
      '解码后无有效帧输出。\n' +
      '可能原因：\n' +
      '  1. 源编码不受支持（仅 H.264 / H.265 可用 WebCodecs 解码）\n' +
      '  2. 加密密钥错误导致数据损坏\n' +
      '  3. 分辨率/编码参数超出浏览器限制'
    );
  }

  onProgress?.(0.8, 'GPU 编码 H.264 中...');

  const muxer = new Mp4Muxer({
    fastStart: true,
    videoCodec: 'avc',
    audioCodec: 'aac',
  });

  let encoderError = null;
  const encoder = new VideoEncoder({
    output: (chunk) => { muxer.addVideoChunk(chunk); },
    error: (e) => { encoderError = e; log(`VideoEncoder 错误: ${e.message}`, 'error'); },
  });

  const targetBitrate = Math.min(width * height * 0.15, 5_000_000);
  try {
    encoder.configure({
      codec: 'avc1.640028',
      width,
      height,
      bitrate: targetBitrate,
      framerate: 30,
    });
  } catch (e) {
    throw new Error(`编码器配置失败: ${e.message}`);
  }

  for (let i = 0; i < decodedFrames.length; i++) {
    if (signal && signal.aborted) {
      encoder.close();
      decodedFrames.forEach(f => { try { f.close(); } catch {} });
      throw new DOMException('已取消', 'AbortError');
    }
    const frame = decodedFrames[i];
    try {
      encoder.encode(frame, { keyFrame: i % 30 === 0 });
    } catch (e) {}
    frame.close();

    if (i % 50 === 0) {
      onProgress?.(0.8 + (i / decodedFrames.length) * 0.15, `编码 ${i}/${decodedFrames.length}`);
    }
  }

  decodedFrames.length = 0;

  await encoder.flush();
  await encoder.close();
  if (encoderError) {
    throw new Error(`编码过程中发生错误: ${encoderError.message}`);
  }

  onProgress?.(0.97, '封装 MP4...');
  const mp4Data = muxer.finalize();
  onProgress?.(1.0, '完成');

  const blob = new Blob([mp4Data], { type: 'video/mp4' });
  log(`转码完成: ${(mp4Data.byteLength / 1024 / 1024).toFixed(2)} MB`, 'success');
  return blob;
}

// ============================================================
//  模式 3: 自动选择
// ============================================================

export async function convertAuto(segments, manifest, options = {}) {
  const { onLog } = options;
  const log = (msg, level) => onLog?.(msg, level);

  const hasWebCodecs = !!(window.VideoDecoder && window.VideoEncoder);

  if (manifest.encrypted && !options.decrypt?.key) {
    throw new Error(
      `检测到加密流（${manifest.keyMethod || 'AES-128'}），需要解密密钥才能处理。\n` +
      `请在"转换设置"中提供 32 位十六进制密钥，或确认密钥 URI 可访问。`
    );
  }

  const codec = String(manifest.videoCodec || '');
  if (codec.includes('H.264') || codec.includes('推测')) {
    log('Auto: H.264 源 → 使用 remux（最快，零质量损失）', 'info');
    return convertRemux(segments, options);
  }

  if ((codec.includes('H.265') || codec.includes('HEVC') || codec.includes('AV1')) && hasWebCodecs) {
    log('Auto: H.265/AV1 源 + WebCodecs 可用 → GPU 转码', 'info');
    return convertWebCodecs(segments, manifest, options);
  }

  if ((codec.includes('H.265') || codec.includes('HEVC') || codec.includes('AV1')) && !hasWebCodecs) {
    throw new Error(
      `${codec} 源需要 WebCodecs GPU 转码，但当前浏览器不支持。\n` +
      `需要：Chrome 94+ / Edge 94+ / Safari 26+ / Firefox 130+\n` +
      `当前 UA: ${navigator.userAgent}`
    );
  }

  log(`Auto: 未知编码 "${codec}" → 尝试 remux`, 'warn');
  return convertRemux(segments, options);
}

// ============================================================
//  统一入口
// ============================================================

export async function convert(m3u8Source, mode = 'auto', callbacks = {}, decryptOpts = null, signal = null) {
  const { onLog } = callbacks;
  const log = (msg, level) => onLog?.(msg, level);

  if (signal && signal.aborted) throw new DOMException('已取消', 'AbortError');

  const { content, baseUrl } = await fetchM3U8(m3u8Source, signal);
  const manifest = parseM3U8(content, baseUrl);

  log(
    `解析完成: ${manifest.segments.length} 分片, ${manifest.duration.toFixed(1)}s, ${manifest.videoCodec}, ${manifest.isLive ? 'LIVE' : 'VOD'}` +
    (manifest.encrypted ? `, 加密(${manifest.keyMethod})` : ''),
    'success'
  );

  if (manifest.isMaster) {
    log(`检测到 Master Playlist，共 ${manifest.streams.length} 条子流`, 'info');
    const sorted = [...manifest.streams].sort((a, b) => b.bandwidth - a.bandwidth);
    const best = sorted[0];
    log(`自动选择最高码率: ${best.resolution} (${Math.round(best.bandwidth / 1000)} kbps, ${best.videoCodec})`, 'info');
    const subResp = await fetch(best.url, { signal });
    if (!subResp.ok) throw new Error(`子流获取失败 HTTP ${subResp.status}`);
    const subContent = await subResp.text();
    const subBaseUrl = best.url.substring(0, best.url.lastIndexOf('/') + 1);
    const subManifest = parseM3U8(subContent, subBaseUrl);
    Object.assign(manifest, subManifest);
    log(`子流解析: ${manifest.segments.length} 分片, ${manifest.videoCodec}`, 'info');
  }

  let decryptInfo = null;
  if (manifest.encrypted) {
    if (decryptOpts?.key) {
      decryptInfo = {
        key: decryptOpts.key,
        iv: decryptOpts.iv || null,
        ivHex: decryptOpts.ivHex || manifest.iv || null,
      };
      log('使用用户提供的密钥', 'success');
    } else if (decryptOpts?.keyInput) {
      const keyBytes = parseUserKey(decryptOpts.keyInput);
      decryptInfo = {
        key: keyBytes,
        iv: null,
        ivHex: decryptOpts.ivHex || manifest.iv || null,
      };
      log('用户密钥解析成功', 'success');
    } else if (manifest.keyUri) {
      log('正在从 URI 获取解密密钥...', 'info');
      try {
        const key = await fetchDecryptionKey(manifest.keyUri, baseUrl, signal);
        decryptInfo = {
          key,
          iv: null,
          ivHex: manifest.iv || null,
        };
        log('密钥获取成功', 'success');
      } catch (e) {
        log(e.message, 'error');
        throw new Error(
          `${e.message}\n\n` +
          `你也可以手动提供密钥：在转换设置中输入 32 位十六进制密钥。`
        );
      }
    } else {
      throw new Error(
        `检测到加密流（${manifest.keyMethod || 'AES-128'}），但无法获取密钥。\n` +
        `原因：\n` +
        `  1. 未提供密钥 URI\n` +
        `  2. 未手动输入密钥\n` +
        `解决方案：在"转换设置"面板中输入 32 位十六进制密钥。`
      );
    }
  }

  if (manifest.isLive) {
    log('检测到直播流（LIVE）。直播流可以播放但下载可能不完整。', 'warn');
  }

  const opts = { ...callbacks, decrypt: decryptInfo, signal };

  switch (mode) {
    case 'remux':    return convertRemux(manifest.segments, opts);
    case 'transcode': return convertWebCodecs(segments, manifest, opts);
    case 'auto':
    default:          return convertAuto(manifest.segments, manifest, opts);
  }
}

export function detectBrowser() {
  const ua = navigator.userAgent || '';
  const vendor = navigator.vendor || '';
  const video = document.createElement('video');
  const canPlayHLS = video.canPlayType('application/vnd.apple.mpegurl');
  const supportsNativeHLS = canPlayHLS === 'probably' || canPlayHLS === 'maybe';
  const looksLikeSafari = /safari/i.test(ua) && !/chrome|chromium|edge|edg/i.test(ua);
  const isSafari = looksLikeSafari && /apple/i.test(vendor) && supportsNativeHLS;
  const hasVideoDecoder = typeof window.VideoDecoder === 'function';
  const hasVideoEncoder = typeof window.VideoEncoder === 'function';
  const hasAudioDecoder = typeof window.AudioDecoder === 'function';
  const hasAudioEncoder = typeof window.AudioEncoder === 'function';
  const hasWebCodecsFull = hasVideoDecoder && hasVideoEncoder && hasAudioDecoder && hasAudioEncoder;
  const hasWebCodecsPartial = hasVideoDecoder && hasVideoEncoder;

  return {
    ua, vendor, isSafari, supportsNativeHLS,
    isChrome: /chrome|chromium/i.test(ua) && !/edge|edg/i.test(ua),
    isEdge: /edge|edg/i.test(ua),
    isFirefox: /firefox/i.test(ua),
    hasVideoDecoder, hasVideoEncoder, hasAudioDecoder, hasAudioEncoder,
    hasWebCodecsFull, hasWebCodecsPartial,
  };
}
