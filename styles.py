"""
ビジュアル重視のゲームUI CSS
"""

COMPACT_CSS = """
<style>
/* Google Fontsは使えないのでシステム日本語フォントを活用 */
body, .stApp, .stMarkdown, .stMetric, input, select, textarea {
    font-family: 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', 'Noto Sans JP', 'Yu Gothic', sans-serif;
}

/* Streamlitのヘッダーとメニューを非表示 */
header[data-testid="stHeader"],
.stDeployButton,
#MainMenu,
footer {
    display: none !important;
}

/* 上部の余白を削除 */
.main { padding-top: 0 !important; }

.block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 1rem !important;
}

/* ========== 背景 ========== */
.stApp {
    background:
        radial-gradient(ellipse at 15% 15%, rgba(80,60,140,0.25) 0%, transparent 50%),
        radial-gradient(ellipse at 85% 85%, rgba(60,100,140,0.2) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(30,30,50,0.8) 0%, #0d0d14 100%),
        #0d0d14 !important;
    min-height: 100vh !important;
}

/* 網目テクスチャ */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

/* メインコンテンツ */
.main .block-container {
    background: rgba(13,13,20,0.7) !important;
    backdrop-filter: blur(20px) !important;
    max-width: 100% !important;
    position: relative !important;
    z-index: 1 !important;
    border-left: 1px solid rgba(255,255,255,0.06) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

/* ========== スクロールバー ========== */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg,#FFD700,#FF8C00);
    border-radius: 2px;
}

/* ========== タイポグラフィ ========== */
h1 {
    color: #ffffff !important;
    font-size: 1.6rem !important;
    font-weight: 900 !important;
    margin: 0.3rem 0 0.5rem !important;
    line-height: 1.2 !important;
    text-shadow: 0 0 20px rgba(100,200,255,0.3) !important;
}
h2 {
    color: #ffffff !important;
    font-size: 1.2rem !important;
    font-weight: 800 !important;
    margin: 0.2rem 0 0.3rem !important;
}
h3 {
    color: rgba(255,255,255,0.9) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    margin: 0.2rem 0 0.2rem !important;
}
h4 {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    margin: 0.15rem 0 !important;
}
p {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.85rem !important;
    margin: 0.15rem 0 !important;
    line-height: 1.4 !important;
}

/* ========== ボタン ========== */
.stButton > button {
    background: linear-gradient(135deg, rgba(60,70,100,0.9) 0%, rgba(40,50,80,0.9) 100%) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
    padding: 0.5rem 0.8rem !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    transition: all 0.15s ease !important;
    min-height: 36px !important;
    letter-spacing: 0.02em !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(255,200,80,0.5) !important;
    box-shadow: 0 4px 16px rgba(255,160,0,0.25), inset 0 1px 0 rgba(255,255,255,0.15) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #c97d20 0%, #a85f10 50%, #c97d20 100%) !important;
    border-color: rgba(255,200,80,0.5) !important;
    box-shadow: 0 3px 12px rgba(200,120,0,0.4), inset 0 1px 0 rgba(255,220,100,0.3) !important;
    font-size: 0.88rem !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #e8921f 0%, #c97d20 100%) !important;
    box-shadow: 0 5px 20px rgba(220,140,0,0.5) !important;
}

.stButton > button:disabled {
    background: rgba(40,40,50,0.8) !important;
    color: rgba(255,255,255,0.3) !important;
    border-color: rgba(255,255,255,0.08) !important;
    opacity: 0.7 !important;
    transform: none !important;
}

/* ========== プログレスバー ========== */
.stProgress > div > div > div {
    background: linear-gradient(90deg,#ff4444,#ff6b6b) !important;
    box-shadow: 0 0 10px rgba(255,100,100,0.5) !important;
}
.stProgress {
    height: 12px !important;
    margin: 4px 0 !important;
}

/* ========== メトリック ========== */
[data-testid="stMetricValue"] {
    font-size: 1.2rem !important;
    color: #ffffff !important;
    font-weight: 900 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: rgba(255,255,255,0.55) !important;
}
[data-testid="stMetric"] {
    padding: 0.4rem 0.3rem !important;
    background: rgba(255,255,255,0.03) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

/* ========== アラート ========== */
.stAlert {
    padding: 0.6rem 0.8rem !important;
    margin: 0.3rem 0 !important;
    font-size: 0.82rem !important;
    border-radius: 8px !important;
}
.stInfo {
    background: rgba(59,130,246,0.15) !important;
    border-color: rgba(59,130,246,0.4) !important;
}
.stSuccess {
    background: rgba(34,197,94,0.15) !important;
    border-color: rgba(34,197,94,0.4) !important;
}
.stWarning {
    background: rgba(234,179,8,0.15) !important;
    border-color: rgba(234,179,8,0.4) !important;
}
.stError {
    background: rgba(239,68,68,0.15) !important;
    border-color: rgba(239,68,68,0.4) !important;
}

/* ========== エキスパンダー ========== */
details {
    background: rgba(255,255,255,0.02) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    margin: 4px 0 !important;
}
summary {
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.85) !important;
    padding: 0.5rem 0.7rem !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    cursor: pointer !important;
}
.streamlit-expanderContent {
    background: rgba(0,0,0,0.15) !important;
    padding: 0.5rem !important;
    font-size: 0.78rem !important;
    max-height: 150px !important;
    overflow-y: auto !important;
}

/* ========== 区切り線 ========== */
hr {
    margin: 0.4rem 0 !important;
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg,transparent,rgba(255,255,255,0.15),transparent) !important;
}

/* ========== カラム ========== */
[data-testid="column"] { padding: 3px !important; }

/* ========== キャプション ========== */
[data-testid="stCaptionContainer"] {
    font-size: 0.72rem !important;
    color: rgba(255,255,255,0.55) !important;
    margin: 0.1rem 0 !important;
}

/* ========== テキスト全般 ========== */
p, span, li { color: rgba(255,255,255,0.9) !important; }

/* ========== element-container ========== */
.element-container { margin: 0.1rem 0 !important; }

/* ========== セレクトボックス ========== */
.stSelectbox label { font-size: 0.8rem !important; }

/* アニメーション */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px rgba(255,200,80,0.3); }
    50% { box-shadow: 0 0 15px rgba(255,200,80,0.6); }
}
</style>
"""