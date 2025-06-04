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

## 🛠 How to Install and Run the Resume Analyzer

Follow the steps below to set up and run the Resume Analyzer app on your system.

---

### 🔁 Step 1: Clone the Repository

Open your terminal or command prompt and run:

```bash
git clone https://github.com/moni-labz/CV-Analyser.git
cd CV-Analyser
````

---

### 🐍 Step 2: Set Up a Virtual Environment (Recommended)

A virtual environment keeps your dependencies clean and isolated.

#### 🔹 For **Windows** (PowerShell):

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

#### 🔹 For **Linux/macOS**:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 📦 Step 3: Install the Required Python Libraries

Once the virtual environment is activated, install the required dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:

* `streamlit` – for the user interface
* `requests` – for calling the Gemini API
* `PyPDF2` – for reading PDF resumes
* `python-docx` – for reading Word resumes
* `pandas` – for generating the CSV output

---

### 🔑 Step 4: Get Your Google Gemini API Key

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **“Create API Key”**.
3. Name it something like `resume-tool-key`.
4. Copy the key that starts with `AIza...`.

---

### 🔐 Step 5: Set Your API Key

You have two options to provide your Gemini API key.

#### ✅ Option A: Set as Environment Variable (Recommended)

##### 🔹 For **Windows** (PowerShell):

```bash
$env:GEMINI_API_KEY="AIzaYourKeyHere"
```

##### 🔹 For **Linux/macOS**:

```bash
export GEMINI_API_KEY="AIzaYourKeyHere"
```

#### ⚠️ Option B: Hardcode in the Code (Not Recommended for Production)

Open `streamlit_app.py` and find this line:

```python
API_KEY = "GEMINI_API_KEY"  # ← replace this
```

Replace it with:

```python
API_KEY = "AIzaYourKeyHere"
```

---

### ▶️ Step 6: Run the Streamlit App

Now you're ready to launch the app:

```bash
streamlit run app.py
```

After a few seconds, the app will open automatically in your browser at:

```
http://localhost:8501
```

---

## 🚀 How to Use the Resume Analyzer

1. Upload up to **five resumes** in PDF or DOCX format.
2. Click on **🔍 Analyze & Download CSV**.
3. Wait while each resume is processed:

   * 🟡 *Spinner* → Gemini is extracting data.
   * ✅ *Finished* → Resume successfully analyzed.
4. Once all resumes are processed, click **📥 Download Combined CSV**.
5. Open the CSV in **Excel, Google Sheets, or your ATS**.

---

✅ You're now ready to analyze resumes at scale with the power of **Google Gemini** and **Streamlit**!





## 📝 License

MIT – free for personal or commercial use. Please keep the original copyright notice.

---

Happy parsing! Pull requests are welcome.

