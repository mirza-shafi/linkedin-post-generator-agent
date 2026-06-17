"""Modern, interactive Streamlit UI for the LinkedIn Post Generator Agent."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

from linkedin_agent import LinkedInPostAgent, PostRequest
from linkedin_agent.agent import DEFAULT_MODEL, DEFAULT_TEMPERATURE

load_dotenv()

# --------------------------------------------------------------------------- #
# Page configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Styling
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      /* Pull content up — shrink Streamlit's large default top padding */
      .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 820px;
      }
      /* Hide the default header bar so content sits higher */
      header[data-testid="stHeader"] { height: 0; background: transparent; }
      /* Tighten vertical gaps between widgets */
      div[data-testid="stVerticalBlock"] { gap: 0.6rem; }
      /* App background — clean white / soft light */
      .stApp {
        background: linear-gradient(180deg, #ffffff 0%, #f4f7fb 100%);
        color: #1d2226;
      }
      /* Sidebar — light surface */
      section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e6e9ef;
      }
      /* Hero header */
      .hero {
        background: linear-gradient(135deg, #0a66c2 0%, #378fe9 100%);
        padding: 16px 24px;
        border-radius: 14px;
        color: #ffffff;
        box-shadow: 0 6px 18px rgba(10,102,194,0.18);
        margin-bottom: 14px;
      }
      .hero h1 { margin: 0; font-size: 1.5rem; font-weight: 800; }
      .hero p  { margin: 4px 0 0; opacity: 0.95; font-size: 0.9rem; }
      /* Generated post card */
      .post-card {
        background: #ffffff;
        color: #1d2226;
        border: 1px solid #e6e9ef;
        border-radius: 16px;
        padding: 24px 26px;
        line-height: 1.6;
        font-size: 1.02rem;
        box-shadow: 0 6px 20px rgba(20,40,80,0.08);
        white-space: pre-wrap;
        border-left: 5px solid #0a66c2;
      }
      /* Primary button */
      .stButton > button {
        background: #0a66c2;
        color: #fff;
        border: none;
        border-radius: 24px;
        padding: 0.55rem 1.4rem;
        font-weight: 700;
        font-size: 1rem;
        width: 100%;
        transition: all 0.15s ease-in-out;
        box-shadow: 0 4px 12px rgba(10,102,194,0.25);
      }
      .stButton > button:hover {
        background: #084e96;
        transform: translateY(-1px);
      }
      /* Context chips */
      .chip {
        display: inline-block;
        background: #eaf2fb;
        color: #0a66c2;
        border: 1px solid #d4e4f7;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 2px 6px 2px 0;
        font-size: 0.82rem;
        font-weight: 600;
      }
      /* Input fields — light, rounded */
      .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 10px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Hero
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <div class="hero">
      <h1>💼 LinkedIn Post Generator</h1>
      <p>Turn any topic into a polished, engaging LinkedIn post — in any language.
      Powered by LangChain + Google Gemini.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Sidebar — configuration
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("⚙️ Settings")

    api_key_present = bool(
        os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    )
    if api_key_present:
        st.success("API key detected ✓")
    else:
        st.error("No GOOGLE_API_KEY found")
        st.caption("Set it in a `.env` file or paste it below.")

    api_key_input = st.text_input(
        "Google Gemini API key",
        type="password",
        placeholder="Paste to override / provide a key",
        help="Leave blank to use GOOGLE_API_KEY from your environment / .env file.",
    )

    model = st.selectbox(
        "Model",
        options=[
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
            "gemini-flash-latest",
        ],
        index=0,
        help="gemini-2.5-flash is a fast, capable default.",
    )

    temperature = st.slider(
        "Creativity (temperature)",
        min_value=0.0,
        max_value=1.0,
        value=float(DEFAULT_TEMPERATURE),
        step=0.05,
        help="Lower = focused and safe. Higher = more creative and varied.",
    )

    st.divider()
    st.caption("Built with Streamlit · LangChain · Gemini")

# --------------------------------------------------------------------------- #
# Main form
# --------------------------------------------------------------------------- #
LANGUAGES = [
    "English", "Bengali", "Spanish", "French", "German", "Hindi",
    "Arabic", "Portuguese", "Mandarin Chinese", "Japanese", "Other",
]

with st.form("post_form"):
    topic = st.text_input(
        "📝 Topic",
        placeholder="e.g., AI in Healthcare, Remote Work Productivity",
    )

    col1, col2 = st.columns(2)
    with col1:
        language_choice = st.selectbox("🌐 Language", options=LANGUAGES, index=0)
    with col2:
        tone = st.text_input(
            "🎯 Tone (optional)",
            placeholder="inspirational, technical, witty…",
        )

    custom_language = ""
    if language_choice == "Other":
        custom_language = st.text_input(
            "Specify language", placeholder="e.g., Italian, Korean"
        )

    audience = st.text_input(
        "👥 Target audience (optional)",
        placeholder="e.g., startup founders, data scientists",
    )

    submitted = st.form_submit_button("✨ Generate Post")

# --------------------------------------------------------------------------- #
# Generation
# --------------------------------------------------------------------------- #
if submitted:
    language = custom_language.strip() if language_choice == "Other" else language_choice

    if not topic.strip():
        st.warning("Please enter a topic to generate a post.")
    elif not language.strip():
        st.warning("Please specify a language.")
    else:
        effective_key = api_key_input.strip() or None
        if not effective_key and not api_key_present:
            st.error(
                "No API key available. Add GOOGLE_API_KEY to your environment "
                "or paste a key in the sidebar."
            )
        else:
            try:
                with st.spinner("Crafting your LinkedIn post…"):
                    agent = LinkedInPostAgent(
                        model=model,
                        temperature=temperature,
                        api_key=effective_key,
                    )
                    request = PostRequest(
                        topic=topic,
                        language=language,
                        tone=tone or None,
                        audience=audience or None,
                    )
                    post = agent.generate(request)

                st.success("Done! Here's your post:")

                # Context chips
                chips = [f"🌐 {language}", f"🤖 {model}", f"🌡️ {temperature:.2f}"]
                if tone:
                    chips.append(f"🎯 {tone}")
                if audience:
                    chips.append(f"👥 {audience}")
                st.markdown(
                    "".join(f'<span class="chip">{c}</span>' for c in chips),
                    unsafe_allow_html=True,
                )

                # Rendered post card
                st.markdown(
                    f'<div class="post-card">{post}</div>', unsafe_allow_html=True
                )

                st.divider()
                col_a, col_b = st.columns(2)
                with col_a:
                    st.download_button(
                        "⬇️ Download as .txt",
                        data=post,
                        file_name="linkedin_post.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                with col_b:
                    with st.popover("📋 Copy text", use_container_width=True):
                        st.code(post, language=None)
                        st.caption("Select the text above and copy.")
            except Exception as exc:  # noqa: BLE001 - surface errors to the user
                st.error(f"Failed to generate post: {exc}")
else:
    st.info("Fill in a topic and language, then click **Generate Post**. 🚀")
