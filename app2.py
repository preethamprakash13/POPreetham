import streamlit as st
import google.generativeai as genai
import time

# Configure API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Page config
st.set_page_config(page_title="Ask PO Preetham", page_icon="⚡")
st.title("⚡ Product and Healthcare Agent - Ask PO Preetham")
st.caption("Ask Preetham anything about product management, healthcare interoperability, or FHIR standards!")

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

# ─── Session state setup ───────────────────────────────────────────
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

if "last_message_time" not in st.session_state:
    st.session_state.last_message_time = 0

# ─── Sidebar with reset button & stats ────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("🔄 Reset Conversation"):
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.messages = []
        st.session_state.message_count = 0
        st.session_state.last_message_time = 0
        st.success("Conversation reset!")
        st.rerun()

    st.divider()
    st.metric("Messages sent", st.session_state.message_count)
    st.caption("Max 50 messages per session")
    st.caption("Max 500 characters per message")

# ─── Display chat history ──────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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