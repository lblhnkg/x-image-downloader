<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, viewport-fit=cover">
    <title>X 媒体下载器</title>
    <script src="https://cdn.jsdelivr.net/npm/@hotwired/turbo@7.3.0/dist/turbo.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@1.5.13/dist/hls.min.js">
    </script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0a0a;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
            min-height: 100vh;
            padding: 20px;
            padding-bottom: 80px;
        }

        .hidden {
            display: none !important;
        }

        .app-container {
            width: 100%;
            max-width: 480px;
            margin: 0 auto;
            background: linear-gradient(145deg, #141414 0%, #1a1a1a 100%);
            border-radius: 32px;
            padding: 40px 28px 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
            min-height: 560px;
            position: relative;
            transition: all 0.3s ease;
        }

        @media (min-width: 700px) {
            .app-container {
                max-width: 900px;
                padding: 50px 40px 40px;
                border-radius: 36px;
            }
            .gallery {
                grid-template-columns: repeat(4, 1fr) !important;
                gap: 14px;
            }
            .search-row input {
                font-size: 18px;
            }
            .option-btn {
                padding: 8px 18px;
                font-size: 13px;
            }
            .submenu-grid {
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 14px;
            }
            .submenu-card {
                padding: 24px 20px;
                min-height: 100px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
        }

        @media (min-width: 1024px) {
            .app-container {
                max-width: 1100px;
                padding: 60px 50px 50px;
                border-radius: 40px;
            }
            .gallery {
                grid-template-columns: repeat(4, 1fr) !important;
                gap: 18px;
            }
            .submenu-card {
                padding: 28px 24px;
                min-height: 110px;
            }
            .submenu-card-title {
                font-size: 18px;
            }
        }

        @media (max-width: 420px) {
            .app-container {
                padding: 28px 18px 22px;
                border-radius: 24px;
            }
            .gallery {
                gap: 6px;
            }
            .item-actions button {
                font-size: 9px;
                padding: 4px 0;
            }
            .submenu-card {
                padding: 14px 16px;
            }
            .submenu-card-title {
                font-size: 15px;
            }
        }

        @media (max-width: 360px) {
            .app-container {
                padding: 20px 12px 16px;
                border-radius: 20px;
            }
            .item-actions button {
                font-size: 8px;
                padding: 3px 0;
            }
        }

        .page {
            display: none;
            animation: fadeIn 0.4s ease;
        }

        .page.active {
            display: block;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(6px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .back-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 22px;
            cursor: pointer;
            color: rgba(255, 255, 255, 0.5);
            font-size: 15px;
            transition: color 0.2s ease;
            font-weight: 400;
            letter-spacing: 0.2px;
            padding: 4px 0;
        }

        .back-row:hover {
            color: rgba(255, 255, 255, 0.8);
        }

        .back-row .back-icon {
            font-size: 18px;
            line-height: 1;
        }

        .back-home {
            display: inline-block;
            color: rgba(255, 255, 255, 0.4);
            font-size: 14px;
            text-decoration: none;
            margin-bottom: 18px;
            transition: color 0.2s ease;
            cursor: pointer;
        }

        .back-home:hover {
            color: rgba(255, 255, 255, 0.7);
        }

        .submenu-title {
            font-size: 20px;
            font-weight: 500;
            color: #fff;
            margin-bottom: 6px;
            letter-spacing: -0.3px;
        }

        .submenu-desc {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.3);
            margin-bottom: 18px;
            font-weight: 300;
        }

        .submenu-grid {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .submenu-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 14px;
            padding: 18px 20px;
            cursor: pointer;
            transition: all 0.25s ease;
        }

        .submenu-card:hover {
            background: rgba(255, 255, 255, 0.07);
            border-color: rgba(255, 255, 255, 0.12);
        }

        .submenu-card:active {
            transform: scale(0.98);
        }

        .submenu-card-title {
            font-size: 16px;
            font-weight: 450;
            color: #fff;
        }

        .submenu-card-desc {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.3);
            margin-top: 2px;
            font-weight: 300;
        }

        .mode-banner {
            background: rgba(255, 215, 0, 0.08);
            border: 1px solid rgba(255, 215, 0, 0.15);
            border-radius: 8px;
            padding: 8px 14px;
            margin-bottom: 16px;
            font-size: 12px;
            color: rgba(255, 215, 0, 0.6);
            text-align: center;
            font-weight: 300;
            transition: background 0.3s, color 0.3s, border-color 0.3s;
        }

        .mode-banner.developer {
            background: rgba(0, 200, 255, 0.06);
            border-color: rgba(0, 200, 255, 0.1);
            color: rgba(0, 200, 255, 0.5);
        }

        .search-section {
            margin-top: 6px;
        }

        .search-label {
            font-size: 13px;
            color: rgba(255, 255, 255, 0.4);
            font-weight: 300;
            margin-bottom: 6px;
            display: block;
        }

        .search-row {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        .search-row input {
            flex: 1;
            background: transparent;
            border: 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.12);
            padding: 10px 0 8px;
            font-size: 16px;
            color: #fff;
            outline: none;
            transition: border-color 0.25s ease;
            font-family: inherit;
        }

        .search-row input::placeholder {
            color: rgba(255, 255, 255, 0.25);
            font-weight: 300;
            font-size: 14px;
        }

        .search-row input:focus {
            border-bottom-color: rgba(255, 255, 255, 0.5);
        }

        .search-row .search-btn-icon {
            background: transparent;
            border: 0;
            color: rgba(255, 255, 255, 0.4);
            font-size: 20px;
            cursor: pointer;
            padding: 6px 4px 6px 10px;
            transition: color 0.2s ease;
        }

        .search-row .search-btn-icon:hover {
            color: rgba(255, 255, 255, 0.7);
        }

        .search-favorite-btn {
            background: transparent;
            border: 0;
            color: rgba(255, 255, 255, 0.3);
            font-size: 14px;
            cursor: pointer;
            padding: 6px 4px 6px 6px;
            transition: color 0.2s ease;
            white-space: nowrap;
            font-family: inherit;
        }

        .search-favorite-btn:hover {
            color: rgba(255, 255, 255, 0.6);
        }

        .search-favorite-btn.favorited {
            color: #ffd700;
        }

        .favorites-panel {
            margin-top: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.02);
        }

        .favorite-empty {
            padding: 16px 14px;
            color: rgba(255, 255, 255, 0.25);
            font-size: 13px;
            font-weight: 300;
            text-align: center;
        }

        .favorite-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }

        .favorite-item:last-child {
            border-bottom: 0;
        }

        .favorite-item .fav-info {
            flex: 1;
            min-width: 0;
        }

        .favorite-item .fav-name {
            font-size: 14px;
            color: #fff;
            font-weight: 400;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .favorite-item .fav-handle {
            font-size: 11px;
            color: rgba(255, 255, 255, 0.3);
            margin-top: 1px;
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .favorite-item .fav-handle:hover {
            color: rgba(255, 255, 255, 0.7);
        }

        .favorite-item .fav-actions {
            display: flex;
            gap: 6px;
        }

        .favorite-item .fav-actions button {
            background: transparent;
            border: 0;
            color: rgba(255, 255, 255, 0.3);
            font-size: 12px;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 6px;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        .favorite-item .fav-actions .fav-use {
            color: rgba(255, 255, 255, 0.6);
        }

        .favorite-item .fav-actions .fav-use:hover {
            color: #fff;
            background: rgba(255, 255, 255, 0.08);
        }

        .favorite-item .fav-actions .fav-delete:hover {
            color: #ff6b6b;
            background: rgba(255, 107, 107, 0.08);
        }

        .favorite-toggle-btn {
            width: 100%;
            background: transparent;
            border: 0;
            color: rgba(255, 255, 255, 0.3);
            font-size: 13px;
            font-weight: 300;
            padding: 10px 0 6px;
            cursor: pointer;
            text-align: left;
            font-family: inherit;
            transition: color 0.2s ease;
        }

        .favorite-toggle-btn:hover {
            color: rgba(255, 255, 255, 0.5);
        }

        .option-section {
            margin-top: 18px;
        }

        .option-label {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.3);
            font-weight: 300;
            margin-bottom: 8px;
            display: block;
        }

        .option-row {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }

        .option-btn {
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.4);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
            font-weight: 300;
        }

        .option-btn:hover {
            border-color: rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.6);
        }

        .option-btn.active {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.2);
            color: #fff;
        }

        .date-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 8px;
        }

        .date-row input[type="date"] {
            background: transparent;
            border: 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 8px 0 6px;
            font-size: 14px;
            color: rgba(255, 255, 255, 0.6);
            outline: none;
            font-family: inherit;
            transition: border-color 0.25s ease;
        }

        .date-row input[type="date"]:focus {
            border-bottom-color: rgba(255, 255, 255, 0.4);
        }

        .date-row input[type="date"]::-webkit-calendar-picker-indicator {
            filter: invert(0.6);
        }

        .primary-btn {
            width: 100%;
            padding: 14px 0;
            background: #fff;
            color: #0a0a0a;
            border: 0;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: inherit;
            margin-top: 18px;
        }

        .primary-btn:hover {
            opacity: 0.85;
            transform: scale(0.98);
        }

        .primary-btn:active {
            transform: scale(0.96);
        }

        .primary-btn:disabled {
            opacity: 0.3;
            cursor: default;
            transform: none;
        }

        .status-box {
            margin-top: 14px;
            padding: 12px 14px;
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.04);
            font-size: 13px;
            color: rgba(255, 255, 255, 0.5);
            font-weight: 300;
            line-height: 1.6;
            min-height: 20px;
        }

        .status-box.error {
            color: #ff6b6b;
            border-color: rgba(255, 107, 107, 0.15);
            background: rgba(255, 107, 107, 0.04);
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 18px;
            margin-bottom: 12px;
        }

        .result-title {
            font-size: 15px;
            font-weight: 450;
            color: #fff;
        }

        .result-count {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.25);
            font-weight: 300;
        }

        .gallery {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .gallery.fade-in {
            animation: fadeIn 0.35s ease;
        }

        .item {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.04);
            position: relative;
            transition: all 0.2s ease;
        }

        .item.selected {
            border-color: #007aff;
            background: rgba(0, 122, 255, 0.08);
        }

        .select-check {
            position: absolute;
            top: 8px;
            left: 8px;
            z-index: 10;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.5);
            background: rgba(0, 0, 0, 0.5);
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: #fff;
            transition: all 0.2s ease;
            pointer-events: none;
        }

        .item.in-select-mode .select-check {
            display: flex;
        }

        .item.selected .select-check {
            background: #007aff;
            border-color: #007aff;
        }

        .item.selected .select-check::after {
            content: "✓";
            font-weight: 600;
        }

        .media-wrap {
            position: relative;
            width: 100%;
            background: rgba(255, 255, 255, 0.03);
            overflow: hidden;
        }

        .media-wrap img {
            display: block;
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            cursor: pointer;
        }

        .item.in-select-mode .media-wrap img {
            cursor: default;
            pointer-events: none;
        }

        .media-error {
            width: 100%;
            aspect-ratio: 1 / 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.03);
            color: rgba(255, 255, 255, 0.2);
            font-size: 12px;
            text-align: center;
            padding: 12px;
            font-weight: 300;
        }

        .video-badge {
            position: absolute;
            left: 8px;
            top: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 400;
            letter-spacing: 0.3px;
        }

        .source-badge {
            position: absolute;
            right: 8px;
            top: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: rgba(255, 255, 255, 0.7);
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 300;
            letter-spacing: 0.3px;
        }

        .library-badge {
            position: absolute;
            right: 8px;
            top: 8px;
            background: rgba(0, 0, 0, 0.7);
            color: rgba(255, 255, 255, 0.7);
            border-radius: 12px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 300;
            letter-spacing: 0.3px;
        }

        .item-info {
            padding: 8px 10px;
        }

        .item-author {
            font-size: 11px;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.5);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .item-author:hover {
            color: rgba(255, 255, 255, 0.8);
        }

        .item-date {
            font-size: 10px;
            color: rgba(255, 255, 255, 0.2);
            margin-top: 2px;
            font-weight: 300;
        }

        .item-actions {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 4px;
            margin-top: 6px;
        }

        .item-actions button {
            padding: 5px 0;
            border-radius: 6px;
            font-size: 10px;
            cursor: pointer;
            font-family: inherit;
            border: 0;
            transition: all 0.2s ease;
            pointer-events: auto;
        }

        .item.in-select-mode .item-actions button {
            pointer-events: none;
            opacity: 0.25;
        }

        .item-actions .btn-view {
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.4);
        }

        .item-actions .btn-view:hover {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.7);
        }

        .item-actions .btn-download {
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.4);
        }

        .item-actions .btn-download:hover {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.7);
        }

        .item-actions .btn-original {
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.4);
        }

        .item-actions .btn-original:hover {
            background: rgba(255, 255, 255, 0.1);
            color: rgba(255, 255, 255, 0.7);
        }

        .selection-toolbar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 100;
            background: rgba(20, 20, 22, 0.92);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding: 12px 20px;
            padding-bottom: calc(12px + env(safe-area-inset-bottom));
            display: none;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }

        .selection-toolbar.active {
            display: flex;
        }

        .selection-toolbar .toolbar-left {
            display: flex;
            gap: 16px;
            align-items: center;
        }

        .selection-toolbar .toolbar-btn {
            background: transparent;
            border: 0;
            color: rgba(255, 255, 255, 0.6);
            font-size: 15px;
            font-weight: 450;
            padding: 8px 4px;
            cursor: pointer;
            font-family: inherit;
            transition: color 0.2s ease;
        }

        .selection-toolbar .toolbar-btn:hover {
            color: #fff;
        }

        .selection-toolbar .toolbar-btn.danger {
            background: #fff;
            color: #ff3b30;
            padding: 8px 20px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 15px;
        }

        .selection-toolbar .toolbar-btn.danger:hover {
            opacity: 0.85;
        }

        .selection-toolbar .toolbar-btn.danger:active {
            transform: scale(0.96);
        }

        .selection-toolbar .selected-count {
            color: rgba(255, 255, 255, 0.4);
            font-size: 13px;
            font-weight: 300;
        }

        .delete-confirm-overlay {
            position: fixed;
            inset: 0;
            z-index: 200;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .delete-confirm-overlay.active {
            display: flex;
        }

        .delete-confirm-box {
            background: #1c1c1e;
            border-radius: 14px;
            padding: 28px 24px 20px;
            max-width: 340px;
            width: 100%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
        }

        .delete-confirm-box .confirm-icon {
            font-size: 48px;
            margin-bottom: 12px;
            display: block;
            color: #ff3b30;
        }

        .delete-confirm-box .confirm-title {
            font-size: 18px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 6px;
        }

        .delete-confirm-box .confirm-desc {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.4);
            line-height: 1.5;
            margin-bottom: 20px;
            font-weight: 300;
        }

        .delete-confirm-box .confirm-actions {
            display: flex;
            gap: 8px;
        }

        .delete-confirm-box .confirm-actions button {
            flex: 1;
            padding: 12px 0;
            border: 0;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s ease;
        }

        .delete-confirm-box .confirm-actions .confirm-cancel {
            background: transparent;
            color: #007aff;
        }

        .delete-confirm-box .confirm-actions .confirm-cancel:hover {
            background: rgba(0, 122, 255, 0.1);
        }

        .delete-confirm-box .confirm-actions .confirm-delete {
            background: #fff;
            color: #ff3b30;
        }

        .delete-confirm-box .confirm-actions .confirm-delete:hover {
            opacity: 0.85;
        }

        .delete-confirm-box .confirm-actions .confirm-delete:active {
            transform: scale(0.96);
        }

        .modal-overlay {
            position: fixed;
            inset: 0;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.95);
            display: flex;
            flex-direction: column;
            padding: env(safe-area-inset-top) 0 env(safe-area-inset-bottom) 0;
        }

        .modal-overlay.hidden {
            display: none !important;
        }

        .modal-top {
            min-height: 54px;
            padding: 10px 16px 0;
            display: flex;
            align-items: center;
            justify-content: flex-end;
        }

        .modal-close {
            background: rgba(255, 255, 255, 0.08);
            border: 0;
            color: rgba(255, 255, 255, 0.5);
            border-radius: 16px;
            padding: 6px 14px;
            font-size: 13px;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s ease;
            font-weight: 300;
        }

        .modal-close:hover {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .modal-content {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px 16px;
            overflow: auto;
        }

        .modal-content img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }

        .modal-content video {
            max-width: 100%;
            max-height: 100%;
        }

        .modal-bottom {
            padding: 10px 16px 16px;
            display: flex;
            gap: 10px;
        }

        .modal-bottom button {
            flex: 1;
            padding: 12px 0;
            border: 0;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 450;
            cursor: pointer;
            font-family: inherit;
            transition: all 0.2s ease;
        }

        .modal-bottom .modal-download {
            background: #fff;
            color: #0a0a0a;
        }

        .modal-bottom .modal-download:hover {
            opacity: 0.85;
        }

        .modal-bottom .modal-original {
            background: rgba(255, 255, 255, 0.08);
            color: rgba(255, 255, 255, 0.6);
        }

        .modal-bottom .modal-original:hover {
            background: rgba(255, 255, 255, 0.15);
            color: #fff;
        }

        .dev-signature {
            text-align: center;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.15);
            margin-top: 32px;
            letter-spacing: 0.5px;
            font-weight: 300;
        }

        .library-placeholder {
            text-align: center;
            color: rgba(255, 255, 255, 0.3);
            padding: 40px 20px;
            font-size: 14px;
            font-weight: 300;
            line-height: 1.8;
        }

        .library-placeholder .icon {
            font-size: 48px;
            display: block;
            margin-bottom: 12px;
        }

        .loader {
            text-align: center;
            color: rgba(255, 255, 255, 0.2);
            padding: 30px 0;
            font-size: 13px;
            font-weight: 300;
        }
    </style>
</head>
<body>

    <div class="app-container">

        <!-- X 二级菜单 -->
        <div class="page active" id="pageXSub">
            <span class="back-home" id="backToHome">‹ 返回首页</span>
            <div id="xModeBanner" class="mode-banner" style="display:none;"></div>
            <div class="submenu-title">下载 X 上的媒体</div>
            <div class="submenu-desc">图片 · 视频 · 喜欢 · 书签</div>
            <div class="submenu-grid">
                <div class="submenu-card" id="subSearch">
                    <div class="submenu-card-title">搜索博主</div>
                    <div class="submenu-card-desc">输入用户名，搜索指定博主的媒体</div>
                </div>
                <div class="submenu-card" id="subLikes">
                    <div class="submenu-card-title">❤️ 我的喜欢</div>
                    <div class="submenu-card-desc">查看采集器上传的喜欢列表</div>
                </div>
                <div class="submenu-card" id="subBookmarks">
                    <div class="submenu-card-title">🔖 我的书签</div>
                    <div class="submenu-card-desc">查看采集器上传的书签列表</div>
                </div>
            </div>
            <div class="dev-signature">开发者：浮生若夢</div>
        </div>

        <!-- 搜索博主页 -->
        <div class="page" id="pageSearch">
            <div class="back-row" id="backFromSearch">
                <span class="back-icon">‹</span> <span id="backFromSearchText">返回</span>
            </div>
            <div class="submenu-title" id="searchPageTitle">搜索博主</div>
            <div class="submenu-desc" id="searchPageDesc">输入 X 用户名，搜索该博主的所有媒体</div>

            <!-- 搜索输入区域 -->
            <div class="search-section" id="searchInputArea">
                <label class="search-label">博主</label>
                <div class="search-row">
                    <input type="text" id="profileInput" placeholder="请输入博主用户名（X上@开头的字符串，可不带@）" autocomplete="off" autocapitalize="off" spellcheck="false">
                    <button class="search-btn-icon" id="searchBtn">⌕</button>
                    <button class="search-favorite-btn" id="favoriteAddBtn">☆ 收藏</button>
                </div>
                <div class="favorite-entry" style="margin-top:10px;">
                    <button class="favorite-toggle-btn" id="favoriteToggleBtn">我的收藏</button>
                    <div class="favorites-panel hidden" id="favoritesPanel"></div>
                </div>
            </div>

            <!-- 筛选条件 -->
            <div class="option-section">
                <span class="option-label">时间范围</span>
                <div class="option-row" data-group="range">
                    <button class="option-btn active" data-value="all">全部</button>
                    <button class="option-btn" data-value="7">最近7天</button>
                    <button class="option-btn" data-value="30">最近30天</button>
                    <button class="option-btn" data-value="365">最近1年</button>
                    <button class="option-btn" data-value="custom">自定义</button>
                </div>
            </div>
            <div class="hidden" id="customDates" style="margin-top:10px;">
                <div class="date-row">
                    <div><label class="search-label" style="font-size:11px;">开始日期</label><input type="date" id="startDate"></div>
                    <div><label class="search-label" style="font-size:11px;">结束日期</label><input type="date" id="endDate"></div>
                </div>
            </div>

            <div class="option-section">
                <span class="option-label">媒体类型</span>
                <div class="option-row" data-group="media">
                    <button class="option-btn active" data-value="all">全部</button>
                    <button class="option-btn" data-value="photo">图片</button>
                    <button class="option-btn" data-value="video">视频</button>
                </div>
            </div>

            <div class="option-section">
                <span class="option-label">帖子来源</span>
                <div class="option-row" data-group="source">
                    <button class="option-btn active" data-value="all">全部</button>
                    <button class="option-btn" data-value="original">原创</button>
                    <button class="option-btn" data-value="repost">转帖 / 引用</button>
                </div>
            </div>

            <button class="primary-btn" id="searchSubmitBtn">开始收集媒体</button>
            <div class="status-box hidden" id="searchStatus"></div>

            <div class="result-header hidden" id="searchResultHeader">
                <span class="result-title" id="searchResultTitle">搜索结果</span>
                <span class="result-count" id="searchResultCount"></span>
            </div>
            <div class="gallery" id="searchGallery"></div>

            <div class="dev-signature">开发者：浮生若夢</div>
        </div>

        <!-- 我的喜欢 / 我的书签 -->
        <div class="page" id="pageLibrary">
            <div class="back-row" id="backFromLibrary">
                <span class="back-icon">‹</span> 返回
            </div>
            <div id="libraryModeBanner"></div>
            <div class="submenu-title" id="libraryTitle">我的喜欢</div>
            <div class="submenu-desc" id="libraryDesc">查看采集器上传的喜欢列表</div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;margin-top:4px;flex-wrap:wrap;gap:6px;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <span style="font-size:12px;color:rgba(255,255,255,0.25);font-weight:300;" id="libraryCount">正在读取…</span>
                    <button style="background:transparent;border:0;color:rgba(255,255,255,0.2);font-size:12px;cursor:pointer;font-family:inherit;padding:4px 8px;border-radius:6px;transition:all 0.2s ease;" id="refreshLibraryBtn">刷新</button>
                </div>
                <div><button id="selectToggleBtn" style="background:transparent;border:0;color:rgba(255,255,255,0.4);font-size:13px;cursor:pointer;font-family:inherit;padding:4px 8px;border-radius:6px;transition:all 0.2s ease;">选择</button></div>
            </div>

            <div class="option-section" style="margin-top:0;">
                <span class="option-label">时间范围</span>
                <div class="option-row" data-group="libraryRange">
                    <button class="option-btn active" data-value="all">全部</button>
                    <button class="option-btn" data-value="7">最近7天</button>
                    <button class="option-btn" data-value="30">最近30天</button>
                    <button class="option-btn" data-value="365">最近1年</button>
                    <button class="option-btn" data-value="custom">自定义</button>
                </div>
            </div>
            <div class="hidden" id="libraryCustomDates" style="margin-top:8px;">
                <div class="date-row">
                    <div><label class="search-label" style="font-size:11px;">开始日期</label><input type="date" id="libraryStartDate"></div>
                    <div><label class="search-label" style="font-size:11px;">结束日期</label><input type="date" id="libraryEndDate"></div>
                </div>
            </div>

            <div class="option-section" style="margin-top:12px;">
                <span class="option-label">媒体类型</span>
                <div class="option-row" data-group="libraryMedia">
                    <button class="option-btn active" data-value="all">全部</button>
                    <button class="option-btn" data-value="image">图片</button>
                    <button class="option-btn" data-value="video">视频</button>
                </div>
            </div>

            <div class="status-box hidden" id="libraryStatus"></div>
            <div class="result-header hidden" id="libraryResultHeader">
                <span class="result-title" id="libraryResultTitle">媒体</span>
                <span class="result-count" id="libraryResultCount"></span>
            </div>
            <div class="gallery" id="libraryGallery"></div>
            <div class="dev-signature">开发者：浮生若夢</div>
        </div>

    </div>

    <!-- Modal -->
    <div class="modal-overlay hidden" id="modal">
        <div class="modal-top"><button class="modal-close" id="modalCloseBtn">关闭</button></div>
        <div class="modal-content" id="modalContent"></div>
        <div class="modal-bottom">
            <button class="modal-download" id="modalDownloadBtn">下载</button>
            <button class="modal-original" id="modalOriginalBtn">打开原帖</button>
        </div>
    </div>

    <!-- 选择工具栏 -->
    <div class="selection-toolbar" id="selectionToolbar">
        <div class="toolbar-left">
            <button class="toolbar-btn" id="toolbarCancel">取消</button>
            <button class="toolbar-btn" id="toolbarSelectAll">全选</button>
        </div>
        <div style="display:flex;align-items:center;gap:12px;">
            <span class="selected-count" id="selectedCount">已选 0 个</span>
            <button class="toolbar-btn danger" id="toolbarDelete">删除</button>
        </div>
    </div>

    <!-- 删除确认 -->
    <div class="delete-confirm-overlay" id="deleteConfirm">
        <div class="delete-confirm-box">
            <span class="confirm-icon">🗑️</span>
            <div class="confirm-title" id="confirmTitle">确定删除？</div>
            <div class="confirm-desc" id="confirmDesc">这些媒体将被永久删除，无法恢复。</div>
            <div class="confirm-actions">
                <button class="confirm-cancel" id="confirmCancel">取消</button>
                <button class="confirm-delete" id="confirmDelete">确定删除</button>
            </div>
        </div>
    </div>

    <script>
        // ============================================================
        // X 下载器 - 最终修复版
        // HLS 视频：新标签页打开（系统播放器）
        // MP4 视频：在 Modal 中播放（走代理）
        // 图片：在 Modal 中查看大图
        // ============================================================

        // ---- 状态 ----
        let currentMode = 'guest';
        let currentSubPage = '';
        let currentItem = null;
        let currentHls = null;

        let range = 'all';
        let mediaType = 'all';
        let sourceType = 'all';
        let libraryMediaType = 'all';
        let libraryRange = 'all';

        let favorites = [];
        let favoritesLoaded = false;

        let isSelectMode = false;
        let selectedIds = new Set();

        let isGalleryMode = false;
        let galleryUsername = '';
        let returnSource = '';

        const API_KEY = 'fushengruomeng';
        const FAVORITE_KEY = 'universal_downloader_favorites';

        let cachedLibraryItems = [];
        let cachedLibrarySource = '';
        let allFilteredItems = [];
        let currentBatch = 0;
        const BATCH_SIZE = 50;
        let isLoadingMore = false;
        let allLoaded = false;
        let scrollListenerAttached = false;

        // ---- DOM 引用 ----
        function $(id) { return document.getElementById(id); }

        var pageXSub = $('pageXSub');
        var pageSearch = $('pageSearch');
        var pageLibrary = $('pageLibrary');
        var backToHome = $('backToHome');
        var backFromSearch = $('backFromSearch');
        var backFromLibrary = $('backFromLibrary');
        var backFromSearchText = $('backFromSearchText');
        var searchPageTitle = $('searchPageTitle');
        var searchPageDesc = $('searchPageDesc');
        var xModeBanner = $('xModeBanner');
        var libraryModeBanner = $('libraryModeBanner');

        var subSearch = $('subSearch');
        var subLikes = $('subLikes');
        var subBookmarks = $('subBookmarks');

        var profileInput = $('profileInput');
        var searchBtn = $('searchBtn');
        var favoriteAddBtn = $('favoriteAddBtn');
        var favoriteToggleBtn = $('favoriteToggleBtn');
        var favoritesPanel = $('favoritesPanel');
        var searchSubmitBtn = $('searchSubmitBtn');
        var searchStatus = $('searchStatus');
        var searchResultHeader = $('searchResultHeader');
        var searchResultTitle = $('searchResultTitle');
        var searchResultCount = $('searchResultCount');
        var searchGallery = $('searchGallery');
        var searchInputArea = $('searchInputArea');

        var libraryTitle = $('libraryTitle');
        var libraryDesc = $('libraryDesc');
        var libraryCount = $('libraryCount');
        var refreshLibraryBtn = $('refreshLibraryBtn');
        var libraryStatus = $('libraryStatus');
        var libraryResultHeader = $('libraryResultHeader');
        var libraryResultTitle = $('libraryResultTitle');
        var libraryResultCount = $('libraryResultCount');
        var libraryGallery = $('libraryGallery');
        var selectToggleBtn = $('selectToggleBtn');

        var startDate = $('startDate');
        var endDate = $('endDate');
        var customDates = $('customDates');
        var libraryCustomDates = $('libraryCustomDates');
        var libraryStartDate = $('libraryStartDate');
        var libraryEndDate = $('libraryEndDate');

        var modal = $('modal');
        var modalContent = $('modalContent');
        var modalCloseBtn = $('modalCloseBtn');
        var modalDownloadBtn = $('modalDownloadBtn');
        var modalOriginalBtn = $('modalOriginalBtn');

        var selectionToolbar = $('selectionToolbar');
        var toolbarCancel = $('toolbarCancel');
        var toolbarSelectAll = $('toolbarSelectAll');
        var toolbarDelete = $('toolbarDelete');
        var selectedCount = $('selectedCount');
        var deleteConfirm = $('deleteConfirm');
        var confirmTitle = $('confirmTitle');
        var confirmDesc = $('confirmDesc');
        var confirmCancel = $('confirmCancel');
        var confirmDelete = $('confirmDelete');

        // ---- 页面切换 ----
        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(function(p) { p.classList.remove('active'); });
            var target = document.getElementById(pageId);
            if (target) target.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
            if (isSelectMode) exitSelectMode();
        }

        // ---- 模式横幅 ----
        function updateModeBanners() {
            if (currentMode === 'guest') {
                xModeBanner.textContent = '📌 访客模式 · 数据来自本地浏览器';
                xModeBanner.className = 'mode-banner';
                xModeBanner.style.display = 'block';
            } else {
                xModeBanner.textContent = '🔒 开发者模式 · 数据来自服务器';
                xModeBanner.className = 'mode-banner developer';
                xModeBanner.style.display = 'block';
            }
        }

        function updateLibraryBanner(mode) {
            var bannerHtml = '';
            if (mode === 'guest') {
                bannerHtml = '<div class="mode-banner">📌 访客模式 · 数据来自本地浏览器</div>';
            } else {
                bannerHtml = '<div class="mode-banner developer">🔒 开发者模式 · 数据来自服务器</div>';
            }
            libraryModeBanner.innerHTML = bannerHtml;
        }

        // ---- 收藏功能（访客模式修复） ----
        function loadFavorites() {
            if (currentMode === 'guest') {
                loadFavoritesFromLocal();
                return;
            }
            loadFavoritesFromServer();
        }

        function loadFavoritesFromServer() {
            fetch('/api/favorites', {
                headers: { 'X-API-Key': API_KEY },
                credentials: 'include'
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.ok && Array.isArray(data.items)) {
                    favorites = data.items;
                    favoritesLoaded = true;
                    localStorage.setItem(FAVORITE_KEY, JSON.stringify(favorites));
                    renderFavorites();
                    updateFavoriteButton();
                } else {
                    loadFavoritesFromLocal();
                }
            })
            .catch(function() { loadFavoritesFromLocal(); });
        }

        function loadFavoritesFromLocal() {
            try {
                var data = localStorage.getItem(FAVORITE_KEY);
                favorites = data ? JSON.parse(data) : [];
                favoritesLoaded = true;
                renderFavorites();
                updateFavoriteButton();
            } catch (e) {
                favorites = [];
            }
        }

        function renderFavorites() {
            favoritesPanel.innerHTML = '';
            if (!favorites || favorites.length === 0) {
                favoritesPanel.innerHTML = '<div class="favorite-empty">暂时没有收藏的博主</div>';
                return;
            }
            favorites.forEach(function(fav, index) {
                var div = document.createElement('div');
                div.className = 'favorite-item';
                div.innerHTML =
                    '<div class="fav-info"><div class="fav-name">' + (fav.name || fav.username) +
                    '</div><div class="fav-handle" data-username="' + fav.username + '">@' + fav.username +
                    '</div></div>' +
                    '<div class="fav-actions">' +
                    '<button class="fav-delete" data-index="' + index + '">删除</button>' +
                    '</div>';
                favoritesPanel.appendChild(div);
            });

            favoritesPanel.querySelectorAll('.fav-handle').forEach(function(el) {
                el.addEventListener('click', function() {
                    var username = el.dataset.username;
                    if (username) {
                        openGallery(username, null);
                    }
                });
            });

            favoritesPanel.querySelectorAll('.fav-delete').forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    var idx = parseInt(btn.dataset.index);
                    var fav = favorites[idx];
                    if (fav) {
                        removeFavorite(fav.username);
                    }
                });
            });
        }

        function updateFavoriteButton() {
            var username = normalizeUsername(profileInput.value);
            if (!username) {
                favoriteAddBtn.textContent = '☆ 收藏';
                favoriteAddBtn.classList.remove('favorited');
                return;
            }
            var exists = favorites.some(function(f) { return f.username.toLowerCase() === username.toLowerCase(); });
            favoriteAddBtn.textContent = exists ? '★ 已收藏' : '☆ 收藏';
            if (exists) {
                favoriteAddBtn.classList.add('favorited');
            } else {
                favoriteAddBtn.classList.remove('favorited');
            }
        }

        function bindFavoriteEvents() {
            var oldBtn = favoriteAddBtn;
            var newBtn = oldBtn.cloneNode(true);
            oldBtn.parentNode.replaceChild(newBtn, oldBtn);
            favoriteAddBtn = newBtn;

            favoriteAddBtn.addEventListener('click', function() {
                var username = normalizeUsername(profileInput.value);
                if (!username) {
                    showSearchStatus('请先输入博主名', 'error');
                    return;
                }
                var exists = favorites.some(function(f) { return f.username.toLowerCase() === username.toLowerCase(); });
                if (exists) {
                    removeFavorite(username);
                } else {
                    addFavorite(username);
                }
            });

            var oldToggle = favoriteToggleBtn;
            var newToggle = oldToggle.cloneNode(true);
            oldToggle.parentNode.replaceChild(newToggle, oldToggle);
            favoriteToggleBtn = newToggle;

            favoriteToggleBtn.addEventListener('click', function() {
                favoritesPanel.classList.toggle('hidden');
            });

            profileInput.removeEventListener('input', profileInput._inputHandler);
            profileInput._inputHandler = function() {
                updateFavoriteButton();
            };
            profileInput.addEventListener('input', profileInput._inputHandler);
        }

        function addFavorite(username) {
            if (currentMode === 'developer') {
                fetch('/api/favorites', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': API_KEY
                    },
                    body: JSON.stringify({ username: username, name: username }),
                    credentials: 'include'
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.ok) {
                        loadFavoritesFromServer();
                    } else {
                        addFavoriteLocal(username);
                    }
                })
                .catch(function() { addFavoriteLocal(username); });
            } else {
                addFavoriteLocal(username);
            }
        }

        function addFavoriteLocal(username) {
            if (!favorites.some(function(f) { return f.username.toLowerCase() === username.toLowerCase(); })) {
                favorites.push({ username: username, name: username, addedAt: new Date().toISOString() });
                localStorage.setItem(FAVORITE_KEY, JSON.stringify(favorites));
                renderFavorites();
                updateFavoriteButton();
            }
        }

        function removeFavorite(username) {
            if (currentMode === 'developer') {
                fetch('/api/favorites/' + encodeURIComponent(username), {
                    method: 'DELETE',
                    headers: { 'X-API-Key': API_KEY },
                    credentials: 'include'
                })
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.ok) {
                        loadFavoritesFromServer();
                    } else {
                        removeFavoriteLocal(username);
                    }
                })
                .catch(function() { removeFavoriteLocal(username); });
            } else {
                removeFavoriteLocal(username);
            }
        }

        function removeFavoriteLocal(username) {
            var idx = favorites.findIndex(function(f) { return f.username.toLowerCase() === username.toLowerCase(); });
            if (idx >= 0) {
                favorites.splice(idx, 1);
                localStorage.setItem(FAVORITE_KEY, JSON.stringify(favorites));
                renderFavorites();
                updateFavoriteButton();
            }
        }

        // ---- 博主专属模式 ----
        function openGallery(username, source) {
            isGalleryMode = true;
            galleryUsername = username;
            returnSource = source || '';

            searchPageTitle.textContent = '@' + username + ' 的媒体';
            searchPageDesc.textContent = '';

            var inputRow = document.querySelector('.search-row');
            if (inputRow) {
                inputRow.querySelector('input').style.display = 'none';
                inputRow.querySelector('.search-btn-icon').style.display = 'none';
                var favBtn = inputRow.querySelector('.search-favorite-btn');
                if (favBtn) favBtn.style.display = 'inline-block';
            }

            var favoriteEntry = document.querySelector('.favorite-entry');
            if (favoriteEntry) favoriteEntry.style.display = 'none';

            var sourceLabel = returnSource === 'likes' ? '我的喜欢' : (returnSource === 'bookmarks' ? '我的书签' : '搜索博主');
            backFromSearchText.textContent = '返回 ' + sourceLabel;

            profileInput.value = username;
            updateFavoriteButton();

            showPage('pageSearch');

            searchGallery.innerHTML = '';
            searchResultHeader.classList.add('hidden');
            hideSearchStatus();

            performSearch();
        }

        function exitGallery() {
            var source = returnSource;
            isGalleryMode = false;
            galleryUsername = '';
            returnSource = '';

            searchPageTitle.textContent = '搜索博主';
            searchPageDesc.textContent = '输入 X 用户名，搜索该博主的所有媒体';

            var inputRow = document.querySelector('.search-row');
            if (inputRow) {
                inputRow.querySelector('input').style.display = '';
                inputRow.querySelector('.search-btn-icon').style.display = '';
                var favBtn = inputRow.querySelector('.search-favorite-btn');
                if (favBtn) favBtn.style.display = 'inline-block';
            }

            var favoriteEntry = document.querySelector('.favorite-entry');
            if (favoriteEntry) favoriteEntry.style.display = '';

            backFromSearchText.textContent = '返回';

            profileInput.value = '';
            updateFavoriteButton();
            searchGallery.innerHTML = '';
            searchResultHeader.classList.add('hidden');
            hideSearchStatus();

            setTimeout(function() {
                if (source === 'likes' || source === 'bookmarks') {
                    openLibrary(source);
                } else {
                    showPage('pageSearch');
                }
            }, 50);
        }

        // ---- 工具函数 ----
        function normalizeUsername(input) {
            var value = input.trim();
            if (!value) return null;
            if (value.includes('x.com/') || value.includes('twitter.com/')) {
                if (!value.startsWith('http://') && !value.startsWith('https://')) {
                    value = 'https://' + value;
                }
                try {
                    var url = new URL(value);
                    var parts = url.pathname.split('/').filter(function(p) { return p; });
                    if (parts.length) value = parts[0];
                } catch (e) {
                    return null;
                }
            }
            value = value.replace(/^@+/, '').replace(/\/+$/, '').replace(/[^A-Za-z0-9_]/g, '');
            return value || null;
        }

        function formatDateFromX(value) {
            if (!value) return '';
            var match = value.match(/^\w+\s+(\w+)\s+(\d+).*?(\d{4})$/);
            if (!match) return value;
            var months = { Jan: '01', Feb: '02', Mar: '03', Apr: '04', May: '05', Jun: '06', Jul: '07', Aug: '08', Sep: '09',
                Oct: '10', Nov: '11', Dec: '12' };
            var month = months[match[1]];
            if (!month) return value;
            return match[3] + '-' + month + '-' + String(match[2]).padStart(2, '0');
        }

        function formatLibraryDate(value) {
            if (!value) return '';
            try {
                var date = new Date(value);
                if (isNaN(date.getTime())) return '';
                return date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date
                    .getDate()).padStart(2, '0');
            } catch (e) { return ''; }
        }

        function getLibraryDateRange() {
            if (libraryRange === 'all') return { start: null, end: null };
            if (libraryRange === 'custom') {
                return { start: libraryStartDate.value || null, end: libraryEndDate.value || null };
            }
            var now = new Date();
            var start = new Date(now);
            start.setDate(start.getDate() - Number(libraryRange));
            return {
                start: start.getFullYear() + '-' + String(start.getMonth() + 1).padStart(2, '0') + '-' + String(start
                    .getDate()).padStart(2, '0'),
                end: now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now
                    .getDate()).padStart(2, '0')
            };
        }

        function getDates() {
            if (range === 'all') return { start: null, end: null };
            if (range === 'custom') return { start: startDate.value || null, end: endDate.value || null };
            var now = new Date();
            var start = new Date(now);
            start.setDate(start.getDate() - Number(range));
            return {
                start: start.getFullYear() + '-' + String(start.getMonth() + 1).padStart(2, '0') + '-' + String(start
                    .getDate()).padStart(2, '0'),
                end: now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now
                    .getDate()).padStart(2, '0')
            };
        }

        function getFilename(item) {
            var date = formatDateFromX(item.created_at || item.createdAt) || 'x-media';
            var suffix = (item.media_total && item.media_total > 1) ? '-' + item.media_index : '';
            var extension = '.jpg';
            var type = item.media_type || item.type;
            var rawUrl = item.originalUrl || item.sourceUrl || item.media_url || item.url || '';
            var lower = String(rawUrl).toLowerCase();
            if (type === 'video') extension = '.mp4';
            else if (lower.includes('.png')) extension = '.png';
            else if (lower.includes('.webp')) extension = '.webp';
            else if (lower.includes('.gif')) extension = '.gif';
            return date + suffix + extension;
        }

        function showSearchStatus(msg, type) {
            type = type || '';
            searchStatus.classList.remove('hidden');
            searchStatus.textContent = msg;
            searchStatus.className = 'status-box' + (type === 'error' ? ' error' : '');
        }

        function hideSearchStatus() {
            searchStatus.classList.add('hidden');
            searchStatus.textContent = '';
            searchStatus.className = 'status-box';
        }

        // ---- 搜索 ----
        function performSearch() {
            var raw = profileInput.value.trim();
            var username = normalizeUsername(raw);
            if (!username) {
                showSearchStatus('无法识别博主。可以输入：NASA / @NASA / x.com/NASA', 'error');
                return;
            }
            var dates = getDates();
            if (dates.start && dates.end && dates.start > dates.end) {
                showSearchStatus('开始日期不能晚于结束日期', 'error');
                return;
            }
            searchSubmitBtn.disabled = true;
            searchSubmitBtn.textContent = '正在收集…';
            hideSearchStatus();
            searchResultHeader.classList.add('hidden');
            searchGallery.innerHTML = '';

            var params = new URLSearchParams();
            params.set('profile', 'https://x.com/' + username);
            params.set('media_type', mediaType);
            params.set('source_type', sourceType);
            if (dates.start) params.set('start_date', dates.start);
            if (dates.end) params.set('end_date', dates.end);

            fetch('/api/search?' + params.toString())
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (!data.ok) throw new Error(data.detail || '搜索失败');
                    renderSearchResults(data, username);
                })
                .catch(function(err) {
                    showSearchStatus(err.message || '搜索失败', 'error');
                })
                .finally(function() {
                    searchSubmitBtn.disabled = false;
                    searchSubmitBtn.textContent = '开始收集媒体';
                });
        }

        function renderSearchResults(data, username) {
            searchResultHeader.classList.remove('hidden');
            searchResultTitle.textContent = '@' + username;
            searchResultCount.textContent = '找到 ' + data.count + ' 个媒体 · 查询 ' + data.pages + ' 页';
            searchGallery.innerHTML = '';
            if (!data.items || data.items.length === 0) {
                searchGallery.innerHTML = '<div class="loader">没有找到媒体</div>';
                return;
            }
            data.items.forEach(function(item) {
                searchGallery.appendChild(createMediaItem(item, 'search'));
            });
        }

        // ---- 媒体库 ----
        function getStorageKey(source) {
            return 'universal_downloader_' + source;
        }

        function loadLibraryFromLocal(source) {
            libraryCount.textContent = '正在读取本地数据…';
            libraryStatus.classList.add('hidden');
            libraryResultHeader.classList.add('hidden');
            libraryGallery.innerHTML = '';
            libraryGallery.classList.remove('fade-in');

            var key = getStorageKey(source);
            var raw = localStorage.getItem(key);
            var items = [];
            try {
                if (raw) {
                    var parsed = JSON.parse(raw);
                    if (Array.isArray(parsed)) {
                        items = parsed;
                    }
                }
            } catch (e) {
                console.warn('读取本地数据失败:', e);
            }

            if (!items || items.length === 0) {
                libraryCount.textContent = '共 0 个媒体';
                libraryGallery.innerHTML = '<div class="library-placeholder"><span class="icon">📭</span>暂无数据，请安装采集器</div>';
                libraryResultHeader.classList.add('hidden');
                selectToggleBtn.classList.add('hidden');
                libraryGallery.classList.add('fade-in');
                return;
            }

            var formatted = items.map(function(item, index) {
                return {
                    id: item.id || 'local_' + index,
                    type: item.type || 'image',
                    url: item.url || '',
                    originalUrl: item.originalUrl || item.url || '',
                    thumbnail: item.thumbnail || item.url || '',
                    tweet_url: item.tweet_url || item.url || '',
                    author: item.author || '采集器',
                    tweetCreatedAt: item.createdAt || new Date().toISOString(),
                    source: source,
                };
            });

            cachedLibraryItems = formatted;
            cachedLibrarySource = source;
            selectToggleBtn.classList.remove('hidden');
            resetPagination();
            renderLibraryResults();
        }

        function loadLibraryFromServer(source) {
            if (source !== cachedLibrarySource || cachedLibraryItems.length === 0) {
                libraryCount.textContent = '正在读取…';
                libraryStatus.classList.add('hidden');
                libraryResultHeader.classList.add('hidden');
                libraryGallery.innerHTML = '';
                libraryGallery.classList.remove('fade-in');

                var params = new URLSearchParams();
                params.set('source', source);
                params.set('media_type', 'all');

                fetch('/api/media?' + params.toString(), { credentials: 'include' })
                    .then(function(res) { return res.json(); })
                    .then(function(data) {
                        if (!data.ok) throw new Error(data.detail || '读取媒体库失败');
                        cachedLibraryItems = data.items || [];
                        cachedLibrarySource = source;
                        selectToggleBtn.classList.remove('hidden');
                        resetPagination();
                        renderLibraryResults();
                    })
                    .catch(function(err) {
                        libraryCount.textContent = '读取失败';
                        libraryStatus.classList.remove('hidden');
                        libraryStatus.textContent = err.message || '读取媒体库失败';
                        libraryStatus.className = 'status-box error';
                        selectToggleBtn.classList.add('hidden');
                    });
                return;
            }

            selectToggleBtn.classList.remove('hidden');
            resetPagination();
            renderLibraryResults();
        }

        function openLibrary(source) {
            currentSubPage = source;
            if (source === 'likes') {
                libraryTitle.textContent = '我的喜欢';
                libraryDesc.textContent = '查看采集器上传的喜欢列表';
            } else {
                libraryTitle.textContent = '我的书签';
                libraryDesc.textContent = '查看采集器上传的书签列表';
            }
            showPage('pageLibrary');

            updateLibraryBanner(currentMode);

            if (currentMode === 'guest') {
                loadLibraryFromLocal(source);
            } else {
                fetch('/api/auth/check', { credentials: 'include' })
                    .then(function(res) { return res.json(); })
                    .then(function(data) {
                        if (!data.authenticated) {
                            libraryCount.textContent = '会话已过期';
                            libraryGallery.innerHTML =
                                '<div class="library-placeholder"><span class="icon">🔒</span>请返回首页重新登录</div>';
                            libraryGallery.classList.add('fade-in');
                            selectToggleBtn.classList.add('hidden');
                            return;
                        }
                        loadLibraryFromServer(source);
                    })
                    .catch(function() {
                        libraryCount.textContent = '连接失败';
                        libraryGallery.innerHTML =
                            '<div class="library-placeholder"><span class="icon">📡</span>无法连接服务器</div>';
                        libraryGallery.classList.add('fade-in');
                        selectToggleBtn.classList.add('hidden');
                    });
            }
        }

        function renderLibraryResults() {
            var filtered = cachedLibraryItems;
            if (libraryMediaType === 'image') {
                filtered = cachedLibraryItems.filter(function(item) { return item.type === 'image'; });
            } else if (libraryMediaType === 'video') {
                filtered = cachedLibraryItems.filter(function(item) { return item.type === 'video'; });
            }

            var dateRange = getLibraryDateRange();
            if (dateRange.start || dateRange.end) {
                var startDt = dateRange.start ? new Date(dateRange.start + 'T00:00:00Z') : null;
                var endDt = dateRange.end ? new Date(dateRange.end + 'T23:59:59Z') : null;
                filtered = filtered.filter(function(item) {
                    var timeStr = item.tweetCreatedAt || item.createdAt || '';
                    if (!timeStr) return true;
                    try {
                        var dt = new Date(timeStr);
                        if (isNaN(dt.getTime())) return true;
                        if (startDt && dt < startDt) return false;
                        if (endDt && dt > endDt) return false;
                        return true;
                    } catch (e) { return true; }
                });
            }

            allFilteredItems = filtered;
            libraryCount.textContent = '共 ' + allFilteredItems.length + ' 个媒体';
            libraryResultHeader.classList.remove('hidden');
            libraryResultTitle.textContent = currentSubPage === 'likes' ? '我的喜欢' : '我的书签';
            libraryResultCount.textContent = '共 ' + allFilteredItems.length + ' 个媒体';

            libraryGallery.innerHTML = '';
            libraryGallery.classList.remove('fade-in');

            if (!allFilteredItems || allFilteredItems.length === 0) {
                libraryGallery.innerHTML = '<div class="loader">没有符合条件的媒体</div>';
                libraryGallery.classList.add('fade-in');
                return;
            }

            allFilteredItems.sort(function(a, b) {
                var timeA = a.tweetCreatedAt || a.createdAt || '';
                var timeB = b.tweetCreatedAt || b.createdAt || '';
                if (timeA && timeB) return timeB.localeCompare(timeA);
                if (timeA && !timeB) return -1;
                if (!timeA && timeB) return 1;
                return 0;
            });

            currentBatch = 0;
            allLoaded = false;
            isLoadingMore = false;
            if (isSelectMode) exitSelectMode();
            loadNextBatch();

            if (!scrollListenerAttached) {
                window.addEventListener('scroll', handleScroll);
                scrollListenerAttached = true;
            }
        }

        function resetPagination() {
            allFilteredItems = [];
            currentBatch = 0;
            allLoaded = false;
            isLoadingMore = false;
        }

        function resetPaginationAndRender() {
            resetPagination();
            renderLibraryResults();
        }

        function loadNextBatch() {
            if (allLoaded || isLoadingMore) return;
            if (currentBatch * BATCH_SIZE >= allFilteredItems.length) {
                allLoaded = true;
                libraryGallery.classList.add('fade-in');
                return;
            }

            isLoadingMore = true;
            requestAnimationFrame(function() {
                var start = currentBatch * BATCH_SIZE;
                var end = Math.min(start + BATCH_SIZE, allFilteredItems.length);
                var fragment = document.createDocumentFragment();
                for (var i = start; i < end; i++) {
                    var el = createMediaItem(allFilteredItems[i], 'library');
                    fragment.appendChild(el);
                }
                libraryGallery.appendChild(fragment);
                currentBatch++;

                if (currentBatch * BATCH_SIZE >= allFilteredItems.length) {
                    allLoaded = true;
                    libraryGallery.classList.add('fade-in');
                }
                isLoadingMore = false;
            });
        }

        var scrollTimeout = null;

        function handleScroll() {
            if (scrollTimeout) return;
            scrollTimeout = setTimeout(function() {
                scrollTimeout = null;
                var scrollY = window.scrollY || window.pageYOffset;
                var windowHeight = window.innerHeight;
                var docHeight = document.documentElement.scrollHeight;
                if (scrollY + windowHeight >= docHeight - 300) {
                    if (!allLoaded && !isLoadingMore) {
                        loadNextBatch();
                    }
                }
            }, 150);
        }

        refreshLibraryBtn.addEventListener('click', function() {
            cachedLibraryItems = [];
            cachedLibrarySource = '';
            resetPagination();
            if (currentSubPage) {
                openLibrary(currentSubPage);
            }
        });

        // ---- 选项按钮 ----
        function bindOptionButtons() {
            document.querySelectorAll('.option-row').forEach(function(row) {
                row.querySelectorAll('.option-btn').forEach(function(btn) {
                    btn.removeEventListener('click', btn._listener);
                    var listener = function() {
                        var group = row.dataset.group;
                        row.querySelectorAll('.option-btn').forEach(function(b) { b.classList.remove(
                            'active'); });
                        btn.classList.add('active');
                        var value = btn.dataset.value;

                        if (group === 'range') {
                            range = value;
                            customDates.classList.toggle('hidden', value !== 'custom');
                            if (isGalleryMode && galleryUsername) {
                                performSearch();
                            }
                        } else if (group === 'media') {
                            mediaType = value;
                            if (isGalleryMode && galleryUsername) {
                                performSearch();
                            }
                        } else if (group === 'source') {
                            sourceType = value;
                            if (isGalleryMode && galleryUsername) {
                                performSearch();
                            }
                        } else if (group === 'libraryRange') {
                            libraryRange = value;
                            libraryCustomDates.classList.toggle('hidden', value !== 'custom');
                            resetPaginationAndRender();
                        } else if (group === 'libraryMedia') {
                            libraryMediaType = value;
                            resetPaginationAndRender();
                        }
                    };
                    btn._listener = listener;
                    btn.addEventListener('click', listener);
                });
            });
        }

        // ---- 选择模式 ----
        selectToggleBtn.addEventListener('click', function() {
            enterSelectMode();
        });

        function enterSelectMode() {
            if (isSelectMode) return;
            isSelectMode = true;
            selectedIds.clear();

            selectionToolbar.classList.add('active');
            selectToggleBtn.textContent = '取消选择';
            selectToggleBtn.style.color = 'rgba(255,255,255,0.6)';

            var items = document.querySelectorAll('#libraryGallery .item');
            items.forEach(function(el) {
                el.classList.add('in-select-mode');
                el.removeEventListener('click', handleItemClick);
                el.addEventListener('click', handleItemClick);
            });

            updateSelectedCount();
        }

        function exitSelectMode() {
            if (!isSelectMode) return;
            isSelectMode = false;
            selectedIds.clear();

            selectionToolbar.classList.remove('active');
            selectToggleBtn.textContent = '选择';
            selectToggleBtn.style.color = 'rgba(255,255,255,0.4)';

            var items = document.querySelectorAll('#libraryGallery .item');
            items.forEach(function(el) {
                el.classList.remove('in-select-mode', 'selected');
                el.removeEventListener('click', handleItemClick);
            });

            updateSelectedCount();
        }

        function handleItemClick(e) {
            var item = e.currentTarget;
            if (e.target.closest('button') || e.target.closest('a')) return;

            var mediaId = item.dataset.mediaId;
            if (!mediaId) return;

            if (selectedIds.has(mediaId)) {
                selectedIds.delete(mediaId);
                item.classList.remove('selected');
            } else {
                selectedIds.add(mediaId);
                item.classList.add('selected');
            }
            updateSelectedCount();
        }

        function updateSelectedCount() {
            var count = selectedIds.size;
            selectedCount.textContent = '已选 ' + count + ' 个';
            toolbarDelete.style.display = count > 0 ? 'block' : 'none';
        }

        toolbarSelectAll.addEventListener('click', function() {
            var items = document.querySelectorAll('#libraryGallery .item');
            var allSelected = true;
            items.forEach(function(el) {
                var id = el.dataset.mediaId;
                if (id && !selectedIds.has(id)) {
                    allSelected = false;
                }
            });
            if (allSelected) {
                items.forEach(function(el) {
                    var id = el.dataset.mediaId;
                    if (id) {
                        selectedIds.delete(id);
                        el.classList.remove('selected');
                    }
                });
            } else {
                items.forEach(function(el) {
                    var id = el.dataset.mediaId;
                    if (id) {
                        selectedIds.add(id);
                        el.classList.add('selected');
                    }
                });
            }
            updateSelectedCount();
        });

        toolbarCancel.addEventListener('click', exitSelectMode);

        toolbarDelete.addEventListener('click', function() {
            var count = selectedIds.size;
            if (count === 0) return;
            confirmTitle.textContent = '删除 ' + count + ' 个媒体？';
            confirmDesc.textContent = '这些媒体将被永久删除，无法恢复。';
            deleteConfirm.classList.add('active');
        });

        confirmCancel.addEventListener('click', function() {
            deleteConfirm.classList.remove('active');
        });

        confirmDelete.addEventListener('click', function() {
            var ids = Array.from(selectedIds);
            if (ids.length === 0) return;
            deleteConfirm.classList.remove('active');

            if (currentMode === 'guest') {
                var key = getStorageKey(currentSubPage);
                var raw = localStorage.getItem(key);
                if (raw) {
                    try {
                        var items = JSON.parse(raw);
                        var idSet = new Set(ids);
                        var filtered = items.filter(function(item) {
                            return !idSet.has(item.id);
                        });
                        localStorage.setItem(key, JSON.stringify(filtered));
                        loadLibraryFromLocal(currentSubPage);
                        exitSelectMode();
                    } catch (e) {
                        alert('删除失败：' + e.message);
                    }
                }
                return;
            }

            fetch('/api/media', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ media_ids: ids }),
                credentials: 'include'
            })
            .then(function(res) { return res.json(); })
            .then(function(data) {
                if (data.ok) {
                    var deletedSet = new Set(ids);
                    cachedLibraryItems = cachedLibraryItems.filter(function(item) { return !deletedSet.has(item
                        .id); });
                    exitSelectMode();
                    renderLibraryResults();
                } else {
                    alert('删除失败：' + (data.detail || '未知错误'));
                }
            })
            .catch(function(e) {
                alert('删除请求失败：' + e.message);
            });
        });

        deleteConfirm.addEventListener('click', function(e) {
            if (e.target === deleteConfirm) {
                deleteConfirm.classList.remove('active');
            }
        });

        // ---- 创建媒体卡片 ----
        function createMediaItem(item, mode) {
            var wrapper = document.createElement('div');
            wrapper.className = 'item';
            wrapper.dataset.mediaId = item.id || '';

            var isVideo = item.media_type === 'video' || item.type === 'video';
            var mediaUrl = item.media_url || item.url || '';
            var thumbnail = item.thumbnail || mediaUrl;
            var normalized = normalizeLibraryItem(item);

            var mediaWrap = document.createElement('div');
            mediaWrap.className = 'media-wrap';

            var checkBox = document.createElement('div');
            checkBox.className = 'select-check';
            mediaWrap.appendChild(checkBox);

            var img = document.createElement('img');
            img.src = isVideo ? thumbnail : mediaUrl;
            img.loading = 'lazy';
            img.alt = item.alt || '';
            img.onerror = function() {
                var fallback = item.originalUrl || item.sourceUrl || '';
                if (fallback && !img.dataset.fallback) {
                    img.dataset.fallback = '1';
                    img.src = '/api/media-proxy?url=' + encodeURIComponent(fallback);
                    return;
                }
                var errorDiv = document.createElement('div');
                errorDiv.className = 'media-error';
                errorDiv.textContent = '媒体暂时无法加载';
                img.replaceWith(errorDiv);
            };
            img.addEventListener('click', function() { openModal(normalized); });

            mediaWrap.appendChild(img);

            if (isVideo) {
                var badge = document.createElement('div');
                badge.className = 'video-badge';
                badge.textContent = '视频';
                mediaWrap.appendChild(badge);
            }

            if (mode === 'search') {
                if (item.source && item.source !== 'original') {
                    var badge2 = document.createElement('div');
                    badge2.className = 'source-badge';
                    badge2.textContent = item.source === 'repost' ? '转帖' : '引用';
                    mediaWrap.appendChild(badge2);
                }
            } else {
                var badge2 = document.createElement('div');
                badge2.className = 'library-badge';
                badge2.textContent = currentSubPage === 'likes' ? '喜欢' : '书签';
                mediaWrap.appendChild(badge2);
            }

            wrapper.appendChild(mediaWrap);

            var info = document.createElement('div');
            info.className = 'item-info';

            if (item.author) {
                var author = document.createElement('div');
                author.className = 'item-author';
                author.textContent = '@' + item.author;
                if (mode === 'library') {
                    author.style.cursor = 'pointer';
                    author.addEventListener('click', function(e) {
                        e.stopPropagation();
                        var username = item.author;
                        if (username) {
                            openGallery(username, currentSubPage);
                        }
                    });
                }
                info.appendChild(author);
            }

            var date = document.createElement('div');
            date.className = 'item-date';
            var rawDate = item.tweetCreatedAt || item.created_at || item.createdAt || '';
            date.textContent = mode === 'search' ? formatDateFromX(rawDate) : formatLibraryDate(rawDate);
            info.appendChild(date);

            var actions = document.createElement('div');
            actions.className = 'item-actions';

            var viewBtn = document.createElement('button');
            viewBtn.className = 'btn-view';
            viewBtn.textContent = isVideo ? '播放' : '查看';
            viewBtn.onclick = function(e) { e.stopPropagation();
                openModal(normalized); };
            actions.appendChild(viewBtn);

            var downloadBtn = document.createElement('button');
            downloadBtn.className = 'btn-download';
            downloadBtn.textContent = '下载';
            downloadBtn.onclick = function(e) { e.stopPropagation();
                downloadItem(normalized); };
            actions.appendChild(downloadBtn);

            var postBtn = document.createElement('button');
            postBtn.className = 'btn-original';
            postBtn.textContent = '原帖';
            postBtn.onclick = function(e) { e.stopPropagation(); if (item.tweet_url) window.open(item.tweet_url,
                    '_blank'); };
            actions.appendChild(postBtn);

            info.appendChild(actions);
            wrapper.appendChild(info);

            return wrapper;
        }

        function normalizeLibraryItem(item) {
            var type = item.type || item.media_type || 'image';
            var mediaUrl = item.url || item.media_url || item.sourceUrl || '';
            var originalUrl = item.originalUrl || item.sourceUrl || mediaUrl;
            return {
                media_type: type,
                media_url: mediaUrl,
                video_url: type === 'video' ? mediaUrl : '',
                thumbnail: item.thumbnail || '',
                tweet_url: item.tweet_url || '',
                author: item.author || '',
                created_at: item.tweetCreatedAt || item.createdAt || item.created_at || '',
                originalUrl: originalUrl,
                libraryId: item.id || '',
                width: item.width || 0,
                height: item.height || 0,
                bitrate: item.bitrate || 0,
                streamType: item.streamType || '',
                media_index: item.media_index || 1,
                media_total: item.media_total || 1
            };
        }

        // ============================================================
        // 核心修复：下载
        // ============================================================
        function downloadItem(item) {
            var url = item.originalUrl || item.media_url || item.url || '';
            if (!url) {
                alert('这个媒体暂时没有可下载地址。');
                return;
            }

            var isVideo = item.media_type === 'video' || item.type === 'video';
            var filename = getFilename(item);

            if (isVideo) {
                var videoFilename = filename.endsWith('.mp4') ? filename : filename + '.mp4';
                window.location.href = '/api/video-download?url=' + encodeURIComponent(url) + '&filename=' + encodeURIComponent(videoFilename);
            } else {
                window.location.href = '/api/download?url=' + encodeURIComponent(url) + '&filename=' + encodeURIComponent(filename);
            }
        }

        // ============================================================
        // 核心修复：预览
        // HLS 视频：新标签页打开（系统播放器）
        // MP4 视频：在 Modal 中播放（走代理）
        // 图片：在 Modal 中查看大图
        // ============================================================
        function openModal(item) {
            currentItem = item;
            modalContent.innerHTML = '';

            var rawVideoUrl = item.originalUrl || item.video_url || item.media_url || item.url || '';
            var isVideo = item.media_type === 'video' || item.type === 'video';

            if (isVideo) {
                if (!rawVideoUrl) {
                    modalContent.innerHTML = '<div class="media-error" style="color:#fff;background:transparent;">该视频暂无可用播放地址，请点击下载保存到本地</div>';
                    modalDownloadBtn.textContent = '下载视频';
                    modal.classList.remove('hidden');
                    return;
                }

                // 判断是否为 HLS（.m3u8）
                var isM3u8 = rawVideoUrl.includes('.m3u8') || rawVideoUrl.includes('m3u8');

                if (isM3u8) {
                    // HLS 视频：直接在新标签页用系统播放器打开，不显示 Modal
                    window.open(rawVideoUrl, '_blank');
                    // 关闭 Modal
                    modal.classList.add('hidden');
                    modalContent.innerHTML = '';
                    currentItem = null;
                    return;
                }

                // MP4 或其他：走代理播放（保留原有 Modal 逻辑）
                var container = document.createElement('div');
                container.style.cssText = 'width:100%;height:100%;display:flex;align-items:center;justify-content:center;position:relative;';

                var video = document.createElement('video');
                video.controls = true;
                video.autoplay = true;
                video.playsInline = true;
                video.preload = 'metadata';
                video.style.cssText = 'max-width:100%;max-height:100%;';

                var proxyUrl = '/api/media-proxy?url=' + encodeURIComponent(rawVideoUrl);
                video.src = proxyUrl;
                video.load();

                video.addEventListener('loadedmetadata', function() {
                    video.play().catch(function() {});
                });

                video.addEventListener('error', function(e) {
                    console.error('视频播放错误:', video.error);
                    video.style.display = 'none';
                    var errorMsg = document.createElement('div');
                    errorMsg.style.cssText = 'color:rgba(255,255,255,0.5);text-align:center;padding:20px;font-size:14px;font-weight:300;';
                    errorMsg.textContent = '视频加载失败，请尝试下载后播放';
                    container.appendChild(errorMsg);
                });

                container.appendChild(video);
                modalContent.appendChild(container);

                modalDownloadBtn.textContent = '下载视频';
                modalDownloadBtn.onclick = function() {
                    downloadItem(item);
                };
                modal.classList.remove('hidden');
            } else {
                // 图片：保留完整预览功能
                var img = document.createElement('img');
                img.src = item.media_url || item.url || item.originalUrl || '';
                img.alt = item.alt || '';
                img.onerror = function() {
                    var proxySource = item.originalUrl || item.sourceUrl || '';
                    if (proxySource && !img.dataset.proxy) {
                        img.dataset.proxy = '1';
                        img.src = '/api/media-proxy?url=' + encodeURIComponent(proxySource);
                        return;
                    }
                    modalContent.innerHTML = '<div class="media-error" style="color:#fff;background:transparent;">图片暂时无法加载</div>';
                };
                modalContent.appendChild(img);
                modalDownloadBtn.textContent = '下载原图';
                modalDownloadBtn.onclick = function() {
                    downloadItem(item);
                };
                modal.classList.remove('hidden');
            }
        }

        // ---- 事件绑定、导航、初始化 ----
        modalCloseBtn.addEventListener('click', closeModal);
        modal.addEventListener('click', function(e) {
            if (e.target === modal) closeModal();
        });

        function closeModal() {
            var video = modalContent.querySelector('video');
            if (video) {
                video.pause();
                video.removeAttribute('src');
                video.load();
                video.remove();
            }
            if (currentHls) {
                currentHls.destroy();
                currentHls = null;
            }
            modal.classList.add('hidden');
            modalContent.innerHTML = '';
            currentItem = null;
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeModal();
        });

        modalDownloadBtn.addEventListener('click', function() {
            if (currentItem) downloadItem(currentItem);
        });

        modalOriginalBtn.addEventListener('click', function() {
            if (currentItem && currentItem.tweet_url) {
                window.open(currentItem.tweet_url, '_blank');
            }
        });

        backToHome.addEventListener('click', function() {
            window.location.href = '/';
        });

        backFromSearch.addEventListener('click', function() {
            if (isGalleryMode) {
                exitGallery();
            } else {
                showPage('pageXSub');
            }
        });

        backFromLibrary.addEventListener('click', function() {
            showPage('pageXSub');
            if (isSelectMode) exitSelectMode();
        });

        subSearch.addEventListener('click', function() {
            showPage('pageSearch');
        });

        subLikes.addEventListener('click', function() {
            openLibrary('likes');
        });

        subBookmarks.addEventListener('click', function() {
            openLibrary('bookmarks');
        });

        function refreshDomRefs() {
            // 重新获取所有 DOM 引用（以防 Turbo 缓存导致引用失效）
        }

        function initApp() {
            refreshDomRefs();

            searchBtn.addEventListener('click', performSearch);
            searchSubmitBtn.addEventListener('click', performSearch);
            profileInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') performSearch();
            });

            bindFavoriteEvents();
            bindOptionButtons();

            libraryStartDate.addEventListener('change', function() {
                if (libraryRange === 'custom') resetPaginationAndRender();
            });
            libraryEndDate.addEventListener('change', function() {
                if (libraryRange === 'custom') resetPaginationAndRender();
            });

            selectToggleBtn.addEventListener('click', function() {
                enterSelectMode();
            });

            refreshLibraryBtn.addEventListener('click', function() {
                cachedLibraryItems = [];
                cachedLibrarySource = '';
                resetPagination();
                if (currentSubPage) {
                    openLibrary(currentSubPage);
                }
            });

            var savedMode = localStorage.getItem('userMode') || 'guest';
            currentMode = savedMode;

            if (currentMode === 'developer') {
                fetch('/api/auth/check', { credentials: 'include' })
                    .then(function(res) { return res.json(); })
                    .then(function(data) {
                        if (!data.authenticated) {
                            currentMode = 'guest';
                            localStorage.setItem('userMode', 'guest');
                            console.log('⚠️ Session 已过期，降级为访客模式');
                        }
                        updateModeBanners();
                        loadFavorites();
                        showPage('pageXSub');
                    })
                    .catch(function() {
                        currentMode = 'guest';
                        localStorage.setItem('userMode', 'guest');
                        updateModeBanners();
                        loadFavorites();
                        showPage('pageXSub');
                    });
            } else {
                updateModeBanners();
                loadFavorites();
                showPage('pageXSub');
            }

            console.log('🐦 X 下载器已加载（Turbo 模式）');
            console.log('开发者：浮生若夢');
            console.log('当前模式：' + currentMode);
        }

        document.addEventListener('turbo:before-cache', function() {
            if (scrollListenerAttached) {
                window.removeEventListener('scroll', handleScroll);
                scrollListenerAttached = false;
            }
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
                scrollTimeout = null;
            }
        });

        document.addEventListener('turbo:load', initApp);
        document.addEventListener('DOMContentLoaded', initApp);
    </script>
</body>
</html>
