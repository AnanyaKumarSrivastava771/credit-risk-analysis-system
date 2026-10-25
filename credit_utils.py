"""Shared helpers used by BOTH the training script and the Streamlit app."""
import os
import pandas as pd

DATA_PATH = "data/credit_risk_dataset.csv"
TARGET = "loan_status"          # 1 = defaulted, 0 = repaid
NUM_COLS = ["person_age", "person_income", "person_emp_length", "loan_amnt",
            "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length"]
CAT_COLS = ["person_home_ownership", "loan_intent", "loan_grade", "cb_person_default_on_file"]
FEATURES = NUM_COLS + CAT_COLS

# Decision thresholds on the predicted probability of default (PD)
APPROVE_BELOW = 0.15
REJECT_FROM = 0.40


def load_raw():
    """Use the real Kaggle CSV if the user placed it in data/, else build the stand-in."""
    if not os.path.exists(DATA_PATH):
        from generate_data import make_dataset
        os.makedirs("data", exist_ok=True)
        make_dataset().to_csv(DATA_PATH, index=False)
    return pd.read_csv(DATA_PATH)


def clean_data(df):
    """Module 1: remove duplicates and impossible values. Returns (clean_df, log)."""
    log = {"rows_raw": len(df)}
    df = df.drop_duplicates()
    log["duplicates_removed"] = log["rows_raw"] - len(df)
    n = len(df)
    df = df[df["person_age"].between(18, 100)]          # ages like 144 are data-entry errors
    log["impossible_age_removed"] = n - len(df)
    n = len(df)
    df = df[df["person_emp_length"].isna() | (df["person_emp_length"] <= 60)]  # 123 years of work
    log["impossible_emp_length_removed"] = n - len(df)
    log["missing_emp_length"] = int(df["person_emp_length"].isna().sum())
    log["missing_loan_int_rate"] = int(df["loan_int_rate"].isna().sum())
    log["rows_clean"] = len(df)
    return df.reset_index(drop=True), log


def risk_category(pd_):
    if pd_ < APPROVE_BELOW:
        return "Low Risk"
    if pd_ < REJECT_FROM:
        return "Medium Risk"
    return "High Risk"


def recommendation(pd_):
    if pd_ < APPROVE_BELOW:
        return "Approve Loan"
    if pd_ < REJECT_FROM:
        return "Review Manually"
    return "Reject Application"
