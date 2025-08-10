import os
import json
import datetime as dt
from pathlib import Path

import streamlit as st

from utils.file_utils import read_file_text, save_text
from utils.text_utils import clean_text
from utils.openai_utils import generate_text, ModelConfig

BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts"
EXPORTS_DIR = BASE_DIR / "exports"
SAMPLE_DIR = BASE_DIR / "sample_data"

st.set_page_config(page_title="Smart Resume & Cover Letter Generator", layout="wide")


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_export(name: str, content: str) -> str:
    timestamp = dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    filename = f"{timestamp}-{name}"
    out_path = EXPORTS_DIR / filename
    save_text(str(out_path), content)
    return str(out_path)


st.title("Smart Resume & Cover Letter Generator")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    temperature = st.slider("Temperature", 0.0, 1.2, 0.7, 0.1)
    max_tokens = st.number_input("Max tokens (0=auto)", value=0, min_value=0, step=100)
    config = ModelConfig(model=model, temperature=float(temperature), max_tokens=None if max_tokens == 0 else int(max_tokens))
    st.markdown("API key must be set in environment as `OPENAI_API_KEY`.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Resume Upload")
    resume_file = st.file_uploader("Upload resume (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="resume")
    resume_text = ""
    if resume_file is not None:
        tmp_path = BASE_DIR / ("tmp_resume_" + resume_file.name)
        with open(tmp_path, "wb") as f:
            f.write(resume_file.read())
        resume_text, _ = read_file_text(str(tmp_path))
        resume_text = clean_text(resume_text)
        st.text_area("Resume text", value=resume_text, height=300)

with col2:
    st.subheader("Job Description Upload")
    jd_file = st.file_uploader("Upload job description (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="jd")
    job_description = ""
    if jd_file is not None:
        tmp_path = BASE_DIR / ("tmp_jd_" + jd_file.name)
        with open(tmp_path, "wb") as f:
            f.write(jd_file.read())
        job_description, _ = read_file_text(str(tmp_path))
        job_description = clean_text(job_description)
        st.text_area("Job description text", value=job_description, height=300)

st.markdown("---")

colA, colB, colC = st.columns(3)

with colA:
    st.subheader("Optimize Resume")
    if st.button("Generate Optimized Resume", use_container_width=True, disabled=not (resume_text and job_description)):
        try:
            prompt = load_prompt("optimize_resume.txt")
            output = generate_text(prompt, variables={
                "resume_text": resume_text,
                "job_description": job_description,
            }, config=config)
            st.success("Optimized resume generated.")
            st.text_area("Optimized Resume", value=output, height=350)
            path = save_export("optimized_resume.txt", output)
            st.download_button("Download Optimized Resume", data=output, file_name="optimized_resume.txt")
            st.caption(f"Saved to {path}")
        except Exception as e:
            st.error(f"Error: {e}")

with colB:
    st.subheader("Cover Letter")
    candidate_name = st.text_input("Candidate Name", value="Your Name")
    if st.button("Generate Cover Letter", use_container_width=True, disabled=not (resume_text and job_description)):
        try:
            prompt = load_prompt("cover_letter.txt")
            output = generate_text(prompt, variables={
                "resume_text": resume_text,
                "job_description": job_description,
                "candidate_name": candidate_name,
            }, config=config)
            st.success("Cover letter generated.")
            st.text_area("Cover Letter", value=output, height=350)
            path = save_export("cover_letter.txt", output)
            st.download_button("Download Cover Letter", data=output, file_name="cover_letter.txt")
            st.caption(f"Saved to {path}")
        except Exception as e:
            st.error(f"Error: {e}")

with colC:
    st.subheader("ATS Score (Optional)")
    if st.button("Evaluate ATS Score", use_container_width=True, disabled=not (resume_text and job_description)):
        try:
            prompt = load_prompt("ats_score.txt")
            raw = generate_text(prompt, variables={
                "resume_text": resume_text,
                "job_description": job_description,
            }, config=config)
            # attempt to parse JSON
            data = {}
            try:
                data = json.loads(raw)
            except Exception:
                # try to extract JSON blob
                start = raw.find("{")
                end = raw.rfind("}")
                if start != -1 and end != -1 and end > start:
                    data = json.loads(raw[start:end+1])
            if not data:
                st.warning("Could not parse ATS response as JSON.")
                st.code(raw)
            else:
                st.metric("Score", data.get("score", "-"))
                st.write("**Strengths**")
                st.write("\n".join(f"- {s}" for s in data.get("strengths", [])))
                st.write("**Gaps**")
                st.write("\n".join(f"- {g}" for g in data.get("gaps", [])))
                st.write("**Recommended Keywords**")
                st.write(", ".join(data.get("recommended_keywords", [])))
                path = save_export("ats_score.json", json.dumps(data, indent=2))
                st.caption(f"Saved to {path}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")

st.caption("Prompts live in /prompts. Logic in /utils. Exports saved to /exports.")