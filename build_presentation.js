const pptxgen = require("pptxgenjs");
const { applyTheme } = require("/mnt/skills/public/pptx/scripts/apply_theme.js");
const m = require("/home/claude/credit-risk-analysis-system/models/metrics.json");
const CH = "/home/claude/credit-risk-analysis-system/outputs/charts/";
const THEME = { name: "RiskNavy", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "1B263B", lt1: "FFFFFF", dk2: "1D3557", lt2: "F1F5F9", accent1: "457B9D", accent2: "2A9D8F",
            accent3: "F4A261", accent4: "E63946", accent5: "6D597A", accent6: "8D99AE", hlink: "457B9D", folHlink: "6D597A" } };
const pres = new pptxgen(); pres.layout = "LAYOUT_16x9"; pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "Credit Risk Analysis System"; pres.author = "Ananya Kumar Srivastava";
const C = pres.SchemeColor;
pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: "1D3557" }, objects: [], slideNumber: undefined });
pres.defineSlideMaster({ title: "CONTENT", background: { color: "FFFFFF" },
  objects: [{ rect: { x: 0, y: 0, w: 10, h: 0.12, fill: { color: "2A9D8F" } } }],
  slideNumber: { x: 9.2, y: 5.25, w: 0.5, h: 0.3, fontSize: 10, color: "8D99AE" } });
pres.addSection({ title: "Credit Risk" });
const S = (t) => { const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Credit Risk" }); s.addText(t, { x: 0.5, y: 0.3, w: 9, h: 0.7, fontSize: 26, bold: true, color: "1D3557", margin: 0, valign: "middle", isTextBox: true, objectName: "Slide title" }); return s; };
const card = (s, x, y, w, h, color, head, body, name) => {
  s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: "F1F5F9" }, line: { color: "F1F5F9" }, objectName: name + " card" });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.08, h, fill: { color }, line: { color }, objectName: name + " bar" });
  s.addText(head, { x: x + 0.25, y: y + 0.1, w: w - 0.4, h: 0.4, fontSize: 16, bold: true, color: "1D3557", margin: 0, isTextBox: true, objectName: name + " head" });
  s.addText(body, { x: x + 0.25, y: y + 0.5, w: w - 0.4, h: h - 0.6, fontSize: 14, color: "1B263B", margin: 0, valign: "top", isTextBox: true, objectName: name + " body" });
};
const pct = (v) => (v * 100).toFixed(1) + "%";

// 1 title
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Credit Risk" });
s.addText("Credit Risk Analysis System", { x: 0.7, y: 1.6, w: 8.6, h: 1, fontSize: 40, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
s.addText("Predicting loan default and recommending Approve / Review / Reject", { x: 0.7, y: 2.6, w: 8.6, h: 0.5, fontSize: 18, color: "A8DADC", margin: 0, isTextBox: true });
s.addText("Data Science Capstone - SkillOrbit\nAnanya Kumar Srivastava, MNIT Jaipur", { x: 0.7, y: 3.9, w: 8, h: 0.8, fontSize: 14, color: "FFFFFF", margin: 0, isTextBox: true });
s.addNotes("Introduce the problem: banks need to decide who will repay. We predict probability of default and turn it into a decision.");

// 2 problem
s = S("The problem and our goal");
card(s, 0.5, 1.2, 4.3, 1.7, "E63946", "The problem", "Approving a bad loan loses money. Rejecting a good customer loses business. Banks need a fast, consistent way to judge risk.", "problem");
card(s, 5.2, 1.2, 4.3, 1.7, "2A9D8F", "Our solution", "A model that outputs each applicant's probability of default (PD), then a risk band and a recommendation.", "solution");
card(s, 0.5, 3.15, 9, 1.7, "457B9D", "Objectives", "Analyze customer data  |  Identify low / high-risk applicants  |  Predict approval probability  |  Dashboard of risk patterns  |  Automatic loan recommendation", "objectives");
s.addNotes("One number, PD, drives everything: risk category, approval probability and the final decision.");

// 3 workflow
s = S("End-to-end workflow");
const steps = ["Dataset", "Cleaning", "EDA", "Model training", "Risk prediction", "Dashboard", "Recommendation"];
steps.forEach((t, i) => {
  const x = 0.3 + i * 1.34;
  s.addShape(pres.shapes.OVAL, { x: x + 0.35, y: 1.8, w: 0.6, h: 0.6, fill: { color: i % 2 ? "2A9D8F" : "1D3557" }, line: { color: "FFFFFF" }, objectName: "step " + (i + 1) });
  s.addText(String(i + 1), { x: x + 0.35, y: 1.8, w: 0.6, h: 0.6, align: "center", valign: "middle", fontSize: 18, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
  s.addText(t, { x: x, y: 2.55, w: 1.3, h: 0.6, align: "center", fontSize: 11, bold: true, color: "1D3557", margin: 0, isTextBox: true });
});
s.addText("Tech stack: Python, Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, Streamlit (deployed on Streamlit Cloud)", { x: 0.5, y: 3.8, w: 9, h: 0.6, fontSize: 14, color: "1B263B", align: "center", margin: 0, isTextBox: true });

// 4 cleaning
s = S("Data cleaning: " + m.cleaning.rows_raw.toLocaleString() + " raw rows to " + m.cleaning.rows_clean.toLocaleString() + " clean rows");
const stats = [[m.cleaning.duplicates_removed, "duplicates removed"], [m.cleaning.impossible_age_removed + m.cleaning.impossible_emp_length_removed, "impossible values removed (age 144, 123 yrs work)"],
  [m.cleaning.missing_emp_length + m.cleaning.missing_loan_int_rate, "missing values filled with median"]];
stats.forEach(([n, l], i) => {
  const x = 0.5 + i * 3.05;
  s.addShape(pres.shapes.RECTANGLE, { x, y: 1.3, w: 2.85, h: 1.7, fill: { color: "F1F5F9" }, line: { color: "F1F5F9" }, objectName: "stat card " + (i + 1) });
  s.addText(Number(n).toLocaleString(), { x, y: 1.4, w: 2.85, h: 0.8, align: "center", fontSize: 36, bold: true, color: ["E63946", "F4A261", "2A9D8F"][i], margin: 0, isTextBox: true });
  s.addText(l, { x: x + 0.15, y: 2.2, w: 2.55, h: 0.7, align: "center", fontSize: 12, color: "1B263B", margin: 0, isTextBox: true });
});
s.addText([{ text: "Encoding: ", options: { bold: true } }, { text: "one-hot for categories.  " }, { text: "Scaling: ", options: { bold: true } }, { text: "StandardScaler.  " },
  { text: "Split: ", options: { bold: true } }, { text: "80/20 stratified.  " }, { text: "No leakage: ", options: { bold: true } }, { text: "imputer, scaler and encoder are fitted on training data only (inside a Pipeline)." }],
  { x: 0.5, y: 3.4, w: 9, h: 1, fontSize: 14, color: "1B263B", margin: 0, valign: "top", isTextBox: true });

// 5 EDA
s = S("EDA: what drives default?");
s.addImage({ path: CH + "02_default_rates.png", x: 0.5, y: 1.1, w: 9, h: 2.7, altText: "Default rate by grade, home ownership and purpose" });
s.addText("Worse loan grade, renting, and a high loan-to-income ratio all push default risk up. Only ~22% of loans default, so the data is imbalanced and accuracy alone would mislead.",
  { x: 0.5, y: 4.0, w: 9, h: 0.9, fontSize: 14, color: "1B263B", margin: 0, valign: "top", isTextBox: true });

// 6 models
s = S("Three models compared on the test set");
const names = Object.keys(m.comparison);
s.addChart(pres.charts.BAR, [
  { name: "ROC-AUC", labels: names, values: names.map(n => +m.comparison[n].roc_auc.toFixed(3)) },
  { name: "Recall", labels: names, values: names.map(n => +m.comparison[n].recall.toFixed(3)) },
  { name: "F1", labels: names, values: names.map(n => +m.comparison[n].f1.toFixed(3)) }],
  { x: 0.5, y: 1.1, w: 5.6, h: 3.8, barDir: "col", chartColors: ["1D3557", "2A9D8F", "F4A261"], showLegend: true, legendPos: "b", legendFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelFormatCode: "0.00", dataLabelFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valAxisMinVal: 0, valAxisMaxVal: 1, valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" }, showTitle: true, title: "Test-set metrics", titleFontFace: "+mn-lt", titleFontSize: 14 });
card(s, 6.3, 1.2, 3.2, 3.6, "457B9D", "Why these metrics?", "Class weighting handles the 78/22 imbalance.\n\nWe report recall, F1 and ROC-AUC, not just accuracy.\n\nSelected: " + m.best_model + " (highest ROC-AUC).", "metrics note");

// 7 calibration and bands
s = S("Calibrated risk score: bands match reality");
s.addImage({ path: CH + "07_risk_bands.png", x: 0.5, y: 1.1, w: 5.9, h: 2.15, altText: "PD distribution and default rate per band" });
const rows = [[{ text: "Band", options: { bold: true, color: "FFFFFF", fill: { color: "1D3557" } } }, { text: "Applicants", options: { bold: true, color: "FFFFFF", fill: { color: "1D3557" } } }, { text: "Actual default", options: { bold: true, color: "FFFFFF", fill: { color: "1D3557" } } }]]
  .concat(Object.entries(m.risk_bands).map(([k, v]) => [k, v.applicants.toLocaleString(), pct(v.actual_default_rate)]));
s.addTable(rows, { x: 6.6, y: 1.2, w: 2.9, colW: [1.0, 0.9, 1.0], fontSize: 11, border: { type: "solid", color: "E2E8F0", pt: 0.5 } });
s.addText("Class weighting inflates probabilities, so we calibrate (isotonic): a predicted 20% now means about 20% really default. Actual default rises from Low to High - the score works.",
  { x: 0.5, y: 3.6, w: 9, h: 1.2, fontSize: 14, color: "1B263B", margin: 0, valign: "top", isTextBox: true });

// 8 recommendation
s = S("Final recommendation logic");
const th = m.thresholds;
card(s, 0.5, 1.3, 2.9, 2.4, "2A9D8F", "Approve Loan", "PD below " + (th.approve_below * 100) + "%\nLow Risk\nVery likely to repay", "approve");
card(s, 3.55, 1.3, 2.9, 2.4, "F4A261", "Review Manually", (th.approve_below * 100) + "% to " + (th.reject_from * 100) + "%\nMedium Risk\nSend to a human analyst", "review");
card(s, 6.6, 1.3, 2.9, 2.4, "E63946", "Reject Application", "PD " + (th.reject_from * 100) + "% or more\nHigh Risk\nLikely to default", "reject");
s.addText("Thresholds are adjustable constants - a bank tunes them to its risk appetite.", { x: 0.5, y: 4.05, w: 9, h: 0.5, fontSize: 14, italic: true, color: "1B263B", align: "center", margin: 0, isTextBox: true });

// 9 dashboard
s = S("Streamlit dashboard");
card(s, 0.5, 1.2, 2.9, 3.4, "1D3557", "1. Risk Predictor", "Enter applicant details.\n\nGet a risk gauge, default and approval probability, risk category, recommendation and plain-language risk flags.", "tab1");
card(s, 3.55, 1.2, 2.9, 3.4, "2A9D8F", "2. Portfolio", "KPIs, risk-category pie, decision counts, default rate by grade and age, loan trends by purpose.\n\nFilters for grade, home ownership and purpose.", "tab2");
card(s, 6.6, 1.2, 2.9, 3.4, "F4A261", "3. Model Performance", "Metric comparison, ROC curves, confusion matrix and the top drivers of risk.", "tab3");

// 10 conclusion
s = S("Limitations and conclusion");
card(s, 0.5, 1.2, 4.3, 3.4, "E63946", "Limitations", "Public dataset only; no real banking integration.\n\nThresholds are illustrative.\n\nNo fairness audit yet.", "limits");
card(s, 5.2, 1.2, 4.3, 3.4, "2A9D8F", "Conclusion and next steps", "A complete pipeline from raw data to a deployed, explainable decision tool.\n\nNext: SHAP explanations, gradient boosting, batch CSV scoring, MySQL storage.", "next");

(async () => { await pres.writeFile({ fileName: "/home/claude/credit-risk-analysis-system/outputs/Project_Presentation.pptx" });
  await applyTheme("/home/claude/credit-risk-analysis-system/outputs/Project_Presentation.pptx", THEME); console.log("ok"); })();
