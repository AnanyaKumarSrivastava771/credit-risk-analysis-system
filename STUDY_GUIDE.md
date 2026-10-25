# Study Guide - how to explain this project

## 30-second pitch
"Banks must decide who will repay a loan. I built a system that takes an applicant's financial details, predicts the
probability they will default using machine learning, converts that into Low/Medium/High risk, shows it on a Streamlit
dashboard, and recommends Approve, Review Manually or Reject."

## The one core idea
Everything is ONE number: PD = probability of default (0 to 1).
- Approval probability = 1 - PD
- Risk category = PD cut into 3 bands
- Recommendation = same cut points turned into an action

## Walk through the code (in the order you will present)
1. credit_utils.py - cleaning rules, column lists, thresholds, recommendation function. Used by both training and app so they never disagree.
2. train_model.py
   - Cleaning: drop duplicates, drop age > 100 and employment > 60 years (data-entry errors). Missing values are left as NaN and imputed inside the pipeline.
   - EDA: 4 chart files that answer "what drives default?".
   - Split: 80/20, stratified (keeps 22% default in both parts), random_state=42 for reproducibility.
   - Pipeline: ColumnTransformer = numeric (median impute -> StandardScaler) + categorical (OneHotEncoder), then the model.
   - Three models trained, compared on test set; best by ROC-AUC is chosen.
   - Calibration (CalibratedClassifierCV, isotonic) so probabilities are trustworthy.
   - Saved with joblib; metrics and charts saved for the dashboard and report.
3. app.py - loads the saved model, builds the input row, calls predict_proba, draws gauge, applies recommendation(); two more tabs for portfolio view and model performance.

## Concepts you must be able to explain
- **Class imbalance**: 78% repay, 22% default. A model that says "everyone repays" gets 78% accuracy and is useless. Fix: class_weight + judge by recall/F1/ROC-AUC.
- **Precision vs recall (here)**: recall = of real defaulters, how many did we catch (missing one costs money). Precision = of those we flagged, how many really default (false alarms lose good customers).
- **ROC-AUC**: chance the model ranks a random defaulter above a random non-defaulter. 0.5 = coin flip, 1.0 = perfect.
- **Data leakage**: if you compute mean/scale on ALL data before splitting, test info leaks into training. Pipeline fits everything on train only.
- **Why scaling**: Logistic Regression is sensitive to feature size (income ~50,000 vs age ~30). Trees do not need it, but one pipeline serves all.
- **One-hot encoding**: models need numbers; each category becomes its own 0/1 column.
- **Logistic Regression**: weighted sum of features pushed through an S-curve to give 0-1 probability. Coefficients are interpretable (positive = raises risk).
- **Decision Tree**: yes/no questions splitting applicants into groups. Depth limited to 6 to avoid memorizing (overfitting).
- **Random Forest**: 300 trees voting; more accurate and stable, less interpretable.
- **Overfitting**: great on training data, poor on new data. We test on unseen data to detect it.
- **Calibration**: class weighting pushes probabilities up. Calibration fixes this so "20%" truly means ~20%. Proof: actual default rate per band (7% / 23% / 67%) matches predicted PD.
- **Thresholds**: 15% and 40% are business choices. Lower approve threshold = safer but fewer loans.

## Honest points to state in a viva
- The numbers in the report were produced on a stand-in dataset with the Kaggle schema because Kaggle needs a login. Re-run on the real CSV before submitting. On the real Kaggle data expect Random Forest to win with ROC-AUC around 0.93 (verify, don't quote from memory).
- No hyper-parameter tuning, fairness audit or real bank integration - all outside the stated scope.

## Likely questions and answers
1. Why not just use accuracy? -> Imbalance; accuracy hides missed defaulters.
2. Why Pipeline? -> No leakage, and the same preprocessing at prediction time.
3. Why calibrate? -> Thresholds on PD only make sense if PD is an honest probability.
4. Which feature matters most? -> Loan grade, loan-to-income ratio, interest rate, home ownership (see chart 06).
5. How would a bank use "Review Manually"? -> Borderline cases go to a human analyst, saving time while limiting risk.
6. What if the model is wrong? -> That is why the middle band exists; also monitor performance and retrain.
7. Can this be biased? -> Yes, if data reflect past bias; a production system needs a fairness audit.
8. How does the app predict? -> Form values -> one-row DataFrame -> same Pipeline -> predict_proba -> PD -> risk band -> recommendation.
