# Credit Risk Analysis System
Data Science Capstone (SkillOrbit) - predicts a loan applicant's probability of default and recommends **Approve / Review Manually / Reject**.

## Run it
```bash
pip install -r requirements.txt
# Put the real Kaggle file here (recommended):  data/credit_risk_dataset.csv
python train_model.py      # clean -> EDA charts -> train 3 models -> save best model
python build_report.py     # (optional) regenerates outputs/Project_Report.docx from real results
streamlit run app.py       # dashboard
```
If `data/credit_risk_dataset.csv` is missing, a stand-in dataset with the same columns is generated automatically.

## Files
| File | Purpose |
|---|---|
| `credit_utils.py` | shared cleaning function, feature lists, risk thresholds, recommendation rules |
| `generate_data.py` | stand-in dataset with the Kaggle schema (only used if the real CSV is absent) |
| `train_model.py` | Modules 1-3: cleaning, EDA, model comparison, calibration, saving |
| `app.py` | Modules 4-5: Streamlit dashboard + recommendation |
| `models/` | saved model (`credit_model.joblib`) and `metrics.json` |
| `outputs/charts/` | all EDA and model charts |

## Decision rule
PD < 15% -> Approve | 15-40% -> Review Manually | >= 40% -> Reject (edit in `credit_utils.py`)

## Deploy (Streamlit Community Cloud)
Push to GitHub (include `models/` and `data/clean_data.csv`), go to share.streamlit.io, choose the repo, main file `app.py`.
