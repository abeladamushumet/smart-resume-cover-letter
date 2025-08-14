import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from utils.openai_utils import generate_text
from utils.file_utils import read_uploaded_file, save_text_as_docx, next_export_filename
from utils.text_utils import clean_text

BASE_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = BASE_DIR / "prompts"
EXPORTS_DIR = BASE_DIR / "exports"
SAMPLE_DIR = BASE_DIR / "sample_data"

load_dotenv()

st.set_page_config(page_title="Smart Resume + Cover Letter", page_icon="📝", layout="wide")


def read_prompt(name: str) -> str:
    path = PROMPTS_DIR / name
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        st.error(f"Failed to load prompt '{name}': {exc}")
        return ""


def sidebar_config():
    st.sidebar.header("Settings")
    api_present = bool(os.getenv("OPENAI_API_KEY"))
    st.sidebar.write(f"API key loaded: {'✅' if api_present else '❌'}")

    model_default = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    model = st.sidebar.text_input("Model", value=model_default, help="Override via OPENAI_MODEL env var")
    temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1)
    max_tokens = st.sidebar.slider("Max tokens", 500, 4000, 1500, 100)

    return model, float(temperature), int(max_tokens)


def input_section(key_prefix: str):
    left, right = st.columns(2)

    with left:
        st.subheader("Resume")
        resume_file = st.file_uploader(
            "Upload resume (DOCX, PDF, TXT)", type=["docx", "pdf", "txt"], key=f"resume_file_{key_prefix}"
        )
        resume_text_default = ""
        if resume_file is not None:
            try:
                text, kind = read_uploaded_file(resume_file)
                resume_text_default = text
                st.caption(f"Detected {kind.upper()} • {len(text):,} chars")
            except Exception as exc:
                st.warning(f"Could not read file: {exc}")
        resume_text = st.text_area("Or paste resume text", value=resume_text_default, height=220, key=f"resume_text_{key_prefix}")

    with right:
        st.subheader("Job Description")
        jd_file = st.file_uploader(
            "Upload job description (TXT, PDF, DOCX)", type=["txt", "pdf", "docx"], key=f"jd_file_{key_prefix}"
        )
        jd_default = ""
        if jd_file is not None:
            try:
                text, _ = read_uploaded_file(jd_file)
                jd_default = text
                st.caption(f"Job description length • {len(text):,} chars")
            except Exception as exc:
                st.warning(f"Could not read JD file: {exc}")
        job_description = st.text_area("Or paste job description", value=jd_default, height=220, key=f"jd_text_{key_prefix}")

    return clean_text(resume_text), clean_text(job_description)


def render_result_section(label: str, content: str, filename_prefix: str):
    st.subheader(label)
    st.text_area("Output", value=content, height=420)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Download DOCX", key=f"download_{filename_prefix}"):
            output_path = next_export_filename(filename_prefix)
            save_text_as_docx(content, output_path)
            st.success(f"Saved to {output_path.relative_to(BASE_DIR)}")
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Download",
                    data=f.read(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dlbtn_{filename_prefix}",
                )


def main():
    st.title("Smart Resume + Cover Letter")
    st.caption("Optimize your resume and generate tailored cover letters. Optional ATS scoring.")

    model, temperature, max_tokens = sidebar_config()

    tabs = st.tabs(["Resume Optimizer", "Cover Letter", "ATS Score (optional)"])

    # Resume Optimizer
    with tabs[0]:
        resume_text, job_description = input_section("resume")
        if st.button("Generate Optimized Resume", type="primary"):
            if not resume_text or not job_description:
                st.warning("Please provide both resume and job description.")
            else:
                with st.spinner("Generating optimized resume..."):
                    template = read_prompt("resume_prompt.txt")
                    user_prompt = template.format(
                        resume_text=resume_text,
                        job_description=job_description,
                    )
                    try:
                        optimized = generate_text(
                            user_prompt=user_prompt,
                            system_prompt="You are an expert resume writer.",
                            model=model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        render_result_section("Optimized Resume", optimized, "resume_optimized")
                    except Exception as exc:
                        st.error(f"Generation failed: {exc}")

    # Cover Letter
    with tabs[1]:
        resume_text, job_description = input_section("cover")
        if st.button("Generate Cover Letter", type="primary"):
            if not resume_text or not job_description:
                st.warning("Please provide both resume and job description.")
            else:
                with st.spinner("Generating cover letter..."):
                    template = read_prompt("coverletter_prompt.txt")
                    user_prompt = template.format(
                        resume_text=resume_text,
                        job_description=job_description,
                    )
                    try:
                        cover = generate_text(
                            user_prompt=user_prompt,
                            system_prompt="You are an expert cover letter writer.",
                            model=model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        render_result_section("Cover Letter", cover, "cover_letter")
                    except Exception as exc:
                        st.error(f"Generation failed: {exc}")

    # ATS Score
    with tabs[2]:
        resume_text, job_description = input_section("ats")
        if st.button("Run ATS Scoring"):
            if not resume_text or not job_description:
                st.warning("Please provide both resume and job description.")
            else:
                with st.spinner("Scoring resume vs JD..."):
                    template = read_prompt("ats_score_prompt.txt")
                    user_prompt = template.format(
                        resume_text=resume_text,
                        job_description=job_description,
                    )
                    try:
                        result = generate_text(
                            user_prompt=user_prompt,
                            system_prompt="You analyze resumes like an ATS and a recruiter.",
                            model=model,
                            temperature=0.1,
                            max_tokens=800,
                        )
                        # Try to parse JSON
                        data = None
                        try:
                            data = json.loads(result)
                        except Exception:
                            st.warning("Model did not return valid JSON. Showing raw output.")
                            st.code(result, language="json")
                        if data:
                            st.metric("ATS Score", f"{data.get('score', 0)} / 100")
                            st.write(data.get("summary", ""))
                            left, right = st.columns(2)
                            with left:
                                st.markdown("**Missing Keywords**")
                                st.write(data.get("missing_keywords", []))
                            with right:
                                st.markdown("**Recommendations**")
                                st.write(data.get("recommendations", []))
                    except Exception as exc:
                        st.error(f"ATS scoring failed: {exc}")


if __name__ == "__main__":
    main()