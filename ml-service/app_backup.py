from flask import Flask, request, jsonify
import pandas as pd
import joblib
import matplotlib.pyplot as plt

app = Flask(__name__)

MODEL_PATH = (
    "churn-service/model/churn_model.pkl"
)

model = joblib.load(
    MODEL_PATH
)


def create_features(df):

    df.columns = df.columns.str.strip()

    # Create derived features WITHOUT renaming originals

    df["Trade_Drop_Percent"] = (
        (
            df["Trades_7D"]
            -
            df["Trades_30D"]
        )
        /
        (
            df["Trades_7D"]
            + 1
        )
    )

    df["Login_Drop_Percent"] = (
        (
            df["Login_7D"]
            -
            df["Login_30D"]
        )
        /
        (
            df["Login_7D"]
            + 1
        )
    )

    df["Engagement_Score"] = (
        (
            df["Email_Open_Rate"]
            +
            df["Push_Click_Rate"]
        ) / 2
    )

    df["Withdrawal_Ratio"] = (
        df["Withdrawals"]
        /
        (
            df["Deposits"]
            + 1
        )
    )

    # create missing model features

    df["Net_Flow"] = (
        df["Deposits"]
        -
        df["Withdrawals"]
    )

    df["PnL"] = (
        df["Portfolio_Value"]
        -
        df["Invested_Amount"]
    )

    df["PnL_Percent"] = (
        (
            df["PnL"]
        )
        /
        (
            df["Invested_Amount"]
            + 1
        )
    )

    print("\nFinal Features:")
    print(df.columns.tolist())

    return df

@app.route(
"/predict",
methods=["POST"]
)
def predict():

    file = request.files["file"]

    df = pd.read_csv(file)

    print("\nCSV Columns:")
    print(df.columns.tolist())

    df = create_features(df)

    X = df.drop(
    columns=[
        "Customer_ID",
        "Exit_Label"
    ],
    errors="ignore"
)
    print("\nModel Input Columns:")
    print(X.columns.tolist())
    print("\nShape:", X.shape)

    probability = ( 
        model.predict_proba(X)
        [:, 1]
    )

    from sklearn.metrics import (
        roc_auc_score,
        precision_score,
        recall_score
        )   

    if "Exit_Label" in df.columns:

        y = df["Exit_Label"]

        pred = probability

        print(
            "\nROC AUC:",
            roc_auc_score(
                y,
                pred
            )
        )

        pred_class = (
            pred > 0.2
        ).astype(int)

        print(
            "Precision:",
            precision_score(
                y,
                pred_class
            )
        )

        print(
            "Recall:",
            recall_score(
                y,
                pred_class
            )
        )

    print("\nProbability stats")
    print("Min:", probability.min())
    print("Max:", probability.max())
    print("Mean:", probability.mean())

    def risk(x):

        if x >= 0.7:
            return "High Risk"

        elif x >= 0.4:
            return "Medium Risk"

        return "Low Risk"

    df[
        "final_churn_probability"
    ] = probability

    df[
        "Risk_Level"
    ] = (
        df[
            "final_churn_probability"
        ]
        .apply(risk)
    )

    df[
        "Primary_Reason"
    ] = "Engagement Decline"

    df.loc[
        df["Trade_Drop_Percent"] > 0.5,
        "Primary_Reason"
    ] = "Low Trading Activity"

    df.loc[
        df["Login_Drop_Percent"] > 0.4,
        "Primary_Reason"
    ] = "Login Frequency Drop"

    df.loc[
        df["Withdrawal_Ratio"] > 1,
        "Primary_Reason"
    ] = "High Withdrawals"

    return jsonify(
        df[
            [
                "Customer_ID",
                "final_churn_probability",
                "Risk_Level",
                "Primary_Reason"
            ]
        ].to_dict(
            orient="records"
        )
    )


if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )