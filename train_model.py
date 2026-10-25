"""
Run:  python train_model.py
Does Modules 1-3: cleaning -> EDA charts -> model training/comparison -> saves best model.
Outputs: models/credit_model.joblib, models/metrics.json, outputs/charts/*.png, data/clean_data.csv
"""
import json, warnings
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, roc_curve, confusion_matrix, ConfusionMatrixDisplay)
from credit_utils import *

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="deep")
CH = "outputs/charts/"
def save(name):
    plt.tight_layout(); plt.savefig(CH + name, dpi=130); plt.close()

# ---------------- MODULE 1: load + clean ----------------
raw = load_raw()
df, log = clean_data(raw)
df.to_csv("data/clean_data.csv", index=False)
print("CLEANING LOG:", log)

# ---------------- MODULE 2: EDA ----------------
fig, ax = plt.subplots(1, 2, figsize=(10, 4))
counts = df[TARGET].value_counts().sort_index()
ax[0].bar(["Repaid (0)", "Default (1)"], counts.values, color=["#2a9d8f", "#e63946"])
for i, v in enumerate(counts.values): ax[0].text(i, v, f"{v:,}\n({v/len(df):.1%})", ha="center", va="bottom")
ax[0].set_title("Class balance (imbalanced!)"); ax[0].set_ylim(0, counts.max() * 1.2)
sns.histplot(data=df, x="person_income", hue=TARGET, log_scale=True, bins=40, ax=ax[1], element="step")
ax[1].set_title("Income distribution (log scale)")
save("01_target_and_income.png")

order = sorted(df.loan_grade.unique())
fig, ax = plt.subplots(1, 3, figsize=(15, 4))
for a, col, title in zip(ax, ["loan_grade", "person_home_ownership", "loan_intent"],
                         ["Default rate by loan grade", "Default rate by home ownership", "Default rate by loan purpose"]):
    r = df.groupby(col)[TARGET].mean().sort_values(ascending=(col != "loan_grade"))
    if col == "loan_grade": r = r.reindex(order)
    sns.barplot(x=r.index, y=r.values, ax=a, color="#457b9d"); a.set_title(title); a.set_ylabel("Default rate")
    a.tick_params(axis="x", rotation=30)
save("02_default_rates.png")

fig, ax = plt.subplots(1, 3, figsize=(15, 4))
sns.boxplot(data=df, x=TARGET, y="loan_percent_income", ax=ax[0]); ax[0].set_title("Loan-to-income ratio vs default")
sns.boxplot(data=df, x=TARGET, y="loan_int_rate", ax=ax[1]); ax[1].set_title("Interest rate vs default")
sns.boxplot(data=df, x=TARGET, y="loan_amnt", ax=ax[2]); ax[2].set_title("Loan amount vs default")
save("03_boxplots.png")

plt.figure(figsize=(8, 6))
sns.heatmap(df[NUM_COLS + [TARGET]].corr(), annot=True, fmt=".2f", cmap="coolwarm", center=0)
plt.title("Correlation heatmap"); save("04_correlation.png")

# ---------------- MODULE 3: models ----------------
X, y = df[FEATURES], df[TARGET]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

prep = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM_COLS),
    ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS)])

models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Decision Tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=50, class_weight="balanced", random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced_subsample",
                                            n_jobs=-1, random_state=42)}
results, fitted = {}, {}
plt.figure(figsize=(6, 5))
for name, m in models.items():
    pipe = Pipeline([("prep", prep), ("model", m)]).fit(Xtr, ytr)
    p = pipe.predict_proba(Xte)[:, 1]; pred = pipe.predict(Xte)
    results[name] = dict(accuracy=accuracy_score(yte, pred), precision=precision_score(yte, pred),
                         recall=recall_score(yte, pred), f1=f1_score(yte, pred), roc_auc=roc_auc_score(yte, p))
    fitted[name] = pipe
    fpr, tpr, _ = roc_curve(yte, p); plt.plot(fpr, tpr, label=f"{name} (AUC={results[name]['roc_auc']:.3f})")
plt.plot([0, 1], [0, 1], "k--"); plt.xlabel("False positive rate"); plt.ylabel("True positive rate")
plt.title("ROC curves"); plt.legend(); save("05_roc_curves.png")
res = pd.DataFrame(results).T.round(3); print(res)

best_name = res["roc_auc"].idxmax(); print("BEST MODEL:", best_name)
best = fitted[best_name]

# Class weighting inflates probabilities, so calibrate them -> honest "probability of default"
final = CalibratedClassifierCV(best, method="isotonic", cv=3).fit(Xtr, ytr)  # clones & refits internally
pd_test = final.predict_proba(Xte)[:, 1]
cm_pred = (pd_test >= REJECT_FROM).astype(int)

fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
ConfusionMatrixDisplay(confusion_matrix(yte, best.predict(Xte)), display_labels=["Repaid", "Default"]).plot(ax=ax[0], cmap="Blues", colorbar=False)
ax[0].set_title(f"{best_name} confusion matrix (threshold 0.5)")
rf = best.named_steps["model"]
names = best.named_steps["prep"].get_feature_names_out()
if hasattr(rf, "feature_importances_"):
    imp = pd.Series(rf.feature_importances_, index=names).sort_values().tail(12)
    colors = "#457b9d"; ttl = "Top 12 features (importance)"
else:  # logistic regression: signed coefficients  (+ raises risk, - lowers risk)
    co = pd.Series(rf.coef_[0], index=names)
    imp = co.reindex(co.abs().sort_values().tail(12).index)
    colors = ["#e63946" if v > 0 else "#2a9d8f" for v in imp]; ttl = "Top 12 coefficients (red = raises risk, green = lowers)"
imp.index = [i.split("__")[1] for i in imp.index]
imp.plot.barh(ax=ax[1], color=colors); ax[1].set_title(ttl)
save("06_model_diagnostics.png")

seg = pd.DataFrame({"pd": pd_test, "actual": yte.values}); seg["risk"] = seg.pd.apply(risk_category)
summary = seg.groupby("risk").agg(applicants=("pd", "size"), actual_default_rate=("actual", "mean"), avg_pd=("pd", "mean"))
summary = summary.reindex(["Low Risk", "Medium Risk", "High Risk"]); print(summary.round(3))
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
sns.histplot(pd_test, bins=40, ax=ax[0], color="#457b9d"); ax[0].axvline(APPROVE_BELOW, c="g", ls="--"); ax[0].axvline(REJECT_FROM, c="r", ls="--")
ax[0].set_title("Predicted default probability (test set)"); ax[0].set_xlabel("PD")
ax[1].bar(summary.index, summary.actual_default_rate, color=["#2a9d8f", "#f4a261", "#e63946"])
ax[1].set_title("Actual default rate per risk band"); ax[1].set_ylabel("Actual default rate")
save("07_risk_bands.png")

joblib.dump(final, "models/credit_model.joblib")
json.dump(dict(cleaning=log, comparison=res.to_dict("index"), best_model=best_name,
               risk_bands=summary.round(4).to_dict("index"), n_train=len(Xtr), n_test=len(Xte),
               calibrated_roc_auc=float(roc_auc_score(yte, pd_test)),
               thresholds=dict(approve_below=APPROVE_BELOW, reject_from=REJECT_FROM)),
          open("models/metrics.json", "w"), indent=2)
print("Saved model + metrics + charts.")
