import sys
from pathlib import Path

# Ensure the project root is importable when Streamlit runs app/main.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.prisma import transcribe_audio
import html as _html
import urllib.parse
import uuid
from datetime import datetime

import streamlit as st

# =====================================================================
#  VACHAN — Work, Documented.
#  Single-file Streamlit app. Paste over app.py and run:  streamlit run app.py
# =====================================================================

st.set_page_config(
    page_title="VACHAN — Work, Documented.",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# STATE
# ---------------------------------------------------------------------
if "agreements" not in st.session_state:
    st.session_state.agreements = []
if "navigation" not in st.session_state:
    st.session_state.navigation = "Overview"
# Safe programmatic navigation (must run BEFORE the sidebar radio is created)
if "_goto" in st.session_state:
    st.session_state.navigation = st.session_state.pop("_goto")


def esc(x):
    return _html.escape(str(x or ""))


def H(s: str):
    """Render HTML safely through st.markdown (strips indentation / blank lines
    so Markdown never mistakes it for a code block)."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def goto(page: str):
    st.session_state["_goto"] = page
    st.rerun()


# ---------------------------------------------------------------------
# DESIGN SYSTEM
# ---------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

:root{
  --bg:#080A0F; --surface:#10141C; --surface2:#171C27;
  --border:rgba(255,255,255,.075); --text:#F5F5F7; --muted:#8F98A8;
  --o1:#FF6B2C; --o2:#FF8547; --o3:#FFB27F; --green:#3DDC97; --amber:#FFC857;
}
*{font-family:'DM Sans',sans-serif;}
html{scroll-behavior:smooth;}

/* ---------- Background: aurora + grid + noise ---------- */
.stApp{
  background:
    radial-gradient(ellipse 60% 45% at 90% -5%, rgba(255,107,44,.18), transparent 60%),
    radial-gradient(ellipse 50% 40% at -5% 85%, rgba(255,107,44,.08), transparent 60%),
    radial-gradient(ellipse 40% 30% at 50% 110%, rgba(80,120,255,.07), transparent 60%),
    var(--bg);
  color:var(--text);
}
.stApp::before{
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:
    linear-gradient(rgba(255,255,255,.022) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.022) 1px, transparent 1px);
  background-size:56px 56px;
  mask-image:radial-gradient(ellipse at 50% 20%, #000 20%, transparent 75%);
  -webkit-mask-image:radial-gradient(ellipse at 50% 20%, #000 20%, transparent 75%);
}
#MainMenu,
footer {
    visibility: hidden;
}

header[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stToolbar"]{display:none;}
.block-container{max-width:1480px; padding:2rem 3rem 4rem; position:relative; z-index:1;
  animation:pageEnter .7s cubic-bezier(.2,.7,.2,1) both;}
@keyframes pageEnter{from{opacity:0; transform:translateY(16px);} to{opacity:1; transform:none;}}
::-webkit-scrollbar{width:9px;} ::-webkit-scrollbar-thumb{background:#252C3A; border-radius:9px;}
::selection{background:rgba(255,133,71,.35);}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#131824 0%,#0C0F16 100%);
  border-right:1px solid rgba(255,255,255,.06);
}
[data-testid="stSidebar"] .block-container{padding:1.8rem 1.15rem; animation:none;}
.brand{display:flex; align-items:center; gap:12px;}
.brand-mark{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;
  background:linear-gradient(135deg,var(--o1),var(--o3)); color:#1a0e07; font-family:'Manrope'; font-weight:800; font-size:21px;
  box-shadow:0 8px 26px rgba(255,107,44,.35); animation:markGlow 3.5s ease-in-out infinite;}
@keyframes markGlow{0%,100%{box-shadow:0 8px 24px rgba(255,107,44,.30);}50%{box-shadow:0 8px 38px rgba(255,107,44,.55);}}
.brand-name{font-family:'Manrope'; font-size:24px; font-weight:800; letter-spacing:4px; color:#fff; line-height:1;}
.brand-name span{color:var(--o2);}
.brand-sub{color:#7E8797; font-size:9px; letter-spacing:2px; margin-top:5px; font-weight:600;}
.sidebar-label{font-size:10px; letter-spacing:2px; color:#6E7889; font-weight:700; margin:26px 0 10px;}

[data-testid="stSidebar"] [data-testid="stRadio"]>div{gap:6px;}
[data-testid="stSidebar"] [data-testid="stRadio"] label{
  background:transparent; border:1px solid transparent; border-radius:12px; padding:11px 13px;
  transition:all .25s cubic-bezier(.2,.7,.2,1); width:100%;}
[data-testid="stSidebar"] [data-testid="stRadio"] label>div:first-child{display:none;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(255,133,71,.08); border-color:rgba(255,133,71,.16); transform:translateX(4px);}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked){
  background:linear-gradient(100deg,rgba(255,133,71,.22),rgba(255,133,71,.05));
  border-color:rgba(255,133,71,.3); box-shadow:inset 3px 0 0 var(--o2);}
[data-testid="stSidebar"] [data-testid="stRadio"] label p{color:#CDD2DB; font-size:13.5px; font-weight:600;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p{color:#FFB27F;}

.powered{padding:14px; background:linear-gradient(145deg,#171D29,#12161F); border:1px solid #273141; border-radius:14px;}
.powered .t{color:#FFB27F; font-size:12px; font-weight:700; letter-spacing:.5px;}
.powered .d{font-size:10.5px; color:#8F98A8; margin-top:6px; line-height:1.7;}
.powered .s{margin-top:12px; color:#A5ADBA; font-size:9px; letter-spacing:1px; display:flex; align-items:center; gap:8px;}
.pulse{width:7px;height:7px;border-radius:50%;background:var(--amber);position:relative;display:inline-block;}
.pulse:after{content:"";position:absolute;inset:-4px;border-radius:50%;border:1px solid var(--amber);animation:ping 1.8s ease-out infinite;}
@keyframes ping{0%{transform:scale(.5);opacity:.9;}100%{transform:scale(1.9);opacity:0;}}
.sidebar-footer{color:#5F6978; font-size:9.5px; line-height:1.9; letter-spacing:.4px;}

/* ---------- Typography ---------- */
.eyebrow{color:var(--o2); font-size:10.5px; font-weight:800; letter-spacing:2.4px; text-transform:uppercase;
  display:flex; align-items:center; gap:10px;}
.eyebrow:before{content:""; width:22px; height:1px; background:var(--o2);}
.page-title{font-family:'Manrope'; font-size:38px; font-weight:800; letter-spacing:-1.6px; margin:10px 0 6px;
  background:linear-gradient(90deg,#fff,#FFD3B8); -webkit-background-clip:text; background-clip:text; color:transparent;}
.page-subtitle{color:var(--muted); font-size:14.5px; line-height:1.7;}
.section-title{font-family:'Manrope'; color:#F1F2F4; font-size:19px; font-weight:700; letter-spacing:-.4px; margin:38px 0 16px;
  display:flex; align-items:center; gap:12px;}
.section-title:after{content:""; flex:1; height:1px; background:linear-gradient(90deg,rgba(255,255,255,.09),transparent);}

/* ---------- Hero ---------- */
.hero{position:relative; overflow:hidden; border-radius:26px; padding:52px 52px; margin:18px 0 8px; min-height:330px;
  background:
    radial-gradient(circle at 82% 35%, rgba(255,107,44,.30), transparent 34%),
    radial-gradient(circle at 10% 110%, rgba(255,107,44,.12), transparent 40%),
    linear-gradient(125deg,#1C2432 0%,#141922 55%,#2A1D17 100%);
  border:1px solid rgba(255,154,105,.22); box-shadow:0 24px 80px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.06);
  display:flex; align-items:center; justify-content:space-between; gap:30px;}
.hero:before{content:""; position:absolute; inset:0;
  background:linear-gradient(115deg,transparent 40%,rgba(255,200,160,.08) 50%,transparent 60%);
  background-size:250% 100%; animation:sheen 6s ease-in-out infinite;}
@keyframes sheen{0%{background-position:150% 0;}100%{background-position:-100% 0;}}
.orb{position:absolute; border-radius:50%; filter:blur(2px); pointer-events:none;}
.orb.a{width:300px;height:300px;right:-60px;top:-120px;border:1px solid rgba(255,157,108,.2);
  box-shadow:0 0 0 28px rgba(255,157,108,.03),0 0 0 60px rgba(255,157,108,.02); animation:floatOrb 8s ease-in-out infinite;}
.orb.b{width:12px;height:12px;right:30%;bottom:60px;background:var(--o2);box-shadow:0 0 24px var(--o1); animation:drift 5s ease-in-out infinite;}
.orb.c{width:7px;height:7px;right:46%;top:50px;background:var(--o3);box-shadow:0 0 16px var(--o2); animation:drift 6.5s ease-in-out infinite reverse;}
@keyframes floatOrb{0%,100%{transform:translateY(0) scale(1);}50%{transform:translateY(18px) scale(1.05);}}
@keyframes drift{0%,100%{transform:translate(0,0);}50%{transform:translate(-14px,-18px);}}
.hero-content{position:relative; z-index:2; max-width:560px;}
.hero-tag{display:inline-flex; align-items:center; gap:9px; border:1px solid rgba(255,160,110,.28); background:rgba(255,133,71,.10);
  border-radius:30px; color:#FFB988; padding:7px 14px; font-size:10px; letter-spacing:1.4px; font-weight:700;}
.hero h1{font-family:'Manrope'; font-size:clamp(36px,4.2vw,56px); font-weight:800; letter-spacing:-2.6px; line-height:1.06; color:#fff; margin:18px 0 16px;}
.hero h1 span{background:linear-gradient(90deg,var(--o2),#FFD0AD,var(--o2)); background-size:200% auto;
  -webkit-background-clip:text; background-clip:text; color:transparent; animation:shine 4s linear infinite;}
@keyframes shine{to{background-position:200% center;}}
.hero p{color:#AEB9C6; font-size:15px; line-height:1.85; max-width:480px; margin:0;}
.hero-visual{position:relative; z-index:2; width:330px; flex-shrink:0;}
.phone{background:linear-gradient(160deg,#1B2230,#10141C); border:1px solid rgba(255,255,255,.1); border-radius:22px; padding:18px;
  box-shadow:0 30px 60px rgba(0,0,0,.45); transform:rotate(3deg); animation:bob 6s ease-in-out infinite;}
@keyframes bob{0%,100%{transform:rotate(3deg) translateY(0);}50%{transform:rotate(1.5deg) translateY(-10px);}}
.phone .row{display:flex; align-items:center; justify-content:space-between; font-size:9px; letter-spacing:1.4px; color:#8F98A8; font-weight:700;}
.rec{display:flex; align-items:center; gap:7px; color:#FF6B6B;}
.rec i{width:7px;height:7px;border-radius:50%;background:#FF5B5B;animation:blink 1.2s infinite;}
@keyframes blink{50%{opacity:.2;}}
.wave{display:flex; align-items:center; gap:3px; height:54px; margin:16px 0;}
.wave b{flex:1; background:linear-gradient(180deg,var(--o3),var(--o1)); border-radius:3px; min-height:5px; animation:wave 1.1s ease-in-out infinite;}
@keyframes wave{0%,100%{height:12%;}50%{height:100%;}}
.bubble{background:rgba(255,255,255,.04); border:1px solid rgba(255,255,255,.07); border-radius:10px; padding:9px 11px; font-size:11px; color:#C3CAD5; line-height:1.55; margin-top:8px;}
.bubble em{color:var(--o3); font-style:normal; font-weight:700;}
.chipline{display:flex; gap:6px; flex-wrap:wrap; margin-top:10px;}
.chip{font-size:9.5px; font-weight:700; letter-spacing:.6px; padding:4px 9px; border-radius:20px;
  background:rgba(61,220,151,.1); color:var(--green); border:1px solid rgba(61,220,151,.25);}
.chip.o{background:rgba(255,133,71,.1); color:var(--o3); border-color:rgba(255,133,71,.28);}

/* ---------- Language marquee ---------- */
.marquee{overflow:hidden; border-top:1px solid var(--border); border-bottom:1px solid var(--border); padding:13px 0; margin:6px 0 4px;
  mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);}
.marquee-track{display:flex; gap:46px; width:max-content; animation:scroll 32s linear infinite;}
.marquee-track span{color:#6E7889; font-size:12px; letter-spacing:2.2px; font-weight:700; white-space:nowrap;}
.marquee-track span:nth-child(3n){color:#B88D74;}
@keyframes scroll{to{transform:translateX(-50%);}}

/* ---------- Cards ---------- */
.metric-card,.feature-card,.content-card,.agr-card{
  position:relative; background:linear-gradient(150deg,#171D28,#10151D); border:1px solid var(--border); border-radius:18px; padding:22px;
  transition:transform .35s cubic-bezier(.2,.7,.2,1), border-color .35s, box-shadow .35s; overflow:hidden;
  animation:rise .7s cubic-bezier(.2,.7,.2,1) both;}
.metric-card:before,.feature-card:before,.content-card:before,.agr-card:before{
  content:""; position:absolute; inset:0; opacity:0; transition:opacity .35s;
  background:radial-gradient(400px circle at 100% 0%, rgba(255,133,71,.13), transparent 55%);}
.metric-card:hover,.feature-card:hover,.content-card:hover,.agr-card:hover{
  transform:translateY(-6px); border-color:rgba(255,133,71,.42); box-shadow:0 18px 44px rgba(0,0,0,.35), 0 0 28px rgba(255,133,71,.07);}
.metric-card:hover:before,.feature-card:hover:before,.content-card:hover:before,.agr-card:hover:before{opacity:1;}
@keyframes rise{from{opacity:0; transform:translateY(22px) scale(.98);} to{opacity:1; transform:none;}}
[data-testid="column"]:nth-child(1) .metric-card,[data-testid="column"]:nth-child(1) .feature-card{animation-delay:.05s;}
[data-testid="column"]:nth-child(2) .metric-card,[data-testid="column"]:nth-child(2) .feature-card{animation-delay:.18s;}
[data-testid="column"]:nth-child(3) .metric-card,[data-testid="column"]:nth-child(3) .feature-card{animation-delay:.31s;}

.metric-card{min-height:138px;}
.metric-top{display:flex; align-items:center; justify-content:space-between; position:relative;}
.metric-icon{width:38px;height:38px;display:grid;place-items:center;background:rgba(255,133,71,.12);border:1px solid rgba(255,133,71,.2);border-radius:12px;color:#FFB27F;font-size:16px;}
.metric-label{color:#929CAA; font-size:10.5px; font-weight:700; letter-spacing:1.1px;}
.metric-value{font-family:'Manrope'; color:#fff; font-size:42px; font-weight:800; letter-spacing:-1.5px; margin-top:16px; line-height:1; position:relative; animation:pop .8s cubic-bezier(.2,1.4,.4,1) both .3s;}
@keyframes pop{from{opacity:0; transform:scale(.6);} to{opacity:1; transform:none;}}
.metric-bar{height:3px; background:#1F2633; border-radius:3px; margin-top:16px; overflow:hidden; position:relative;}
.metric-bar i{display:block; height:100%; background:linear-gradient(90deg,var(--o1),var(--o3)); border-radius:3px; animation:grow 1.2s cubic-bezier(.2,.7,.2,1) both .4s;}
@keyframes grow{from{width:0;}}

.feature-card{min-height:210px; padding:24px;}
.feature-number{color:#FF9C67; font-size:10.5px; font-weight:800; letter-spacing:1.8px; font-family:'JetBrains Mono',monospace; position:relative;}
.feature-icon{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;font-size:22px;margin:18px 0 14px;
  background:linear-gradient(135deg,rgba(255,133,71,.2),rgba(255,133,71,.05)); border:1px solid rgba(255,133,71,.22); position:relative;}
.feature-title{font-family:'Manrope'; font-size:17px; font-weight:800; color:#F4F5F6; position:relative;}
.feature-desc{color:#939EAC; font-size:12.5px; line-height:1.75; margin-top:8px; position:relative;}

/* ---------- Agreement cards ---------- */
.agr-card{padding:20px 22px; margin-bottom:6px; animation-delay:.05s;}
.agr-top{display:flex; justify-content:space-between; align-items:flex-start; gap:14px; position:relative;}
.agr-cust{font-family:'Manrope'; font-size:17px; font-weight:800; color:#fff;}
.agr-svc{color:#9BA5B3; font-size:12.5px; margin-top:3px;}
.agr-price{font-family:'Manrope'; font-size:22px; font-weight:800; color:#FFB27F; text-align:right; white-space:nowrap;}
.agr-meta{display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-top:16px; padding-top:14px; border-top:1px dashed rgba(255,255,255,.08); position:relative;}
.agr-meta div{font-size:11.5px; color:#C8CFDA;}
.agr-meta small{display:block; color:#6E7889; font-size:9px; letter-spacing:1.4px; font-weight:700; margin-bottom:4px;}
.pill{display:inline-flex; align-items:center; gap:6px; padding:4px 11px; border-radius:20px; font-size:9.5px; font-weight:800; letter-spacing:1px;}
.pill.pending{background:rgba(255,200,87,.1); color:var(--amber); border:1px solid rgba(255,200,87,.3);}
.pill.confirmed{background:rgba(61,220,151,.1); color:var(--green); border:1px solid rgba(61,220,151,.3);}
.pill:before{content:""; width:6px;height:6px;border-radius:50%;background:currentColor;}
.agr-id{font-family:'JetBrains Mono',monospace; font-size:10px; color:#5F6978; margin-top:6px; text-align:right;}

/* ---------- Empty ---------- */
.empty-state{border:1px dashed #384355; border-radius:20px; background:rgba(18,23,31,.7); text-align:center; padding:50px 20px; position:relative; overflow:hidden;}
.empty-state:before{content:""; position:absolute; inset:0; background:radial-gradient(circle at 50% 0%, rgba(255,133,71,.09), transparent 60%);}
.empty-symbol{position:relative; margin:0 auto 16px; width:62px;height:62px;display:grid;place-items:center;border-radius:20px;background:rgba(255,133,71,.1);color:#FFB27F;font-size:26px;
  border:1px solid rgba(255,133,71,.2); animation:bob2 3.2s ease-in-out infinite;}
@keyframes bob2{0%,100%{transform:translateY(0);}50%{transform:translateY(-7px);}}
.empty-title{color:#F2F3F5; font-size:17px; font-weight:700; position:relative;}
.empty-desc{color:#8E99A8; font-size:12.5px; line-height:1.85; margin-top:8px; position:relative;}

/* ---------- Buttons ---------- */
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{
  background:linear-gradient(110deg,#F26A2B,#FFA46F); color:#1A0F08 !important; border:1px solid #FF9A61; border-radius:12px;
  min-height:46px; padding:0 22px; font-weight:800; letter-spacing:.2px; transition:all .25s cubic-bezier(.2,.7,.2,1);
  box-shadow:0 6px 22px rgba(255,107,44,.18); position:relative; overflow:hidden;}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stFormSubmitButton"]>button:hover{
  transform:translateY(-3px); box-shadow:0 12px 32px rgba(255,107,44,.38); filter:brightness(1.07);}
.stButton>button:active{transform:scale(.97);}
.stButton>button:disabled{background:#1C2230; color:#5C6677 !important; border-color:#2A3242; box-shadow:none; transform:none;}
.stButton>button p,.stDownloadButton>button p,[data-testid="stFormSubmitButton"]>button p{color:#1A0F08 !important; font-weight:800;}
.stButton>button:disabled p{color:#5C6677 !important;}

/* ---------- Inputs ---------- */
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stDateInput input{
  background:#121720 !important; color:#F5F5F7 !important; border:1px solid #2C3646 !important; border-radius:12px !important; transition:all .25s;}
.stTextInput input:focus,.stTextArea textarea:focus,.stNumberInput input:focus,.stDateInput input:focus{
  border-color:var(--o2) !important; box-shadow:0 0 0 3px rgba(255,133,71,.14) !important;}
.stSelectbox div[data-baseweb="select"]>div{background:#121720 !important; border:1px solid #2C3646 !important; border-radius:12px !important;}
label,.stTextInput label,.stSelectbox label,.stTextArea label{color:#AAB2BF !important; font-size:12.5px !important; font-weight:600 !important;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px !important; border-color:rgba(255,255,255,.08) !important;
  background:linear-gradient(150deg,rgba(23,29,40,.8),rgba(16,21,29,.8)); backdrop-filter:blur(8px);}
[data-testid="stFileUploader"]{background:linear-gradient(135deg,rgba(255,133,71,.08),rgba(255,255,255,.015)); border:1px dashed rgba(255,151,99,.5);
  border-radius:16px; padding:16px; transition:all .3s;}
[data-testid="stFileUploader"]:hover{border-color:var(--o2); background:rgba(255,133,71,.11); transform:scale(1.005);}
[data-testid="stFileUploader"] section{background:transparent;}
[data-testid="stAlert"]{border-radius:12px;}
[data-testid="stForm"]{border:none !important; padding:0 !important;}
hr{border-color:var(--border) !important; margin:22px 0 !important;}
.stCaption,[data-testid="stCaptionContainer"]{color:var(--muted) !important;}

/* ---------- Stepper ---------- */
.step-line{display:flex; align-items:center; gap:12px; margin:20px 0 26px; flex-wrap:wrap;}
.step{display:flex; align-items:center; gap:9px; color:#7E8898; font-size:11px; font-weight:700; letter-spacing:.8px; transition:all .3s;}
.step.active{color:#FFB27F;} .step.done{color:var(--green);}
.step-dot{width:26px;height:26px;display:grid;place-items:center;border-radius:50%;background:#232B38;color:#AEB7C3;font-size:11px;}
.step.active .step-dot{background:rgba(255,133,71,.18); color:#FFB27F; border:1px solid rgba(255,133,71,.5); animation:ring 2s infinite;}
.step.done .step-dot{background:rgba(61,220,151,.15); color:var(--green); border:1px solid rgba(61,220,151,.4);}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(255,133,71,.45);}100%{box-shadow:0 0 0 10px rgba(255,133,71,0);}}
.step-connector{height:2px; width:42px; background:#2A3342; border-radius:2px; overflow:hidden;}
.step-connector.done{background:linear-gradient(90deg,var(--green),#2A9B6C);}

.tip{display:flex; gap:12px; align-items:flex-start; background:rgba(255,133,71,.06); border:1px solid rgba(255,133,71,.18); border-radius:14px; padding:14px 16px; margin-top:6px;}
.tip b{color:#FFB27F;} .tip span{color:#A9B2BF; font-size:12.5px; line-height:1.7;}

@media (max-width:900px){
  .block-container{padding:1.2rem 1rem 3rem;}
  .hero{flex-direction:column; padding:32px 24px; align-items:flex-start;}
  .hero-visual{width:100%;}
  .agr-meta{grid-template-columns:1fr 1fr;}
}
@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation:none !important; transition:none !important;}}
/* Restore Streamlit sidebar expand button */

header[data-testid="stHeader"] {
    visibility: visible !important;
    display: block !important;
    background: transparent !important;
}

[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 12px !important;
    left: 12px !important;
    z-index: 999999 !important;
}

[data-testid="stSidebarCollapsedControl"] button {
    color: #FFB27F !important;
    background: #171D28 !important;
    border: 1px solid #FF8547 !important;
    border-radius: 9px !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def counts():
    a = st.session_state.agreements
    total = len(a)
    pending = sum(1 for x in a if x["status"] == "Pending")
    confirmed = sum(1 for x in a if x["status"] == "Confirmed")
    return total, pending, confirmed


def share_text(a):
    lines = [
        "📋 *JOB AGREEMENT — VACHAN*",
        f"Ref: {a['id']}",
        "",
        f"Customer: {a['customer']}",
        f"Service: {a['service']}",
        f"Materials: {a['materials'] or 'Not specified'}",
        f"Agreed price: ₹{a['price']:,}",
        f"Deadline: {a['deadline']}",
        "",
        "Please reply YES to confirm these details.",
        "— Work, Documented.",
    ]
    return "\n".join(lines)


def agreement_card(a):
    pill = "confirmed" if a["status"] == "Confirmed" else "pending"
    label = "CONFIRMED" if a["status"] == "Confirmed" else "AWAITING CONFIRMATION"
    H(f"""
    <div class="agr-card">
      <div class="agr-top">
        <div>
          <div class="agr-cust">{esc(a['customer'])}</div>
          <div class="agr-svc">{esc(a['service'])}</div>
          <div style="margin-top:10px"><span class="pill {pill}">{label}</span></div>
        </div>
        <div>
          <div class="agr-price">₹{a['price']:,}</div>
          <div class="agr-id">{esc(a['id'])}</div>
        </div>
      </div>
      <div class="agr-meta">
        <div><small>MATERIALS</small>{esc(a['materials']) or '—'}</div>
        <div><small>DEADLINE</small>{esc(a['deadline'])}</div>
        <div><small>LANGUAGE · CREATED</small>{esc(a['language'])} · {esc(a['created'])}</div>
      </div>
    </div>
    """)


def add_sample():
    st.session_state.agreements.insert(0, {
        "id": "VCH-" + uuid.uuid4().hex[:6].upper(),
        "customer": "Sunita Devi",
        "phone": "",
        "service": "Kitchen tap & pipe fitting",
        "materials": "2 CP taps, 6 ft PVC pipe, sealant",
        "price": 1850,
        "deadline": "Tomorrow, 11:00 AM",
        "language": "Hinglish",
        "transcript": "",
        "status": "Pending",
        "created": datetime.now().strftime("%d %b, %I:%M %p"),
    })


# ---------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------
total, pending, confirmed = counts()

with st.sidebar:
    H("""
    <div class="brand">
      <div class="brand-mark">V</div>
      <div><div class="brand-name">VACHAN<span>.</span></div><div class="brand-sub">WORK, DOCUMENTED.</div></div>
    </div>
    """)
    H('<div class="sidebar-label">WORKSPACE</div>')

    page = st.radio(
        "Navigation",
        ["Overview", "Create Agreement", "All Agreements"],
        label_visibility="collapsed",
        key="navigation",
        format_func=lambda x: {
            "Overview": "◫    Overview",
            "Create Agreement": "＋    Create Agreement",
            "All Agreements": f"▤    All Agreements" + (f"   ·   {total}" if total else ""),
        }[x],
    )

    H('<div class="sidebar-label">POWERED BY</div>')
    H("""
    <div class="powered">
      <div class="t">✦ GNANI AI</div>
      <div class="d">Voice intelligence<br>Speech processing<br>Smart documentation</div>
      <div class="s"><span class="pulse"></span> INTEGRATION IN PROGRESS</div>
    </div>
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    H('<div class="sidebar-footer">VACHAN · BUILD 0.3.0<br>MADE FOR INDIA\'S INDEPENDENT WORKFORCE</div>')


# ---------------------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------------------
if page == "Overview":
    H('<div class="eyebrow">YOUR WORKSPACE &nbsp;/&nbsp; OVERVIEW</div>')

    bars = "".join(
        f'<b style="animation-delay:{(i * 0.09) % 1.1:.2f}s"></b>' for i in range(26)
    )
    H(f"""
    <div class="hero">
      <div class="orb a"></div><div class="orb b"></div><div class="orb c"></div>
      <div class="hero-content">
        <div class="hero-tag">✦ &nbsp;VOICE-POWERED DOCUMENTATION</div>
        <h1>Every promise.<br><span>Clearly documented.</span></h1>
        <p>Turn everyday customer conversations into structured, editable and shareable job agreements.
        Less confusion. More trust. Better work.</p>
      </div>
      <div class="hero-visual">
        <div class="phone">
          <div class="row"><span>NEW CONVERSATION</span><span class="rec"><i></i>REC</span></div>
          <div class="wave">{bars}</div>
          <div class="bubble">"Bhaiya, <em>tap fitting</em> kal tak ho jayega na? <em>₹1,850</em> final?"</div>
          <div class="chipline">
            <span class="chip">✓ SERVICE</span><span class="chip">✓ PRICE</span>
            <span class="chip o">◷ DEADLINE</span>
          </div>
        </div>
      </div>
    </div>
    """)

    items = ["HINDI", "हिन्दी", "HINGLISH", "BENGALI", "বাংলা", "ENGLISH", "PLUMBERS", "ELECTRICIANS",
             "TAILORS", "CARPENTERS", "PAINTERS", "MECHANICS", "FREELANCERS", "TUTORS"]
    spans = "".join(f"<span>{x}</span>" for x in items * 2)
    H(f'<div class="marquee"><div class="marquee-track">{spans}</div></div>')

    H('<div class="section-title">Your activity</div>')
    m1, m2, m3 = st.columns(3)
    denom = max(total, 1)
    metrics = [
        (m1, "▤", "TOTAL AGREEMENTS", total, 100 if total else 0),
        (m2, "◷", "AWAITING CONFIRMATION", pending, int(pending / denom * 100)),
        (m3, "✓", "CONFIRMED JOBS", confirmed, int(confirmed / denom * 100)),
    ]
    for col, icon, label, value, pct in metrics:
        with col:
            H(f"""
            <div class="metric-card">
              <div class="metric-top"><div class="metric-label">{label}</div><div class="metric-icon">{icon}</div></div>
              <div class="metric-value">{value}</div>
              <div class="metric-bar"><i style="width:{pct}%"></i></div>
            </div>
            """)

    H('<div class="section-title">From conversation to clarity</div>')
    c1, c2, c3 = st.columns(3)
    features = [
        (c1, "01 / CAPTURE", "🎙️", "Record the conversation",
         "Upload a customer conversation in Hindi, Hinglish, Bengali or English."),
        (c2, "02 / UNDERSTAND", "✨", "Structure the details",
         "AI helps identify services, prices, materials and agreed deadlines."),
        (c3, "03 / DOCUMENT", "📋", "Create a job record",
         "Review the details, make corrections and create a shareable record."),
    ]
    for col, number, icon, title, desc in features:
        with col:
            H(f"""
            <div class="feature-card">
              <div class="feature-number">{number}</div>
              <div class="feature-icon">{icon}</div>
              <div class="feature-title">{title}</div>
              <div class="feature-desc">{desc}</div>
            </div>
            """)

    H('<div class="section-title">Recent agreements</div>')
    if st.session_state.agreements:
        for a in st.session_state.agreements[:3]:
            agreement_card(a)
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("＋  Create another agreement", use_container_width=True, key="ov_new"):
                goto("Create Agreement")
        with b2:
            if st.button("▤  View all agreements", use_container_width=True, key="ov_all"):
                goto("All Agreements")
    else:
        H("""
        <div class="empty-state">
          <div class="empty-symbol">▤</div>
          <div class="empty-title">Your workspace is ready</div>
          <div class="empty-desc">Your documented jobs will appear here.<br>Create your first agreement to get started.</div>
        </div>
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        b1, b2 = st.columns([2, 1])
        with b1:
            if st.button("＋  Create your first agreement", use_container_width=True, key="ov_first"):
                goto("Create Agreement")
        with b2:
            if st.button("✦  Load a sample", use_container_width=True, key="ov_sample"):
                add_sample()
                st.toast("Sample agreement added", icon="✅")
                st.rerun()


# ---------------------------------------------------------------------
# CREATE AGREEMENT
# ---------------------------------------------------------------------
elif page == "Create Agreement":
    H('<div class="eyebrow">WORKSPACE &nbsp;/&nbsp; NEW AGREEMENT</div>')
    H('<div class="page-title">Create an agreement</div>')
    H('<div class="page-subtitle">Start with a conversation. Finish with clarity.</div>')

    left, right = st.columns([1.2, .8], gap="large")

    with left:
        H('<div class="section-title" style="margin-top:22px;">01 &nbsp;Conversation</div>')
        with st.container(border=True):
            language = st.selectbox(
                "Conversation language",
                ["Hindi", "Hinglish", "Bengali", "English"],
            )
            audio = st.file_uploader(
                "Upload an audio recording",
                type=["wav", "mp3", "m4a", "ogg"],
                help="Supported formats: WAV, MP3, M4A and OGG",
            )

            if audio:
                st.audio(audio)
                st.success(f"Recording ready: {audio.name}")

            if st.button("✦ Transcribe with Gnani Prisma", use_container_width=True):
                if not audio:
                    st.warning("Please upload an audio recording first.")
                else:
                    try:
                        with st.spinner("Prisma is listening to your recording..."):
                            language_codes = {
                                "Hindi": "hi-IN",
                                "Hinglish": "indic-auto",
                                "Bengali": "bn-IN",
                                "English": "en-IN",
                            }

                            result = transcribe_audio(
                                audio_bytes=audio.getvalue(),
                                filename=audio.name,
                                language_code=language_codes[language],
                            )

                            st.session_state["transcript_box"] = result["transcript"]

                        st.success("Transcription completed successfully!")
                        if result.get("detected_language"):
                            st.caption(
                                f"Detected language: {result['detected_language']}"
                            )
                    except Exception as e:
                        st.error(f"Transcription failed: {e}")

            st.caption("Powered by Gnani Prisma")

        H('<div class="section-title">02 &nbsp;Transcript</div>')
        with st.container(border=True):
            H('<div style="color:#FFB27F;font-size:11px;font-weight:700;letter-spacing:1.4px;margin-bottom:10px;">◉ &nbsp;CONVERSATION TRANSCRIPT</div>')
            transcript = st.text_area(
                "Transcript",
                placeholder="Paste or type the conversation here until Prisma transcription is live…",
                height=170,
                label_visibility="collapsed",
                key="transcript_box",
            )
            st.button("✦  Transcribe conversation", disabled=True, use_container_width=True)
            st.caption("Prisma transcription will be activated after API integration. Until then, paste the text above.")

        H('<div class="section-title">03 &nbsp;Agreement details</div>')
        with st.container(border=True):
            with st.form("agreement_form", clear_on_submit=True):
                f1, f2 = st.columns(2)
                customer = f1.text_input("Customer name *", placeholder="e.g. Sunita Devi")
                phone = f2.text_input("Customer phone (optional)", placeholder="e.g. 98XXXXXXXX")
                service = st.text_input("Service / job *", placeholder="e.g. Kitchen tap & pipe fitting")
                materials = st.text_area("Materials (optional)", placeholder="e.g. 2 taps, 6 ft pipe", height=80)
                g1, g2 = st.columns(2)
                price = g1.number_input("Agreed price (₹) *", min_value=0, step=50, value=0)
                deadline = g2.text_input("Deadline *", placeholder="e.g. Tomorrow, 11 AM")
                st.caption("Anything not agreed in the conversation can be left blank — it stays marked as missing.")
                submitted = st.form_submit_button("✓  Save agreement", use_container_width=True)

            if submitted:
                missing = [n for n, v in [("customer name", customer.strip()), ("service", service.strip()),
                                          ("deadline", deadline.strip())] if not v]
                if missing or price <= 0:
                    if price <= 0:
                        missing.append("price")
                    st.error("Please fill in: " + ", ".join(missing) + ".")
                else:
                    st.session_state.agreements.insert(0, {
                        "id": "VCH-" + uuid.uuid4().hex[:6].upper(),
                        "customer": customer.strip(),
                        "phone": phone.strip(),
                        "service": service.strip(),
                        "materials": materials.strip(),
                        "price": int(price),
                        "deadline": deadline.strip(),
                        "language": language,
                        "transcript": transcript.strip(),
                        "status": "Pending",
                        "created": datetime.now().strftime("%d %b, %I:%M %p"),
                    })
                    st.toast("Agreement saved", icon="✅")
                    st.session_state["_goto"] = "All Agreements"
                    st.rerun()

    with right:
        # live stepper
        step = 1
        if audio or transcript.strip():
            step = 3
        stages = ["CAPTURE", "TRANSCRIBE", "REVIEW", "SAVE"]
        parts = []
        for i, name in enumerate(stages, 1):
            cls = "done" if i < step else ("active" if i == step else "")
            dot = "✓" if i < step else str(i)
            parts.append(f'<div class="step {cls}"><div class="step-dot">{dot}</div>{name}</div>')
            if i < len(stages):
                parts.append(f'<div class="step-connector {"done" if i < step else ""}"></div>')
        H(f'<div class="step-line" style="margin-top:22px;">{"".join(parts)}</div>')

        H('<div class="section-title" style="margin-top:14px;">What happens next?</div>')
        H("""
        <div class="content-card" style="margin-bottom:14px;">
          <div class="feature-icon" style="margin-top:0">🎙️</div>
          <div class="feature-title">Speech to text</div>
          <div class="feature-desc">Your recording is converted into readable text while preserving the original conversation.</div>
        </div>
        <div class="content-card" style="margin-bottom:14px;">
          <div class="feature-icon" style="margin-top:0">✨</div>
          <div class="feature-title">Understand the agreement</div>
          <div class="feature-desc">Important job details are organised into a clear structure. Missing details stay marked as missing.</div>
        </div>
        <div class="content-card">
          <div class="feature-icon" style="margin-top:0">📲</div>
          <div class="feature-title">Review &amp; share</div>
          <div class="feature-desc">Check every detail, make edits and send the job record to your customer on WhatsApp for confirmation.</div>
        </div>
        <div class="tip"><b>💡</b><span>Tip: agree on <b>price, materials and deadline</b> out loud in the recording — they become the three most important lines of the record.</span></div>
        """)


# ---------------------------------------------------------------------
# ALL AGREEMENTS
# ---------------------------------------------------------------------
elif page == "All Agreements":
    H('<div class="eyebrow">WORKSPACE &nbsp;/&nbsp; RECORDS</div>')
    H('<div class="page-title">All agreements</div>')
    H('<div class="page-subtitle">Every job. Every commitment. All in one place.</div>')
    st.markdown("<br>", unsafe_allow_html=True)

    s1, s2 = st.columns([2, 1])
    with s1:
        query = st.text_input("Search agreements", placeholder="Search by customer or service…")
    with s2:
        status_f = st.selectbox("Filter by status", ["All statuses", "Pending", "Confirmed"])

    data = st.session_state.agreements
    q = query.strip().lower()
    shown = [
        a for a in data
        if (status_f == "All statuses" or a["status"] == status_f)
        and (not q or q in a["customer"].lower() or q in a["service"].lower())
    ]

    st.markdown("<br>", unsafe_allow_html=True)

    if not data:
        H("""
        <div class="empty-state">
          <div class="empty-symbol">▤</div>
          <div class="empty-title">No agreements created yet</div>
          <div class="empty-desc">Once you create and save a job record, it will appear here.<br>Your work history starts with the first agreement.</div>
        </div>
        """)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("＋  Create an agreement", use_container_width=True):
            goto("Create Agreement")
    elif not shown:
        H("""
        <div class="empty-state">
          <div class="empty-symbol">⌕</div>
          <div class="empty-title">No matching agreements</div>
          <div class="empty-desc">Try a different search or status filter.</div>
        </div>
        """)
    else:
        for a in shown:
            agreement_card(a)
            b1, b2, b3, b4 = st.columns([1.1, 1, 1, .6])
            with b1:
                if a["status"] == "Pending":
                    if st.button("✓  Mark confirmed", key=f"c_{a['id']}", use_container_width=True):
                        a["status"] = "Confirmed"
                        st.toast("Marked as confirmed", icon="✅")
                        st.rerun()
                else:
                    if st.button("↺  Mark pending", key=f"p_{a['id']}", use_container_width=True):
                        a["status"] = "Pending"
                        st.rerun()
            with b2:
                wa = "https://wa.me/"
                digits = "".join(ch for ch in a.get("phone", "") if ch.isdigit())
                if digits:
                    wa += ("91" + digits[-10:])
                wa += "?text=" + urllib.parse.quote(share_text(a))
                st.link_button("📲  WhatsApp", wa, use_container_width=True)
            with b3:
                st.download_button(
                    "⬇  Download",
                    share_text(a).replace("*", ""),
                    file_name=f"{a['id']}.txt",
                    key=f"d_{a['id']}",
                    use_container_width=True,
                )
            with b4:
                if st.button("🗑", key=f"x_{a['id']}", use_container_width=True, help="Delete"):
                    st.session_state.agreements = [x for x in data if x["id"] != a["id"]]
                    st.rerun()
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)