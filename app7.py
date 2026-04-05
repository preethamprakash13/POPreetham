import streamlit as st
import google.generativeai as genai
import time

# Configure API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ask PO Preetham",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="""
    The "Product Owner Agent" Agentic Prompt
   You are Preetham, a 20-year-old Product Owner prodigy with deep hands-on experience 
in Agile, Scaled Agile Framework (SAFe), Kanban, and Extreme Programming (XP). 
You also carry extensive domain expertise in Healthcare, Pharma, and Insurance. 
You are an expert teacher who balances deep technical precision with clear, 
jargon-free explanations.

Objective: Explain any Agile, Product Ownership, or domain-specific topic provided 
by the user. You must think like a seasoned consultant: prioritize delivery value, 
team health, stakeholder alignment, and regulatory awareness where applicable.

Operational Guidelines:

  Chain-of-Thought: Before generating the response, briefly identify which 
  framework or domain lens you are applying and why it is the most relevant 
  for the user's context.

  Analogy-First: Use a simple, relatable analogy to explain complex frameworks, 
  ceremonies, or domain concepts before going deep.

  Domain Awareness: When the topic touches Healthcare, Pharma, or Insurance, 
  proactively flag relevant compliance considerations (e.g., HIPAA, GxP, FDA, 
  IRDAI) even if the user did not ask.

  Calibration: Detect the user's experience level (Beginner / Intermediate / 
  Advanced) from their language and adjust explanation depth accordingly.

Required Response Structure:

1. Core Essence (What it is)
   Explain the concept, framework, or ceremony in 2-3 sentences.
   Always include a "Real-world Analogy"
   (e.g., "The Product Backlog is like a restaurant menu — the PO is the 
   chef who decides what gets cooked this sprint based on what the customer 
   values most today").

2. Domain Context (Where it applies)
   Identify the specific industry scenario or workflow phase where this 
   concept is most relevant.
   (e.g., "In a Pharma setting, PI Planning maps directly to a drug's 
   regulatory submission milestone calendar — missing a PI goal can delay 
   an FDA filing by months").

3. Implementation Logic (How to apply it)
   Describe how this concept interacts with the broader Agile or SAFe 
   ecosystem. Call out dependencies, roles involved, and common failure 
   points.
   (e.g., "WSJF scoring only works if the Cost of Delay is honestly 
   estimated — in Insurance, a delayed claims feature has a quantifiable 
   daily financial cost, which makes WSJF extremely powerful here").

4. The Blueprint (Practical Artifact or Template)
   Provide a ready-to-use artifact — a User Story, Acceptance Criteria 
   template, PI Objective, Kanban board structure, or a framework 
   comparison table — depending on what the topic demands.

   Example format for a User Story:
EPIC        : [Epic Name]
USER STORY  : As a [persona], I want to [action], so that [outcome].
ACCEPTANCE CRITERIA:
Given [precondition]
When  [action is performed]
Then  [expected result]
DEFINITION OF DONE:
- [ ] Reviewed by PO
- [ ] Acceptance criteria signed off
- [ ] Compliance check completed (if Healthcare / Pharma / Insurance)
- [ ] No open blockers
WSJF SCORING (if applicable):
Business Value     : /10
Time Criticality   : /10
Risk Reduction     : /10
Job Size           : /10
WSJF Score         : (BV + TC + RR) / JS

5. Trade-offs & Watch-outs (What to be careful about)
   Call out at least 2 real-world pitfalls, anti-patterns, or 
   context-specific risks.
   (e.g., "In Healthcare, never define 'Done' without a compliance 
   sign-off step — shipping a feature without regulatory review can 
   trigger an audit or patient safety incident").

6. Preetham's Take (Practitioner Insight)
   Close with a sharp, experience-backed opinion or recommendation — 
   something only a practitioner who has lived through it would say.
   Keep it punchy: 2-4 sentences max.
   (e.g., "Most teams fail at SAFe not because of the framework — 
   but because leadership treats PI Planning like a calendar exercise 
   instead of a commitment ceremony. In Pharma, that attitude has 
   real consequences. Treat every PI Objective like it has an FDA 
   deadline. Because someday, it will.")

    """
)

# ── Session state init ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "message_count" not in st.session_state:
    st.session_state.message_count = 0
if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

MAX_MESSAGES   = 50
MAX_CHARS      = 500

# ── Global CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* ── Sidebar background ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #26215C 0%, #533AB7 55%, #1D9E75 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem 2rem 1rem;
}

/* ── All sidebar text white ── */
[data-testid="stSidebar"] * {
    color: #fff !important;
}

/* ── Sidebar divider ── */
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2) !important;
    margin: 0.5rem 0 !important;
}

/* ── Reset button ── */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: rgba(255,255,255,0.12) !important;
    border: 1.5px solid rgba(255,255,255,0.3) !important;
    color: #fff !important;
    border-radius: 10px !important;
    padding: 0.55rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
    transition: background 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.22) !important;
    border-color: rgba(255,255,255,0.5) !important;
}
[data-testid="stSidebar"] .stButton > button:active {
    transform: scale(0.98) !important;
}

/* ── Metric cards in sidebar ── */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255,255,255,0.10) !important;
    border: 0.5px solid rgba(255,255,255,0.2) !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    text-align: center !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #fff !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: rgba(255,255,255,0.65) !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* ── Caption text in sidebar ── */
[data-testid="stSidebar"] .stCaption {
    color: rgba(255,255,255,0.55) !important;
    font-size: 0.75rem !important;
}

/* ── Success / info alerts in sidebar ── */
[data-testid="stSidebar"] .stAlert {
    background: rgba(29,158,117,0.25) !important;
    border: 1px solid rgba(93,202,165,0.5) !important;
    border-radius: 8px !important;
    color: #9FE1CB !important;
}

/* ── Main area ── */
.main-header {
    background: linear-gradient(135deg, #26215C 0%, #533AB7 60%, #1D9E75 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.chat-bubble-user {
    background: linear-gradient(135deg, #533AB7, #7F77DD);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 0.85rem 1.2rem;
    max-width: 78%;
    margin-left: auto;
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 0.5rem;
}

.chat-bubble-assistant {
    background: #F4F3FF;
    color: #26215C;
    border-radius: 18px 18px 18px 4px;
    padding: 0.85rem 1.2rem;
    max-width: 78%;
    margin-right: auto;
    font-size: 0.92rem;
    line-height: 1.6;
    border: 1px solid #CECBF6;
    margin-bottom: 0.5rem;
}

.domain-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 99px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    margin-right: 5px;
}

/* ── Chat input ── */
[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border: 1.5px solid #CECBF6 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #7F77DD !important;
    box-shadow: 0 0 0 3px rgba(127,119,221,0.15) !important;
}

/* ── Scrollable chat area ── */
.chat-scroll {
    max-height: 62vh;
    overflow-y: auto;
    padding-right: 0.5rem;
    margin-bottom: 1rem;
}
.chat-scroll::-webkit-scrollbar { width: 4px; }
.chat-scroll::-webkit-scrollbar-track { background: transparent; }
.chat-scroll::-webkit-scrollbar-thumb {
    background: #CECBF6;
    border-radius: 99px;
}
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:

    # Agent header card
    st.markdown("""
    <div style="
        display:flex; align-items:center; gap:12px;
        padding-bottom:14px;
        border-bottom:0.5px solid rgba(255,255,255,0.2);
        margin-bottom:6px;
    ">
        <div style="
            width:46px; height:46px; border-radius:50%;
            background:rgba(255,255,255,0.15);
            border:1.5px solid rgba(255,255,255,0.35);
            display:flex; align-items:center; justify-content:center;
            font-size:22px; flex-shrink:0;
        ">🎯</div>
        <div>
            <div style="font-size:14px;font-weight:700;color:#fff;
                        letter-spacing:0.2px;">Ask PO Preetham</div>
            <div style="font-size:11px;color:rgba(255,255,255,0.6);
                        margin-top:2px;">Product Owner Agent</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Domain badges
    st.markdown("""
    <div style="display:flex;flex-wrap:wrap;gap:5px;margin:10px 0 14px;">
        <span style="background:rgba(175,169,236,0.25);border:0.5px solid rgba(175,169,236,0.5);
                     color:#EEEDFE;padding:3px 9px;border-radius:99px;font-size:10px;font-weight:600;">
            Agile
        </span>
        <span style="background:rgba(29,158,117,0.25);border:0.5px solid rgba(93,202,165,0.5);
                     color:#E1F5EE;padding:3px 9px;border-radius:99px;font-size:10px;font-weight:600;">
            SAFe
        </span>
        <span style="background:rgba(127,119,221,0.25);border:0.5px solid rgba(127,119,221,0.5);
                     color:#EEEDFE;padding:3px 9px;border-radius:99px;font-size:10px;font-weight:600;">
            Kanban
        </span>
        <span style="background:rgba(255,255,255,0.12);border:0.5px solid rgba(255,255,255,0.25);
                     color:rgba(255,255,255,0.8);padding:3px 9px;border-radius:99px;
                     font-size:10px;font-weight:600;">
            XP
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Section label
    st.markdown("""
    <div style="font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);
                letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;">
        Controls
    </div>
    """, unsafe_allow_html=True)

    # Reset button
    if st.button("🔄  Reset Conversation"):
        st.session_state.messages       = []
        st.session_state.message_count  = 0
        st.session_state.last_message_time = 0
        st.success("✅  Conversation reset!")
        time.sleep(0.8)
        st.rerun()

    st.divider()

    # Stats section label
    st.markdown("""
    <div style="font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);
                letter-spacing:1.2px;text-transform:uppercase;margin-bottom:10px;">
        Session Stats
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Messages Sent", st.session_state.message_count)
    with col2:
        remaining = MAX_MESSAGES - st.session_state.message_count
        st.metric("Remaining", max(remaining, 0))

    # Progress bar
    progress_pct = min(st.session_state.message_count / MAX_MESSAGES, 1.0)
    bar_color    = "#5DCAA5" if progress_pct < 0.7 else ("#EF9F27" if progress_pct < 0.9 else "#E24B4A")

    st.markdown(f"""
    <div style="margin:12px 0 4px;">
        <div style="background:rgba(255,255,255,0.12);border-radius:99px;height:6px;overflow:hidden;">
            <div style="width:{progress_pct*100:.1f}%;height:100%;border-radius:99px;
                        background:linear-gradient(90deg,{bar_color},#AFA9EC);
                        transition:width 0.4s ease;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;
                    font-size:10px;color:rgba(255,255,255,0.4);margin-top:5px;">
            <span>{st.session_state.message_count} used</span>
            <span>{MAX_MESSAGES} max</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Limits section
    st.markdown("""
    <div style="font-size:10px;font-weight:600;color:rgba(255,255,255,0.45);
                letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;">
        Limits
    </div>
    <div style="background:rgba(255,255,255,0.07);border:0.5px solid rgba(255,255,255,0.15);
                border-radius:10px;padding:10px 12px;display:flex;flex-direction:column;gap:7px;">
        <div style="display:flex;align-items:center;gap:8px;font-size:11px;
                    color:rgba(255,255,255,0.65);">
            <div style="width:7px;height:7px;border-radius:50%;
                        background:#AFA9EC;flex-shrink:0;"></div>
            Max 50 messages per session
        </div>
        <div style="display:flex;align-items:center;gap:8px;font-size:11px;
                    color:rgba(255,255,255,0.65);">
            <div style="width:7px;height:7px;border-radius:50%;
                        background:#5DCAA5;flex-shrink:0;"></div>
            Max 500 characters per message
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top:2rem;text-align:center;font-size:10px;
                color:rgba(255,255,255,0.28);padding-top:10px;
                border-top:0.5px solid rgba(255,255,255,0.1);">
        Healthcare · Pharma · Insurance
    </div>
    """, unsafe_allow_html=True)


# ── MAIN AREA ────────────────────────────────────────────────────────────────────

# Header banner
st.markdown("""
<div class="main-header">
    <div style="width:56px;height:56px;border-radius:50%;
                background:rgba(255,255,255,0.18);
                border:2px solid rgba(255,255,255,0.4);
                display:flex;align-items:center;justify-content:center;
                font-size:26px;flex-shrink:0;">🎯</div>
    <div>
        <div style="font-size:1.4rem;font-weight:700;color:#fff;
                    letter-spacing:0.2px;">Ask PO Preetham</div>
        <div style="font-size:0.85rem;color:rgba(255,255,255,0.65);margin-top:3px;">
            Your expert Product Owner · Agile · SAFe · Kanban · XP
        </div>
        <div style="display:flex;gap:8px;margin-top:8px;flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.15);color:#fff;
                         padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;">
                🏥 Healthcare
            </span>
            <span style="background:rgba(255,255,255,0.15);color:#fff;
                         padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;">
                💊 Pharma
            </span>
            <span style="background:rgba(255,255,255,0.15);color:#fff;
                         padding:2px 10px;border-radius:99px;font-size:11px;font-weight:600;">
                🛡️ Insurance
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Welcome message (shown when no messages)
if not st.session_state.messages:
    st.markdown("""
    <div style="
        background: #F4F3FF;
        border: 1px solid #CECBF6;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        text-align: center;
    ">
        <div style="font-size:2rem;margin-bottom:0.5rem;">👋</div>
        <div style="font-size:1rem;font-weight:600;color:#26215C;margin-bottom:0.4rem;">
            Hey! I'm Preetham, your PO Agent.
        </div>
        <div style="font-size:0.85rem;color:#534AB7;line-height:1.6;">
            Ask me anything about <strong>Agile</strong>, <strong>SAFe</strong>,
            <strong>Kanban</strong>, <strong>XP</strong>, or domain topics in
            <strong>Healthcare</strong>, <strong>Pharma</strong>, and
            <strong>Insurance</strong>.
        </div>
        <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin-top:1rem;">
            <span style="background:#EEEDFE;color:#3C3489;padding:5px 14px;
                         border-radius:99px;font-size:12px;font-weight:600;
                         border:1px solid #CECBF6;">
                💡 Explain PI Planning
            </span>
            <span style="background:#E1F5EE;color:#0F6E56;padding:5px 14px;
                         border-radius:99px;font-size:12px;font-weight:600;
                         border:1px solid #9FE1CB;">
                📋 Write a User Story
            </span>
            <span style="background:#FAECE7;color:#993C1D;padding:5px 14px;
                         border-radius:99px;font-size:12px;font-weight:600;
                         border:1px solid #F5C4B3;">
                🔢 How does WSJF work?
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div class="chat-bubble-user">{msg["content"]}</div>
            """, unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🎯"):
            st.markdown(f"""
            <div class="chat-bubble-assistant">{msg["content"]}</div>
            """, unsafe_allow_html=True)

# ─── Chat input ────────────────────────────────────────────────────
if prompt := st.chat_input("Enter any product management or healthcare topic..."):

    # Guardrail 1 — Empty input check
    if not prompt.strip():
        st.warning("⚠️ Please enter a topic!")
        st.stop()

    # Guardrail 2 — Input length limit
    if len(prompt) > 500:
        st.warning(f"⚠️ Your message is {len(prompt)} characters. Please keep it under 500!")
        st.stop()

    # Guardrail 3 — Rate limiting (max 1 message per 3 seconds)
    current_time = time.time()
    time_since_last = current_time - st.session_state.last_message_time
    if time_since_last < 3:
        st.warning(f"⚠️ Slow down! Please wait {3 - int(time_since_last)} seconds before sending again.")
        st.stop()

    # Guardrail 4 — Max messages per session
    if st.session_state.message_count >= 50:
        st.error("⚠️ You've reached the 50 message limit. Please reset the conversation!")
        st.stop()

    # Update tracking
    st.session_state.last_message_time = current_time
    st.session_state.message_count += 1

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Quota exceeded. Please wait a moment and try again.")
                else:
                    st.error(f"⚠️ An error occurred: {e}")
