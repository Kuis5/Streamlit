"""
1画面レイアウト用のCSS（機能全保持版・余白最小化）
"""

COMPACT_CSS = """
<style>
/* 日本語フォント指定 */
body, .stApp, .stMarkdown, .stMetric, input, select, textarea {
    font-family: '源暎ラテゴ', 'ラテミン', 'Noto Sans JP', 'Hiragino Sans', sans-serif;
}

/* Streamlitのヘッダーとメニューを非表示 */
header[data-testid="stHeader"],
.stDeployButton,
#MainMenu,
footer {
    display: none !important;
}

/* 上部の余白を完全削除 */
.main {
    padding-top: 0 !important;
}

/* ブロックコンテナの上部余白を削除 */
.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* 全体の背景 - ダークストーン（モダン＆リッチ） */
.stApp {
    background: 
        /* 大理石のような筋模様 */
        linear-gradient(
            135deg,
            rgba(60, 70, 80, 0.4) 0%,
            transparent 15%,
            transparent 35%,
            rgba(70, 80, 90, 0.35) 50%,
            transparent 65%,
            transparent 85%,
            rgba(60, 70, 80, 0.4) 100%
        ),
        linear-gradient(
            45deg,
            transparent 0%,
            rgba(80, 90, 100, 0.25) 25%,
            transparent 45%,
            rgba(70, 80, 90, 0.25) 75%,
            transparent 100%
        ),
        /* 微細な金属的な光沢 */
        repeating-linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.03) 0px,
            rgba(255, 255, 255, 0.03) 1px,
            transparent 1px,
            transparent 3px
        ),
        repeating-linear-gradient(
            0deg,
            rgba(255, 255, 255, 0.02) 0px,
            rgba(255, 255, 255, 0.02) 1px,
            transparent 1px,
            transparent 3px
        ),
        /* 淡い光のアクセント */
        radial-gradient(
            ellipse at 20% 20%,
            rgba(100, 120, 150, 0.15) 0%,
            rgba(100, 120, 150, 0.08) 30%,
            transparent 60%
        ),
        radial-gradient(
            ellipse at 80% 80%,
            rgba(120, 100, 150, 0.15) 0%,
            rgba(120, 100, 150, 0.08) 30%,
            transparent 60%
        ),
        /* ベースの深いグラデーション */
        radial-gradient(
            ellipse at 50% 50%,
            #2a2a30 0%,
            #1a1a20 50%,
            #0f0f12 100%
        ),
        #0f0f12 !important;
    height: 100vh !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* 微細なノイズと光の反射 */
.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        /* ノイズテクスチャ */
        repeating-linear-gradient(
            45deg,
            rgba(255, 255, 255, 0.02) 0px,
            rgba(255, 255, 255, 0.02) 1px,
            transparent 1px,
            transparent 2px
        ),
        repeating-linear-gradient(
            -45deg,
            rgba(255, 255, 255, 0.02) 0px,
            rgba(255, 255, 255, 0.02) 1px,
            transparent 1px,
            transparent 2px
        ),
        /* 光のハイライト */
        radial-gradient(
            circle at 30% 30%,
            rgba(150, 160, 180, 0.12) 0%,
            rgba(150, 160, 180, 0.06) 20%,
            transparent 40%
        ),
        radial-gradient(
            circle at 70% 70%,
            rgba(160, 150, 180, 0.12) 0%,
            rgba(160, 150, 180, 0.06) 20%,
            transparent 40%
        );
    opacity: 1;
    pointer-events: none;
    z-index: 0;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.9; }
}

/* メインコンテンツエリア - 余白最小化 */
.main .block-container {
    padding: 0.2rem 0.5rem !important;
    background: 
        linear-gradient(135deg, rgba(25, 25, 28, 0.85) 0%, rgba(18, 18, 22, 0.85) 100%) !important;
    backdrop-filter: blur(15px) !important;
    max-width: 100% !important;
    position: relative !important;
    z-index: 1 !important;
    border: 1px solid rgba(80, 80, 100, 0.2) !important;
    box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.03),
        inset 0 0 50px rgba(0, 0, 0, 0.5),
        0 8px 32px rgba(0, 0, 0, 0.4) !important;
}

/* スクロールバー */
::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3) !important;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 3px !important;
}

/* 見出し - コンパクト */
h1, h2, h3, h4 {
    color: #ffffff !important;
    text-shadow: 0 0 8px rgba(100, 200, 255, 0.4), 2px 2px 3px rgba(0, 0, 0, 0.7) !important;
    font-family: 'Arial Black', sans-serif !important;
    margin: 0.15rem 0 !important;
    line-height: 1 !important;
}

h1 { font-size: 1.2rem !important; }
h2 { font-size: 1rem !important; }
h3 { font-size: 0.9rem !important; }
h4 { font-size: 0.8rem !important; }

/* 段落 */
p {
    margin: 0.1rem 0 !important;
    font-size: 0.75rem !important;
    line-height: 1.1 !important;
}

/* プログレスバー */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #ff6b6b 0%, #ee5a6f 100%) !important;
    box-shadow: 0 0 8px rgba(255, 107, 107, 0.4) !important;
}

.stProgress {
    height: 10px !important;
    margin: 2px 0 !important;
}

/* ボタン */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 5px !important;
    padding: 0.2rem 0.5rem !important;
    font-weight: bold !important;
    font-size: 0.7rem !important;
    box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3) !important;
    transition: all 0.2s ease !important;
    min-height: 28px !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 10px rgba(102, 126, 234, 0.5) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
}

.stButton > button:disabled {
    background: linear-gradient(135deg, #555555 0%, #333333 100%) !important;
    opacity: 0.5 !important;
}

/* メトリック */
[data-testid="stMetricValue"] {
    font-size: 0.85rem !important;
    color: #ffffff !important;
    font-weight: bold !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
}

[data-testid="stMetric"] {
    padding: 0.2rem !important;
}

/* エキスパンダー */
details {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 6px !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    margin: 2px 0 !important;
}

summary {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%) !important;
    color: white !important;
    padding: 4px 6px !important;
    border-radius: 6px !important;
    font-weight: bold !important;
    font-size: 0.7rem !important;
    cursor: pointer !important;
}

.streamlit-expanderContent {
    background: rgba(0, 0, 0, 0.2) !important;
    padding: 5px !important;
    max-height: 120px !important;
    overflow-y: auto !important;
    font-size: 0.7rem !important;
}

/* アラート */
.stAlert {
    padding: 4px 6px !important;
    margin: 2px 0 !important;
    font-size: 0.7rem !important;
    border-radius: 5px !important;
}

/* 区切り線 */
hr {
    margin: 0.15rem 0 !important;
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent) !important;
}

/* カラム */
[data-testid="column"] {
    padding: 2px !important;
}

/* キャプション */
.st-emotion-cache-1kyxreq,
[data-testid="stCaptionContainer"] {
    font-size: 0.65rem !important;
    margin: 0.05rem 0 !important;
}

/* テキスト */
p, span, div, li {
    color: rgba(255, 255, 255, 0.95) !important;
}

/* 情報ボックス */
.stInfo, .stSuccess, .stError, .stWarning {
    padding: 3px 6px !important;
    margin: 2px 0 !important;
    font-size: 0.7rem !important;
}

/* マークダウンのdiv（カスタムHTML用） */
.st-emotion-cache-16idsys p {
    margin: 0.05rem 0 !important;
}

/* インライン要素のマージン調整 */
.element-container {
    margin: 0.05rem 0 !important;
}
</style>
"""