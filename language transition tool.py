import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import base64

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Language Translation Tool",
    page_icon="🌐",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stTextArea textarea {
        font-size: 16px;
        border-radius: 10px;
    }
    .stButton > button {
        width: 100%;
        background-color: #2563eb;
        color: white;
        font-size: 16px;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.6rem 1rem;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    .result-box {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        font-size: 17px;
        color: #1e293b;
        margin-top: 10px;
        min-height: 100px;
        line-height: 1.7;
    }
    .title-text {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle-text {
        font-size: 1rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .char-count {
        color: #94a3b8;
        font-size: 0.8rem;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ── Language list ─────────────────────────────────────────────
LANGUAGES = {
    "Auto Detect":        "auto",
    "English":            "en",
    "Spanish":            "es",
    "French":             "fr",
    "German":             "de",
    "Italian":            "it",
    "Portuguese":         "pt",
    "Russian":            "ru",
    "Chinese (Simplified)": "zh-CN",
    "Chinese (Traditional)": "zh-TW",
    "Japanese":           "ja",
    "Korean":             "ko",
    "Arabic":             "ar",
    "Hindi":              "hi",
    "Malayalam":          "ml",
    "Tamil":              "ta",
    "Telugu":             "te",
    "Bengali":            "bn",
    "Turkish":            "tr",
    "Dutch":              "nl",
    "Polish":             "pl",
    "Swedish":            "sv",
    "Greek":              "el",
    "Hebrew":             "iw",
    "Vietnamese":         "vi",
    "Thai":               "th",
    "Indonesian":         "id",
    "Malay":              "ms",
    "Ukrainian":          "uk",
    "Persian":            "fa",
}

# ── Helper: text-to-speech ────────────────────────────────────
def text_to_speech(text, lang_code):
    """Convert text to speech and return base64 audio."""
    try:
        tts = gTTS(text=text, lang=lang_code, slow=False)
        audio_path = "/tmp/translation_audio.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode()
    except Exception as e:
        return None

# ── Helper: translate ─────────────────────────────────────────
def translate_text(text, source_lang, target_lang):
    """Translate text using Google Translator."""
    try:
        translator = GoogleTranslator(
            source=source_lang,
            target=target_lang
        )
        result = translator.translate(text)
        return result, None
    except Exception as e:
        return None, str(e)

# ── UI ────────────────────────────────────────────────────────
st.markdown('<p class="title-text">🌐 Language Translator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Translate text across 25+ languages instantly using Google Translate API</p>', unsafe_allow_html=True)

# Language selectors
col1, col_swap, col2 = st.columns([5, 1, 5])

with col1:
    src_label = st.selectbox("Source Language", list(LANGUAGES.keys()), index=0)
    src_code  = LANGUAGES[src_label]

with col_swap:
    st.markdown("<br><br>", unsafe_allow_html=True)
    swap = st.button("⇄")

with col2:
    # Default target to Spanish
    tgt_keys = [k for k in LANGUAGES.keys() if k != "Auto Detect"]
    tgt_label = st.selectbox("Target Language", tgt_keys, index=0)
    tgt_code  = LANGUAGES[tgt_label]

# Handle swap
if swap:
    if src_label != "Auto Detect":
        st.session_state["swap_src"] = tgt_label
        st.session_state["swap_tgt"] = src_label
        st.rerun()

# Input text
st.markdown("#### Enter Text")
input_text = st.text_area(
    label="",
    placeholder="Type or paste text here...",
    height=150,
    max_chars=2000,
    key="input_text",
    label_visibility="collapsed"
)

char_count = len(input_text)
st.markdown(f'<p class="char-count">{char_count} / 2000 characters</p>', unsafe_allow_html=True)

# Translate button
translate_clicked = st.button("🔄 Translate", use_container_width=True)

# ── Translation logic ─────────────────────────────────────────
if "translated" not in st.session_state:
    st.session_state.translated = ""
if "tgt_code_used" not in st.session_state:
    st.session_state.tgt_code_used = "es"

if translate_clicked:
    if not input_text.strip():
        st.warning("⚠️ Please enter some text to translate.")
    elif src_code != "auto" and src_code == tgt_code:
        st.warning("⚠️ Source and target languages are the same.")
    else:
        with st.spinner("Translating..."):
            result, error = translate_text(input_text.strip(), src_code, tgt_code)
        if error:
            st.error(f"❌ Translation failed: {error}")
        else:
            st.session_state.translated    = result
            st.session_state.tgt_code_used = tgt_code

# ── Output area ───────────────────────────────────────────────
if st.session_state.translated:
    st.markdown("#### Translation")
    st.markdown(
        f'<div class="result-box">{st.session_state.translated}</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_copy, col_tts = st.columns(2)

    with col_copy:
        # Copy to clipboard via JS
        copy_js = f"""
        <textarea id="copy_area" style="opacity:0;position:absolute;">{st.session_state.translated}</textarea>
        <button onclick="
            var t=document.getElementById('copy_area');
            t.select();
            document.execCommand('copy');
            this.innerText='✅ Copied!';
            setTimeout(()=>this.innerText='📋 Copy Translation',2000);
        " style="
            width:100%; padding:10px; border-radius:10px;
            background:#f1f5f9; border:1px solid #cbd5e1;
            font-size:15px; cursor:pointer; font-weight:600;
            color:#1e293b;
        ">📋 Copy Translation</button>
        """
        st.markdown(copy_js, unsafe_allow_html=True)

    with col_tts:
        if st.button("🔊 Listen (Text-to-Speech)", use_container_width=True):
            # gTTS doesn't support zh-CN code — fix it
            tts_lang = st.session_state.tgt_code_used
            if tts_lang == "zh-CN":
                tts_lang = "zh"
            elif tts_lang == "zh-TW":
                tts_lang = "zh-TW"

            with st.spinner("Generating audio..."):
                audio_b64 = text_to_speech(st.session_state.translated, tts_lang)
            if audio_b64:
                audio_html = f"""
                <audio autoplay controls style="width:100%;margin-top:8px;border-radius:8px;">
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
            else:
                st.warning("Audio not supported for this language.")

# ── Footer ────────────────────────────────────────────────────
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#94a3b8;font-size:13px;">'
    'CodeAlpha AI Internship — Task 1: Language Translation Tool | Built with Streamlit + Google Translate API'
    '</p>',
    unsafe_allow_html=True
)
