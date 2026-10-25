"""
Generates a stand-in dataset with the SAME columns as the Kaggle
"Credit Risk Dataset" (credit_risk_dataset.csv). Used only when the real
CSV is not present in data/. It even includes the dirty rows (impossible
ages, nulls, duplicates) so the cleaning step has real work to do.
"""
import numpy as np, pandas as pd

def make_dataset(n=32000, seed=42):
    rng = np.random.default_rng(seed)
    age = np.clip(rng.gamma(9, 3, n) + 18, 20, 70).astype(int)
    income = np.clip(rng.lognormal(11.0, 0.55, n), 8000, 400000).round(0)
    home = rng.choice(["RENT", "MORTGAGE", "OWN", "OTHER"], n, p=[.50, .41, .08, .01])
    emp = np.clip((age - 20) * rng.beta(1.2, 3, n), 0, 40).round(0)
    intent = rng.choice(["EDUCATION", "MEDICAL", "VENTURE", "PERSONAL", "DEBTCONSOLIDATION", "HOMEIMPROVEMENT"],
                        n, p=[.20, .19, .18, .17, .16, .10])
    grade = rng.choice(list("ABCDEFG"), n, p=[.33, .32, .20, .11, .03, .007, .003])
    gi = np.array([ord(g) - 65 for g in grade])
    loan = np.clip(rng.lognormal(9.2, 0.6, n), 500, 35000).round(-2)
    rate = np.clip(7 + 1.6 * gi + rng.normal(0, 1.2, n), 5.4, 23).round(2)
    pct = (loan / income).round(2)
    hist_default = rng.choice(["Y", "N"], n, p=[.18, .82])
    cred_hist = np.clip(rng.gamma(2, 2.5, n) + 2, 2, 30).astype(int)

    z = (-3.1 + 0.55 * gi + 6.0 * pct - 0.000012 * income
         + 0.5 * (home == "RENT") + 0.9 * (home == "OTHER") - 0.7 * (home == "OWN")
         + 0.35 * (hist_default == "Y") + 0.25 * (intent == "DEBTCONSOLIDATION")
         + 0.2 * (intent == "MEDICAL") - 0.25 * (intent == "EDUCATION")
         - 0.03 * emp + rng.normal(0, 0.6, n))
    status = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)

    df = pd.DataFrame(dict(person_age=age, person_income=income, person_home_ownership=home,
        person_emp_length=emp, loan_intent=intent, loan_grade=grade, loan_amnt=loan,
        loan_int_rate=rate, loan_status=status, loan_percent_income=pct,
        cb_person_default_on_file=hist_default, cb_person_cred_hist_length=cred_hist))

    # ---- inject "real-world dirt" like the Kaggle file has ----
    df.loc[rng.choice(n, 4, replace=False), "person_age"] = [144, 123, 144, 144]
    df.loc[rng.choice(n, 2, replace=False), "person_emp_length"] = [123, 123]
    df.loc[rng.choice(n, int(.028 * n), replace=False), "person_emp_length"] = np.nan
    df.loc[rng.choice(n, int(.095 * n), replace=False), "loan_int_rate"] = np.nan
    df = pd.concat([df, df.sample(165, random_state=1)], ignore_index=True)
    return df

if __name__ == "__main__":
    make_dataset().to_csv("data/credit_risk_dataset.csv", index=False)
    print("saved data/credit_risk_dataset.csv")
