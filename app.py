import os
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="NarrativePro", page_icon="📝", layout="centered")

st.title("📝 NarrativePro")
st.caption("Paste field notes → generate a structured police report draft.")

# Expect your key in Streamlit Secrets as OPENAI_API_KEY
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    st.warning("Missing OPENAI_API_KEY. Add it in Streamlit Secrets to generate reports.")

client = OpenAI(api_key=api_key)

field_notes = st.text_area(
    "Field Notes",
    height=220,
    placeholder="Paste messy notes here (shorthand, timestamps, radio-style notes, etc.)..."
)

example = "02/10/26 approx 1845 hrs dispatched to Central Deck lvl 3 ref minor crash..."
if st.button("Use Example Notes"):
    st.session_state["notes"] = example

# Keep notes in session if user clicks example
if "notes" in st.session_state and not field_notes.strip():
    field_notes = st.session_state["notes"]

generate_disabled = (not api_key) or (not field_notes.strip())

if st.button("Generate Report Draft", type="primary", disabled=generate_disabled):
    system_prompt = (
        "You are a professional police report writing assistant. "
        "Rewrite the provided field notes into a structured, professional police report using objective, factual language. "
        "Maintain chronological order. Do not assume intent or mental state. Do not fabricate missing information. "
        "If important information is missing, list it under 'Missing Information / Follow-up Questions'. "
        "Use clear, concise, neutral language suitable for official documentation. "
        "Format the output using these section headings exactly:\n\n"
        "Incident Summary\n"
        "Parties Involved\n"
        "Narrative (Chronological)\n"
        "Evidence/Property\n"
        "Missing Information / Follow-up Questions"
    )

    with st.spinner("Generating..."):
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": field_notes},
            ],
            temperature=0.2,
        )

    report = resp.choices[0].message.content
    st.subheader("Report Draft")
    st.text_area("Output", value=report, height=360)
    st.download_button("Download Report (.txt)", report, file_name="report.txt")

