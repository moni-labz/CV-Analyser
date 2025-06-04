import streamlit as st
import requests, json, re, time, random
from io import BytesIO
from datetime import date
from PyPDF2 import PdfReader
import docx
import pandas as pd

# ───────────────────────────────
# 1. CONFIG
# ───────────────────────────────
API_KEY    = "GEMINI_API_KEY"                 # ← replace
MODEL_PATH = "v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_URL = f"https://generativelanguage.googleapis.com/{MODEL_PATH}"
TODAY_STR  = str(date.today())              # e.g. "2025-06-04"

MAX_RETRIES = None        # None → retry indefinitely
COOL_OFF_MIN = 10         # wait at least 10 s
COOL_OFF_MAX = 20         # …at most 20 s before the next try

# ───────────────────────────────
# 2. HELPER FUNCTIONS
# ───────────────────────────────
CONTROL = re.compile(r"[\x00-\x09\x0B\x0C\x0E-\x1F]")  # keep \n\r

def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"): text = "\n".join(text.splitlines()[1:])
    if text.endswith("```"):   text = "\n".join(text.splitlines()[:-1])
    return text

def clean_json(raw: str) -> str:
    return CONTROL.sub(" ", _strip_fences(raw))

def clean_firstline(raw: str) -> str:
    return CONTROL.sub(" ", _strip_fences(raw)).splitlines()[0].strip()

def call_gemini(prompt: str, timeout: int = 90) -> str:
    """Gemini call with infinite (or capped) retry & random cool-off."""
    attempt = 0
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}

    while True:
        attempt += 1
        try:
            r = requests.post(f"{GEMINI_URL}?key={API_KEY}",
                              headers=headers, json=body, timeout=timeout)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]

        except requests.exceptions.RequestException as e:
            # Decide whether to give up
            if MAX_RETRIES is not None and attempt >= MAX_RETRIES:
                raise RuntimeError(f"Giving up after {attempt} tries: {e}") from e

            wait_s = random.randint(COOL_OFF_MIN, COOL_OFF_MAX)
            st.info(f"⚠️ Gemini error ({e}). Cooling off {wait_s}s before retry {attempt}…")
            time.sleep(wait_s)

def extract_pdf(buf: BytesIO) -> str:
    return "\n\n".join((p.extract_text() or "") for p in PdfReader(buf).pages)

def extract_docx(buf: BytesIO) -> str:
    return "\n\n".join(p.text for p in docx.Document(buf).paragraphs)

# ───────────────────────────────
# 3. STREAMLIT UI
# ───────────────────────────────
st.set_page_config(page_title="Resume → CSV (auto-retry, cool-off)", layout="wide")
st.title("📄 Resume Analyzer — Gemini keeps trying until it works")

files = st.file_uploader(
    "Upload up to 5 résumés (PDF or DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

if files:
    if len(files) > 5:
        st.warning("⚠️ Please upload no more than 5 files.")
        st.stop()

    rows = []

    if st.button("🔍 Analyze & Download CSV"):
        for idx, f in enumerate(files, 1):
            st.markdown(f"### 📄 Resume {idx}: {f.name}")

            text = extract_pdf(BytesIO(f.getvalue())) if f.type == "application/pdf" \
                   else extract_docx(BytesIO(f.getvalue()))

            if not text.strip():
                st.error("❌ Could not read any text from this file.")
                continue

            # ── 1️⃣ EXTRACTION ──────────────────────────────────
            extract_prompt = (
                "Extract the following information from the resume below **and return ONLY valid "
                "JSON with NO extra text**.\nThe JSON shape MUST be exactly:\n"
                '{\n'
                '  "full_name": "string",\n'
                '  "contact": { "phone": "string", "email": "string", "linkedin": "string", "location": "string" },\n'
                '  "certifications": ["string"],\n'
                '  "projects": [ { "title": "string", "description": "string" } ],\n'
                '  "experience_by_company": [ { "company": "string", "duration": "string" } ],\n'
                '  "date_of_birth": "string or Not mentioned"\n'
                '}\n\n'
                "Resume:\n" + text
            )

            try:
                with st.spinner("Extracting structured data (retry until success)…"):
                    raw_json = call_gemini(extract_prompt)
                    data     = json.loads(clean_json(raw_json))
            except Exception as e:
                st.error(f"❌ Extraction failed: {e}")
                rows.append({"Full Name": f.name, "Total Experience": "Error"})
                continue

            # ── 2️⃣ TOTAL EXPERIENCE ───────────────────────────
            durations = "\n".join(
                f"{e.get('company','Unknown')}: {e.get('duration','')}"
                for e in data.get("experience_by_company", [])
            ) or "No experience entries"

            total_prompt = (
                f"Today is {TODAY_STR}.\n"
                "Based ONLY on the employment periods below, calculate the person's total professional "
                "experience up to today (count overlapping periods only once). "
                "Return ONLY a single line like:  \"X years Y months\".\n\n"
                + durations
            )

            try:
                with st.spinner("Calculating total experience (retry until success)…"):
                    total_raw = call_gemini(total_prompt)
                    total_exp = clean_firstline(total_raw)
            except Exception as e:
                st.warning(f"Could not calculate total experience: {e}")
                total_exp = "Error"

            # ── BUILD CSV ROW ──────────────────────────────────
            row = {
                "Full Name"       : data.get("full_name", ""),
                "Phone"           : data.get("contact", {}).get("phone", ""),
                "Email"           : data.get("contact", {}).get("email", ""),
                "LinkedIn"        : data.get("contact", {}).get("linkedin", ""),
                "Location"        : data.get("contact", {}).get("location", ""),
                "Certifications"  : "; ".join(data.get("certifications", [])),
                "Total Experience": total_exp,
                "Date of Birth"   : data.get("date_of_birth", ""),
            }
            for j, pr in enumerate(data.get("projects", []), 1):
                row[f"Project {j} Title"]       = pr.get("title", "")
                row[f"Project {j} Description"] = pr.get("description", "")
            for j, ex in enumerate(data.get("experience_by_company", []), 1):
                row[f"Company {j}"]          = ex.get("company", "")
                row[f"Company {j} Duration"] = ex.get("duration", "")
            rows.append(row)

            st.success("✅ Finished")

        # ── DOWNLOAD CSV ───────────────────────────────────────
        if rows:
            df = pd.DataFrame(rows)
            st.download_button(
                "📥 Download Combined CSV",
                df.to_csv(index=False).encode(),
                file_name="resumes.csv",
                mime="text/csv",
            )
