# resume_analyzer_with_jd.py
#
# pip install streamlit requests pandas python-dateutil PyPDF2 python-docx matplotlib

import streamlit as st, requests, json, re, time, random, base64, csv
from io import BytesIO
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from PyPDF2 import PdfReader
import docx, pandas as pd, matplotlib.pyplot as plt

API_KEY    = "AIzaSyBrxLkge_12Oyn0psKx2d4Wn2MerKsMwG4"
MODEL_PATH = "v1beta/models/gemini-2.0-flash:generateContent"
GEMINI_URL = f"https://generativelanguage.googleapis.com/{MODEL_PATH}"
CONTROL    = re.compile(r"[\x00-\x09\x0B\x0C\x0E-\x1F]")

# ─────────── helpers (unchanged, folded for brevity) ───────────
def _strip_fences(t): t=t.strip();                     \
    t="\n".join(t.splitlines()[1:]) if t.startswith("```") else t; \
    t="\n".join(t.splitlines()[:-1]) if t.endswith("```") else t;  \
    return t
def clean_json(raw): return CONTROL.sub(" ", _strip_fences(raw))
def call_gemini(prompt,timeout=90):
    for a in range(5):
        try:
            r=requests.post(f"{GEMINI_URL}?key={API_KEY}",
                json={"contents":[{"parts":[{"text":prompt}]}]},
                headers={"Content-Type":"application/json"},timeout=timeout)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except requests.exceptions.RequestException as e:
            wait=random.randint(8,18); st.info(f"Gemini error {e}; retry {a+1}/5 in {wait}s"); time.sleep(wait)
    raise RuntimeError("Gemini failed 5×")
def extract_pdf(b):  return "\n\n".join((p.extract_text() or "") for p in PdfReader(b).pages)
def extract_docx(b): return "\n\n".join(p.text for p in docx.Document(b).paragraphs)
def months_between(p):
    try:
        s,e=[x.strip() for x in p.replace("—","-").replace("–","-").split("-",1)]
        sdt=parse(s,fuzzy=True); edt=date.today() if re.search("present|current|till now",e,re.I) else parse(e,fuzzy=True)
        d=relativedelta(edt,sdt); return str(d.years*12+d.months)
    except: return ""
def fmt_ym(m): y,mo=divmod(m,12); return f"{y}y {mo}m" if y else f"{mo}m"
def get_match_pct(t):
    t=t.replace("\n"," ")
    m=re.search(r"(?i)(overall\s+match(?:\s+percentage)?|match\s+percentage)\s*[:\-]?\s*(\d{1,3})\s*%",t)
    if m: val=int(m.group(2))
    else: val=max([int(x) for x in re.findall(r"(\d{1,3})\s*%",t)] or [0])
    return max(0,min(val,100))

# ────────────────────────── Streamlit UI ──────────────────────────
st.set_page_config("Resume ↔ JD Matcher", layout="wide")
st.title("📄 Resume Analyzer + JD Matcher")

if "df" not in st.session_state: st.session_state.df=None

jd_text=st.text_area("✍️ Paste the Job Description:",height=230)
files  =st.file_uploader("Upload up to 5 resumes (PDF/DOCX)",type=["pdf","docx"],accept_multiple_files=True)

# ────────────────────────── Analyze ──────────────────────────
if st.button("🔍 Analyze") and files and jd_text.strip():
    if len(files)>5: st.warning("Max 5 files."); st.stop()
    rows=[]
    for i,f in enumerate(files,1):
        st.markdown(f"### Resume {i}: {f.name}")
        txt=extract_pdf(BytesIO(f.getvalue())) if f.type=="application/pdf" else extract_docx(BytesIO(f.getvalue()))
        if not txt.strip(): st.error("❌ Empty / unreadable"); continue
        # structured extract
        p1=("Extract JSON only:\n"
            '{ "full_name":"","contact":{"phone":"","email":"","linkedin":"","location":""},'
            '"experience_by_company":[{"company":"","duration":""}],'
            '"certifications":[],"date_of_birth":"" }\n\nResume:\n'+txt)
        try: data=json.loads(clean_json(call_gemini(p1)))
        except Exception as e: st.error(f"Extract err: {e}"); continue
        row={"Full Name":data.get("full_name",""),
             "Phone":data.get("contact",{}).get("phone",""),
             "Email":data.get("contact",{}).get("email",""),
             "LinkedIn":data.get("contact",{}).get("linkedin",""),
             "Location":data.get("contact",{}).get("location",""),
             "Certifications":"; ".join(data.get("certifications",[])),
             "Date of Birth":data.get("date_of_birth","")}
        tot=0
        for j,ex in enumerate(data.get("experience_by_company",[]),1):
            dur=ex.get("duration",""); mon=months_between(dur)
            if mon.isdigit(): tot+=int(mon)
            row[f"Company {j}"]=ex.get("company","")
            row[f"Company {j} Duration"]=dur
            row[f"Company {j} total months"]=mon
        row["Total Experience"]=fmt_ym(tot)
        # JD match
        p2=f"Job Description:\n{jd_text}\n\nResume:\n{txt}\n\nProvide feedback + Match Percentage (0-100)."
        try: fb=call_gemini(p2)
        except Exception as e: fb=f"Error: {e}"
        row["JD Feedback"]=fb.strip(); rows.append(row); st.success("✅ Done")
    # dataframe + scoring
    if rows:
        df=pd.DataFrame(rows)
        df["Match %"]=df["JD Feedback"].apply(get_match_pct)
        df.loc[df["Match %"]<30,"Match %"]=0
        df=df.sort_values("Match %",ascending=False).reset_index(drop=True)
        df["Rank"]=df["Match %"].apply(lambda x:0 if x==0 else None)
        nz=df[df["Rank"].isnull()].copy(); nz["Rank"]=range(1,len(nz)+1); df.update(nz)

        # ─── UNIQUE DISPLAY NAME so bars don't overlap ───
        counts={}
        disp=[]
        for n in df["Full Name"]:
            counts[n]=counts.get(n,0)+1
            disp.append(n if counts[n]==1 else f"{n} #{counts[n]}")
        df["Display Name"]=disp

        st.session_state.df=df; st.success("✅ Analysis complete")

# ────────────────────────── Output & Charts ──────────────────────────
df=st.session_state.df
if df is not None:
    st.download_button("📥 Download CSV (quoted)",
        df.drop(columns=["Display Name"]).to_csv(index=False,quoting=csv.QUOTE_ALL).encode(),
        "resume_analysis_with_jd.csv","text/csv")
    st.dataframe(df.drop(columns=["Display Name"]),use_container_width=True)

    st.subheader("📊 JD Match – Column Chart")
    plot_df=df[df["Match %"]>0]
    if plot_df.empty:
        st.info("All resumes scored 0 %. Nothing to plot.")
    else:
        fig_bar,ax=plt.subplots(figsize=(8,4))
        ax.bar(plot_df["Display Name"], plot_df["Match %"], color="#4CAF50")
        ax.set_ylabel("Match %"); ax.set_ylim(0,100)
        ax.set_title("Resume vs JD – Match %")
        plt.xticks(rotation=30,ha="right"); st.pyplot(fig_bar)

    # pies
    st.subheader("🥧 Individual JD Match Pie Charts")
    cols=st.columns(3)
    for idx,row in df.iterrows():
        with cols[idx%3]:
            pct=int(row["Match %"]); name=row["Display Name"]
            fig_p,ax_p=plt.subplots(figsize=(3,3))
            ax_p.pie([pct,100-pct],labels=["Match","Gap"],autopct="%1.1f%%",
                     startangle=90,colors=["#4CAF50","#FF7043"])
            ax_p.set_title(f"{name}\n({pct}%)",fontsize=9)
            st.pyplot(fig_p)
            buf=BytesIO(); fig_p.savefig(buf,format="png",bbox_inches="tight"); buf.seek(0)
            b64=base64.b64encode(buf.read()).decode()
            st.markdown(f'<a download="{name}_pie.png" '
                        f'href="data:image/png;base64,{b64}">📥 Download</a>',
                        unsafe_allow_html=True)
