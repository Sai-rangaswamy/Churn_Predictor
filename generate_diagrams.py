import zlib
import base64
import urllib.request
import os

def generate_kroki_url(diagram_type, text):
    compressed = zlib.compress(text.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
    return f"https://kroki.io/{diagram_type}/png/{encoded}"

diagrams = {
    "code_flow.png": """graph TD
    A[Frontend Vue App] -->|Upload CSV| B(Go Backend Proxy :8080)
    B -->|Forward Request| C{Flask Python API :5000}
    C --> D[Parse CSV Data]
    D --> E[Feature Engineering]
    E --> F[Load ML Model joblib]
    F --> G[Predict Churn Probability]
    G --> H[Assign Risk Levels & Reasons]
    H --> I[Return JSON Response]
    I --> B
    B --> A
    A --> J[Display Dashboard]""",

    "user_flow.png": """graph TD
    U((User)) -->|Navigates to| A[Upload Page]
    A -->|Clicks Run Predictions| B[Uploads Customer Metrics CSV]
    B --> C{Wait for Analysis}
    C -->|Success| D[View Dashboard]
    D --> E[Analyze Churn Risks and Reasons]
    U -->|Later/End of period| A
    A -->|Clicks MLOps Feedback| F[Uploads Actual Outcomes CSV]
    F --> G[System Validates & Retrains Model]
    G --> H[Views Success Notification Snackbar]""",

    "overall_flow.png": """sequenceDiagram
    participant User
    participant Vue_Frontend as Vue Frontend
    participant Go_Proxy as Go Backend (Port 8080)
    participant Flask_Service as Python Flask (Port 5000)
    participant ML_Model as Model (Joblib)

    User->>Vue_Frontend: Uploads Predictions CSV
    Vue_Frontend->>Go_Proxy: POST /predict (multipart form)
    Go_Proxy->>Flask_Service: POST /predict (proxied)
    Flask_Service->>Flask_Service: create_features(df)
    Flask_Service->>ML_Model: model.predict_proba(X)
    ML_Model-->>Flask_Service: Probabilities
    Flask_Service->>Flask_Service: Calculate Risk_Level & Primary_Reason
    Flask_Service-->>Go_Proxy: JSON [Customer_ID, Risk, Reason]
    Go_Proxy-->>Vue_Frontend: JSON [Customer_ID, Risk, Reason]
    Vue_Frontend-->>User: Redirect to Dashboard

    User->>Vue_Frontend: Uploads Feedback CSV
    Vue_Frontend->>Go_Proxy: POST /feedback (multipart form)
    Go_Proxy->>Flask_Service: POST /feedback (proxied)
    Flask_Service->>ML_Model: Evaluate & Retrain Model
    ML_Model-->>Flask_Service: Retrain Status
    Flask_Service-->>Go_Proxy: JSON (matched, total, retrained)
    Go_Proxy-->>Vue_Frontend: JSON (matched, total, retrained)
    Vue_Frontend-->>User: Show Success Snackbar"""
}

for filename, text in diagrams.items():
    print(f"Generating {filename}...")
    url = generate_kroki_url('mermaid', text)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Error generating {filename}: {e}")
