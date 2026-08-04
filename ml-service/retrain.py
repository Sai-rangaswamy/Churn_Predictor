import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier

MODEL_PATH = "churn-service/model/churn_model.pkl"
BACKUP_DIR = "churn-service/model/backups"
ORIGINAL_DATA_PATH = "customer_churn_dataset.csv"
FEEDBACK_LOG_PATH = "feedback/predictions_log.csv"

# Columns added by the prediction pipeline (not raw input)
LOG_META_COLUMNS = [
    "Prediction_Date",
    "Predicted_Probability",
    "Predicted_Risk_Level",
    "Actual_Outcome",
]


def create_features(df):
    df = df.copy()

    df["Trade_Drop_Percent"] = (
        (df["Trades_7D"] - df["Trades_30D"])
        / (df["Trades_30D"] + 1)
    )

    df["Login_Drop_Percent"] = (
        (df["Login_7D"] - df["Login_30D"])
        / (df["Login_30D"] + 1)
    )

    df["Net_Flow"] = df["Deposits"] - df["Withdrawals"]
    df["Withdrawal_Ratio"] = (
        df["Withdrawals"] / (df["Deposits"] + 1)
    )

    df["PnL"] = df["Portfolio_Value"] - df["Invested_Amount"]
    df["PnL_Percent"] = (
        df["PnL"] / (df["Invested_Amount"] + 1)
    ) * 100

    df["Engagement_Score"] = (
        df["Email_Open_Rate"] + df["Push_Click_Rate"]
    ) / 2

    return df


def build_pipeline(X):

    cat = X.select_dtypes(include="object").columns
    num = X.select_dtypes(exclude="object").columns

    preprocess = ColumnTransformer(
        [
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore"),
                cat,
            ),
            (
                "num",
                "passthrough",
                num,
            ),
        ]
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
    )

    return Pipeline(
        [
            ("prep", preprocess),
            ("model", model),
        ]
    )


def run_retrain():
    """
    Merges feedback data (labeled predictions) with original training
    data, retrains the XGBoost pipeline, backs up the old model, and
    saves the new one. Returns a summary dict.
    """

    os.makedirs(BACKUP_DIR, exist_ok=True)

    # ── 1. Load & prepare feedback data ──────────────────────────────
    log_df = pd.read_csv(FEEDBACK_LOG_PATH)
    labeled = log_df[log_df["Actual_Outcome"].notna()].copy()

    # Strip prediction-metadata columns; keep raw customer columns
    feedback_raw = labeled.drop(
        columns=LOG_META_COLUMNS, errors="ignore"
    )
    feedback_raw["Exit_Label"] = labeled["Actual_Outcome"].astype(int)
    feedback_raw = create_features(feedback_raw)

    # ── 2. Load & prepare original training data ──────────────────────
    original_df = (
        pd.read_csv(ORIGINAL_DATA_PATH)
        .drop_duplicates()
        .fillna(0)
        .reset_index(drop=True)
    )
    original_df = create_features(original_df)

    # ── 3. Combine ────────────────────────────────────────────────────
    combined = pd.concat(
        [original_df, feedback_raw], ignore_index=True
    )

    X = combined.drop(
        columns=["Customer_ID", "Exit_Label"], errors="ignore"
    )
    y = combined["Exit_Label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        stratify=y,
        random_state=42,
    )

    # ── 4. Evaluate current model ─────────────────────────────────────
    old_model = joblib.load(MODEL_PATH)
    old_preds = old_model.predict(X_test)
    old_accuracy = round(accuracy_score(y_test, old_preds) * 100, 2)

    # ── 5. Train new model ────────────────────────────────────────────
    new_pipeline = build_pipeline(X_train)
    new_pipeline.fit(X_train, y_train)
    new_preds = new_pipeline.predict(X_test)
    new_accuracy = round(accuracy_score(y_test, new_preds) * 100, 2)

    # ── 6. Backup old model ───────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(
        BACKUP_DIR, f"churn_model_{timestamp}.pkl"
    )
    joblib.dump(old_model, backup_path)

    # ── 7. Save new model ─────────────────────────────────────────────
    joblib.dump(new_pipeline, MODEL_PATH)

    return {
        "status": "retrained",
        "feedback_rows_used": int(len(labeled)),
        "total_training_rows": int(len(combined)),
        "accuracy_before": old_accuracy,
        "accuracy_after": new_accuracy,
        "backup_saved_to": backup_path,
        "timestamp": timestamp,
    }
