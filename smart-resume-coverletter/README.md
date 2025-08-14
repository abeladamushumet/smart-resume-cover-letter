# Smart Resume + Cover Letter

AI-powered Streamlit app to optimize your resume and generate tailored cover letters for any job description. Optional ATS scoring included.

## Features
- Upload DOCX, PDF, or paste text for your resume
- Paste or upload a job description
- Generate optimized resume content
- Generate tailored cover letters
- Optional ATS score + recommendations
- Export results to DOCX and download

## Setup

1. Clone this repo and enter the project directory.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment:
   - Copy `.env.example` to `.env` and set your API key(s):
     ```bash
     cp .env.example .env
     ```
   - Fill in `OPENAI_API_KEY` and optionally `OPENAI_MODEL` (defaults to `gpt-4o-mini`).

## Run
```bash
streamlit run app.py
```

## Environment
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL` (optional): Model name (e.g., `gpt-4o`, `gpt-4o-mini`).

## Project Structure
```
smart-resume-coverletter/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env               # Not checked in; create from .env.example
├── prompts/
│   ├── resume_prompt.txt
│   ├── coverletter_prompt.txt
│   └── ats_score_prompt.txt
├── utils/
│   ├── __init__.py
│   ├── openai_utils.py
│   ├── file_utils.py
│   └── text_utils.py
├── sample_data/
│   ├── sample_resume.docx   # Optional (generated at runtime if missing)
│   └── sample_job.txt
└── exports/
    ├── .gitkeep
```

## Notes
- `exports/` contains generated DOCX files. They are git-ignored.
- If `sample_resume.docx` is missing, you can upload your own resume or paste text.
- Prompts in `prompts/` are editable; tweak them to your style.