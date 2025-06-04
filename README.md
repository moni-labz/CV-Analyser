Below is a complete, copy-ready **README.md** followed by the **requirements.txt** and a short checklist of code tweaks.
Everything is written so someone with only basic Python knowledge can get the app running in a few minutes.

---

````markdown
# 📄 Resume Analyzer – “Gemini-Powered” Streamlit App

Automatically turn up to **five** PDF / DOCX résumés into a single, tidy CSV that contains:

| Field Group | What You Get |
|-------------|--------------|
| Personal    | Full name, phone, email, LinkedIn, location, date of birth |
| Experience  | Company-wise breakdown **plus** auto-calculated “Total experience” (`X years Y months`) |
| Projects    | Title + description for every project Gemini can spot |
| Certifications | A semicolon-separated list |

Powered by **Google Gemini 2.0 Flash** with an infinite-retry loop and random cool-off, the app keeps requesting until it succeeds, so you don’t have to babysit it.

---

## ✨ Key Strengths (Why this repo is worth a ⭐)

| Aspect | Positive Point |
|--------|----------------|
| **Reliability** | Auto-retry with random 10–20 s cool-off means brief API outages never kill your run. |
| **Data cleanliness** | Regular-expression scrubbers remove control chars and code fences before `json.loads`, preventing parse errors. |
| **Strict JSON contract** | Prompts force Gemini to return *only* valid JSON in a fixed schema, avoiding hallucinated prose. |
| **Multi-format support** | Reads both PDFs (`PyPDF2`) and Word docs (`python-docx`) out-of-the-box. |
| **Overlap-safe experience calc** | Requests Gemini to count overlapping jobs only once, delivering realistic totals. |
| **No local ML heavy-lifting** | All NLP happens in the cloud, so the app remains lightweight and deploys easily on small VPSes. |
| **Instant CSV download** | One click to get a combined CSV—ready for Excel, Google Sheets, ATS, or BI dashboards. |
| **User-friendly UI** | Single-page Streamlit layout, progress spinners, and emoji-based status make analysis painless for non-tech HR staff. |
| **Config-driven** | API key, retry policy, model path, and cool-off range live in one “CONFIG” block—no code hunting. |
| **Dependency-light** | Only six runtime libraries; cold-start is fast even on free-tier hosts. |

---

## 🛠  Quick-start

### 1. Clone & install

```bash
git clone https://github.com/your-handle/resume-analyzer.git
cd resume-analyzer
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
````

### 2. Get a Google AI Studio **API key**

1. Open **[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)** (or “API Keys” in Google AI Studio left menu).
2. Click **“Create API key”** → give it a name (e.g., `gemini-resume-tool`).
3. Copy the key that starts with `AIza…`.
4. Either:

   * **Option A** – set an environment variable

     ```bash
     export GEMINI_API_KEY="AIza…"      # Windows PowerShell: setx GEMINI_API_KEY "AIza…"
     ```
   * **Option B** – paste it straight into `streamlit_app.py` at the top:

     ```python
     API_KEY = "AIza…"   # ← replace
     ```

> **Tip:** for production, always prefer environment variables or a `.env` file to avoid accidentally publishing secrets.

### 3. Run the app

```bash
streamlit run streamlit_app.py
```

It launches on **[http://localhost:8501](http://localhost:8501)** by default.

---

## 🚀  Using the Tool

1. **Upload** up to five resumes (PDF or DOCX).
2. Click **“🔍 Analyze & Download CSV”**.
3. Watch the per-resume section:

   * 🟡 *Spinner* → Gemini is working.
   * ✅ *Finished* → That file has been parsed and added to the table.
4. When all are done, a **📥 Download Combined CSV** button appears.
5. Click it, save `resumes.csv`, open it in Excel/Sheets/your ATS.

---

## 🔧 Suggested Code Improvements

| Area                  | Change                                                                        | Why                                       |
| --------------------- | ----------------------------------------------------------------------------- | ----------------------------------------- |
| **Secrets handling**  | Replace `API_KEY="GEMINI_API_KEY"` with `API_KEY=os.getenv("GEMINI_API_KEY")` | Keeps keys out of source control.         |
| **Retry policy**      | Set `MAX_RETRIES = 5` (or cfg via sidebar)                                    | Prevents infinite loops on long outages.  |
| **Back-off strategy** | Switch from random to exponential (e.g., `time.sleep(2 ** attempt)`)          | Converges faster and respects API limits. |
| **PDF performance**   | Cache `extract_pdf` results with `@st.cache_data`                             | Speeds up re-runs on the same file.       |
| **Error logging**     | Write Gemini errors to a log file instead of only `st.info`                   | Easier debugging after batch runs.        |
| **Accessibility**     | Add `st.caption` under buttons explaining size/format limits                  | Improves usability for new HR users.      |
| **CI/CD**             | Include GitHub Actions workflow to run `flake8` & `pytest`                    | Keeps code quality high as project grows. |

---

## 📦 requirements.txt

```
streamlit>=1.33
requests>=2.31
pandas>=2.2
PyPDF2>=3.0
python-docx>=1.1
```

*(Python 3.9+ recommended; the app is OS-agnostic.)*

---

## 📝 License

MIT – free for personal or commercial use. Please keep the original copyright notice.

---

Happy parsing! Pull requests are welcome.

````

---

### **requirements.txt** (copy-ready)

```text
streamlit>=1.33
requests>=2.31
pandas>=2.2
PyPDF2>=3.0
python-docx>=1.1
````

---

#### Quick Code-Change Checklist

1. **API Key**

   ```python
   import os
   API_KEY = os.getenv("GEMINI_API_KEY", "REPLACE_ME")
   ```
2. **Optional retry cap**

   ```python
   MAX_RETRIES = 5
   ```
3. **Optional exponential back-off**

   ```python
   wait_s = min(60, 2 ** attempt)   # max 60 s
   ```

Once those tweaks are in place, follow the *Quick-start* steps above and you’re set!
