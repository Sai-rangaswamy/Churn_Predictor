import os
import joblib
import numpy as np
import pandas as pd
import shap

from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

MODEL_DIR = "churn-service/model"
os.makedirs(MODEL_DIR, exist_ok=True)


def load_data(path):
    df = pd.read_csv(path)
    df = (
        df
        .drop_duplicates()
        .fillna(0)
        .reset_index(drop=True)
    )
    return df


def create_features(df):

    # Trade activity drop (negative = 7D activity is lower than 30D avg → declining)
    df["Trade_Drop_Percent"] = (
        (df["Trades_7D"] - df["Trades_30D"])
        / (df["Trades_30D"] + 1)
    )

    # Login activity drop
    df["Login_Drop_Percent"] = (
        (df["Login_7D"] - df["Login_30D"])
        / (df["Login_30D"] + 1)
    )

    # Money flow signals
    df["Net_Flow"] = df["Deposits"] - df["Withdrawals"]
    df["Withdrawal_Ratio"] = (
        df["Withdrawals"] / (df["Deposits"] + 1)
    )

    # Portfolio profitability
    df["PnL"] = df["Portfolio_Value"] - df["Invested_Amount"]
    df["PnL_Percent"] = (
        df["PnL"] / (df["Invested_Amount"] + 1)
    ) * 100

    # Engagement composite
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
                cat
            ),
            (
                "num",
                "passthrough",
                num
            )
        ]
    )

    model = XGBClassifier(
        n_estimators=300,
        max_depth=3,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    return Pipeline(
        [
            ("prep", preprocess),
            ("model", model)
        ]
    )


def train_model(df):

    X = df.drop(
        columns=["Customer_ID", "Exit_Label"],
        errors="ignore"
    )

    y = df["Exit_Label"]

    pipeline = build_pipeline(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )

    pipeline.fit(X_train, y_train)

    # SHAP-based Primary_Reason (top contributing feature per customer)
    X_transformed = pipeline.named_steps["prep"].transform(X)
    feature_names = pipeline.named_steps["prep"].get_feature_names_out()
    xgb_model = pipeline.named_steps["model"]

    explainer = shap.TreeExplainer(xgb_model)
    shap_values = explainer(X_transformed)

    reasons = []
    for i in range(len(df)):
        abs_vals = np.abs(shap_values.values[i])
        top_idx = abs_vals.argmax()
        reason = (
            feature_names[top_idx]
            .replace("num__", "")
            .replace("cat__", "")
        )
        reasons.append(reason)

    df["Primary_Reason"] = reasons

    probs = pipeline.predict_proba(X)[:, 1]

    joblib.dump(pipeline, f"{MODEL_DIR}/churn_model.pkl")
    print("Model trained and saved to:", f"{MODEL_DIR}/churn_model.pkl")

    return pipeline, probs, df


def calculate_churn(df, probs):

    df["final_churn_probability"] = probs

    def risk(x):
        if x >= 0.7:
            return "High Risk"
        elif x >= 0.4:
            return "Medium Risk"
        return "Low Risk"

    df["Risk_Level"] = (
        df["final_churn_probability"].apply(risk)
    )

    return df


if __name__ == "__main__":

    df = load_data("customer_churn_dataset.csv")

    df = create_features(df)

    pipeline, probs, df = train_model(df)

    result = calculate_churn(df, probs)

    output = result[
        [
            "Customer_ID",
            "final_churn_probability",
            "Risk_Level",
            "Primary_Reason"
        ]
    ].sort_values(
        "final_churn_probability",
        ascending=False
    ).reset_index(drop=True)

    print(output.head(20))
    print(output.tail(20))

    output.to_csv("churn_results.csv", index=False)
