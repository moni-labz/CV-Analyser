# 📄 Resume Analyzer — *AI-Powered* Streamlit App

Automatically turn **up to five** PDF / DOCX résumés into a neat CSV.

| Field Group     | What You Get                                                                                         |
|-----------------|-------------------------------------------------------------------------------------------------------|
| **Personal**    | Full name, phone, email, LinkedIn, location, date of birth                                            |
| **Experience**  | Company-by-company breakdown **plus** auto-calculated “Total experience” (`X years Y months`)         |
| **Projects**    | Title + description for every project Gemini can detect                                               |
| **Certifications** | A semicolon-separated list                                                                         |

Powered by **Google Gemini 2.0 Flash** with an infinite-retry loop and random cool-off intervals, the app just keeps trying until it succeeds—no babysitting required.

---

## ✨ Key Strengths

| Aspect                    | Why It Rocks                                                                                                      |
|---------------------------|--------------------------------------------------------------------------------------------------------------------|
| **Reliability**           | Auto-retry with 10–20 s random cool-off—brief API hiccups never kill a run.                                        |
| **Data cleanliness**      | Regex scrub removes control characters & code fences before `json.loads`, avoiding parse errors.                   |
| **Strict JSON contract**  | Prompts force Gemini to return **only** valid JSON in a fixed schema, preventing hallucinated prose.               |
| **Multi-format support**  | Reads PDFs (`PyPDF2`) *and* Word docs (`python-docx`) out of the box.                                              |
| **Overlap-safe exp calc** | Tells Gemini to count overlapping jobs only once, yielding realistic totals.                                       |
| **Lightweight**           | All NLP happens in the cloud—deploys easily on small VPSes, no heavy local ML.                                     |
| **One-click CSV**         | Instant “📥 Download Combined CSV” button—ready for Excel, Sheets, ATS, BI, etc.                                   |
| **Friendly UI**           | Single-page Streamlit layout, emoji status, and progress spinners—great for non-tech HR staff.                     |
| **Config-driven**         | API key, model path, retry policy, and cool-off live in one **CONFIG** block—no hunting through code.              |
| **Dependency-light**      | Just six runtime libraries—cold-starts are fast even on free-tier hosts.                                           |

---

Below is the revised **Install & Run** section, now pointing to **your repository** at `https://github.com/moni-labz/CV-Analyser.git`.
Replace the previous block in your README with this one.

````markdown
## 🛠 Quick-start

### 1 · Clone the repo

```bash
git clone https://github.com/moni-labz/CV-Analyser.git
cd CV-Analyser
````

### 2 · Create & activate a virtual environment

```bash
python -m venv .venv          # create venv
# ───────────── macOS/Linux ─────────────
source .venv/bin/activate
# ─────────── Windows (PowerShell) ───────
.\.venv\Scripts\Activate.ps1
```

### 3 · Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4 · Add your Google AI Studio API key

```bash
# macOS / Linux
export GEMINI_API_KEY="AIza…"

# Windows PowerShell
setx GEMINI_API_KEY "AIza…"
```

*(Or paste the key into `streamlit_app.py` if you prefer—environment variables are safer for production.)*

### 5 · Run the app

```bash
streamlit run streamlit_app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser and you’re ready to analyze résumés!

---

```

This snippet drops straight into your README and uses your GitHub URL, keeping the rest of the workflow unchanged.
```
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
