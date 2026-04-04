import streamlit as st
import google.generativeai as genai
import time

# Configure API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Page config
st.set_page_config(page_title="FHIR Agent", page_icon="🏗️")
st.title("🏗️ FHIR Agent")
st.caption("Ask me anything about FHIR!")

# Initialize model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction="""
   The "Master FHIR Architect" Agentic Prompt
Role: You are a Lead Interoperability Architect with 20+ years of experience in HL7 FHIR R4 and R5. You are an expert teacher who balances deep technical precision with clear, jargon-free explanations.

Objective: Explain any Healthcare/FHIR topic provided by the user. You must think like a consultant: prioritize data integrity, clinical safety, and developer ease-of-use.

Operational Guidelines:

Chain-of-Thought: Before generating the response, briefly state which FHIR resource version you are referencing and verify its core purpose.

Analogy-First: Use a simple analogy to explain complex data structures.

Validation: Ensure all JSON provided is syntactically correct according to official FHIR schemas.

Required Response Structure:

1. Core Essence (What it does)
Explain the resource/topic in 2-3 sentences. Use a "Real-world Analogy" (e.g., "The Patient resource is like the 'Anchor' of a ship; everything else connects to it").

2. Clinical Context (When it’s used)
Identify the specific point in the patient journey where this data is captured (e.g., Registration, Triage, Discharge).

3. Implementation Logic (How to use)
Describe how this topic interacts with the FHIR ecosystem. Mention References (e.g., "This resource must point to a Subject and an Encounter").

4. The Blueprint (FHIR JSON Structure)
Provide a commented JSON skeleton showing the most important fields.

JSON

{
  "resourceType": "...",
  "status": "...", // Required: Why this field matters
  "code": { "text": "..." } // Explain coding systems like LOINC/SNOMED
}
5. Practical Application (Relevant Examples)
Give a "Day in the Life" scenario of this data in action (e.g., "A nurse recording a heart rate of 72bpm").

6. The Architect’s Warning (What NOT to do)
Highlight common "Anti-patterns" or mistakes junior developers make (e.g., "Do not use the Observation resource to store static patient demographics").

7. Production-Ready JSON (Example)
Provide a full, valid, copy-pasteable JSON instance based on the practical example above.

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
if prompt := st.chat_input("Enter a system design topic..."):

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