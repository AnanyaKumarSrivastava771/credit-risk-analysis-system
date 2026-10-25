"""Module 4 + 5: Risk Score Dashboard and Final Recommendation System (Streamlit)."""
import json
import joblib, numpy as np, pandas as pd, streamlit as st
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from credit_utils import *

st.set_page_config(page_title="Credit Risk Analysis System", page_icon="🏦", layout="wide")

@st.cache_resource
def load_model():
    return joblib.load("models/credit_model.joblib")

@st.cache_data
def load_scored_data():
    df = pd.read_csv("data/clean_data.csv")
    df["pd"] = load_model().predict_proba(df[FEATURES])[:, 1]
    df["risk"] = df["pd"].apply(risk_category)
    df["decision"] = df["pd"].apply(recommendation)
    return df

metrics = json.load(open("models/metrics.json"))
COLORS = {"Low Risk": "#2a9d8f", "Medium Risk": "#f4a261", "High Risk": "#e63946"}

def gauge(pd_):
    fig, ax = plt.subplots(figsize=(5, 2.8), subplot_kw=dict(projection="polar"))
    ax.set_theta_zero_location("W"); ax.set_theta_direction(-1); ax.set_thetamin(0); ax.set_thetamax(180)
    for lo, hi, c in [(0, APPROVE_BELOW, "#2a9d8f"), (APPROVE_BELOW, REJECT_FROM, "#f4a261"), (REJECT_FROM, 1, "#e63946")]:
        ax.barh(1, np.pi * (hi - lo), left=np.pi * lo, height=0.5, color=c, alpha=.9)
    ax.plot([np.pi * pd_] * 2, [0.6, 1.3], color="black", lw=3)
    ax.set_yticks([]); ax.set_xticks([]); ax.spines["polar"].set_visible(False); ax.set_ylim(0, 1.5)
    ax.text(np.pi / 2, 0.05, f"{pd_:.1%}", ha="center", va="bottom", fontsize=20, fontweight="bold", clip_on=False)
    fig.patch.set_alpha(0); return fig
    

st.title("🏦 Credit Risk Analysis System")
st.caption("Predicts an applicant's probability of default and recommends: Approve / Review Manually / Reject.")
tab1, tab2, tab3 = st.tabs(["🔮 Risk Predictor", "📊 Portfolio Dashboard", "🧪 Model Performance"])

# ---------------------------------------------------------------- TAB 1
with tab1:
    left, right = st.columns([1, 1])
    with left:
        st.subheader("Applicant details")
        c1, c2 = st.columns(2)
        age = c1.number_input("Age", 18, 100, 30)
        income = c2.number_input("Annual income", 4000, 1_000_000, 55000, step=1000)
        home = c1.selectbox("Home ownership", ["RENT", "MORTGAGE", "OWN", "OTHER"])
        emp = c2.number_input("Employment length (years)", 0, 60, 4)
        intent = c1.selectbox("Loan purpose", ["PERSONAL", "EDUCATION", "MEDICAL", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"])
        grade = c2.selectbox("Loan grade (A best - G worst)", list("ABCDEFG"), index=2)
        amnt = c1.number_input("Loan amount", 500, 100000, 10000, step=500)
        rate = c2.number_input("Interest rate (%)", 4.0, 30.0, 11.0, step=0.1)
        prior = c1.selectbox("Previously defaulted?", ["N", "Y"])
        hist = c2.number_input("Credit history length (years)", 0, 50, 5)
        go = st.button("Assess applicant", type="primary", width="stretch")
    with right:
        st.subheader("Assessment")
        if go:
            row = pd.DataFrame([dict(person_age=age, person_income=income, person_emp_length=emp, loan_amnt=amnt,
                loan_int_rate=rate, loan_percent_income=round(amnt / income, 2), cb_person_cred_hist_length=hist,
                person_home_ownership=home, loan_intent=intent, loan_grade=grade, cb_person_default_on_file=prior)])
            p = float(load_model().predict_proba(row[FEATURES])[0, 1])
            p = min(max(p, 0.01), 0.99)
            cat, dec = risk_category(p), recommendation(p)
            st.pyplot(gauge(p), width="content")
            m1, m2, m3 = st.columns(3)
            m1.metric("Default probability", f"{p:.1%}")
            m2.metric("Approval probability", f"{1 - p:.1%}")
            m3.metric("Risk category", cat)
            {"Approve Loan": st.success, "Review Manually": st.warning, "Reject Application": st.error}[dec](f"**Recommendation: {dec}**")
            st.markdown("**Why? (simple risk flags)**")
            flags = []
            if amnt / income > 0.30: flags.append(f"Loan is {amnt/income:.0%} of annual income (above 30% is risky)")
            if grade in "DEFG": flags.append(f"Loan grade {grade} is a weak grade")
            if prior == "Y": flags.append("Applicant has defaulted before")
            if home in ("RENT", "OTHER"): flags.append(f"Home ownership = {home} (historically higher default rate)")
            if rate > 14: flags.append(f"High interest rate ({rate}%) signals lender-assessed risk")
            if not flags: flags.append("No major red flags found")
            for f in flags: st.write("• " + f)
        else:
            st.info("Fill the form and click **Assess applicant**.")

# ---------------------------------------------------------------- TAB 2
with tab2:
    data = load_scored_data()
    f1, f2, f3 = st.columns(3)
    g = f1.multiselect("Loan grade", sorted(data.loan_grade.unique()), default=sorted(data.loan_grade.unique()))
    h = f2.multiselect("Home ownership", sorted(data.person_home_ownership.unique()), default=sorted(data.person_home_ownership.unique()))
    i = f3.multiselect("Loan purpose", sorted(data.loan_intent.unique()), default=sorted(data.loan_intent.unique()))
    d = data[data.loan_grade.isin(g) & data.person_home_ownership.isin(h) & data.loan_intent.isin(i)]
    if d.empty:
        st.warning("No applicants match these filters.")
    else:
        k = st.columns(5)
        k[0].metric("Applications", f"{len(d):,}")
        k[1].metric("Historical default rate", f"{d.loan_status.mean():.1%}")
        k[2].metric("Avg predicted PD", f"{d.pd.mean():.1%}")
        k[3].metric("Avg loan", f"{d.loan_amnt.mean():,.0f}")
        k[4].metric("Avg income", f"{d.person_income.mean():,.0f}")
        a, b = st.columns(2)
        with a:
            st.markdown("**Risk category distribution**")
            fig, ax = plt.subplots(figsize=(5, 3.4)); rc = d.risk.value_counts().reindex(list(COLORS)).fillna(0)
            ax.pie(rc, labels=rc.index, colors=list(COLORS.values()), autopct="%1.0f%%", startangle=90, wedgeprops=dict(width=.45))
            st.pyplot(fig)
        with b:
            st.markdown("**Final recommendations**")
            st.bar_chart(d.decision.value_counts().reindex(["Approve Loan", "Review Manually", "Reject Application"]).fillna(0))
        c, e = st.columns(2)
        with c:
            st.markdown("**Default rate by loan grade**")
            st.bar_chart(d.groupby("loan_grade").loan_status.mean())
        with e:
            st.markdown("**Average loan amount by purpose (loan trends)**")
            st.bar_chart(d.groupby("loan_intent").loan_amnt.mean())
        c, e = st.columns(2)
        with c:
            st.markdown("**Default rate by age group**")
            ag = pd.cut(d.person_age, [17, 25, 30, 35, 45, 100], labels=["18-25", "26-30", "31-35", "36-45", "46+"])
            st.line_chart(d.groupby(ag, observed=True).loan_status.mean())
        with e:
            st.markdown("**Avg loan-to-income ratio by risk category**")
            st.bar_chart(d.groupby("risk").loan_percent_income.mean().reindex(list(COLORS)))
        with st.expander("Highest-risk applicants (top 15)"):
            st.dataframe(d.sort_values("pd", ascending=False).head(15)[
                ["person_age", "person_income", "loan_grade", "loan_amnt", "loan_percent_income", "pd", "risk", "decision"]]
                .style.format({"pd": "{:.1%}"}), width="stretch")

# ---------------------------------------------------------------- TAB 3
with tab3:
    st.subheader("Model comparison (20% held-out test set)")
    st.dataframe(pd.DataFrame(metrics["comparison"]).T.round(3), width="stretch")
    st.success(f"Selected model: **{metrics['best_model']}** (highest ROC-AUC), then probability-calibrated.")
    a, b = st.columns(2)
    a.image("outputs/charts/05_roc_curves.png", caption="ROC curves")
    b.image("outputs/charts/07_risk_bands.png", caption="Do risk bands match reality? Yes - actual default rate rises Low -> High")
    st.image("outputs/charts/06_model_diagnostics.png")
    st.caption(f"Decision rule: PD < {APPROVE_BELOW:.0%} Approve | {APPROVE_BELOW:.0%}-{REJECT_FROM:.0%} Review manually | >= {REJECT_FROM:.0%} Reject")
