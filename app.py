from flask import Flask, render_template, request
import joblib
import pandas as pd


app = Flask(__name__)


# =========================
# LOAD ARTIFACTS
# =========================
MODEL_PATH = "best_wine_pairing_model.pkl"
FEATURES_PATH = "selected_features.pkl"
OPTIONS_PATH = "feature_options.pkl"

model = joblib.load(MODEL_PATH)
selected_features = joblib.load(FEATURES_PATH)
feature_options = joblib.load(OPTIONS_PATH)


# =========================
# HELPERS
# =========================
def build_input_dataframe(form_data: dict) -> pd.DataFrame:
    row = {feature: form_data.get(feature, "") for feature in selected_features}
    return pd.DataFrame([row])[selected_features]


def extract_prediction_label(prediction) -> str:
    try:
        if hasattr(prediction, "__len__"):
            return str(prediction[0])
        return str(prediction)
    except Exception:
        return str(prediction)


def suggest_better_pairings(submitted_values: dict, top_k: int = 3):
    """
    If the user's pairing is predicted as Bad, try alternative wine options
    while keeping the food side fixed.
    """
    fixed_values = {
        "food_item": submitted_values.get("food_item", ""),
        "food_category": submitted_values.get("food_category", ""),
    }

    candidate_rows = []

    for wine_type in feature_options.get("wine_type", []):
        for wine_category in feature_options.get("wine_category", []):
            row = {
                "wine_type": wine_type,
                "wine_category": wine_category,
                "food_item": fixed_values["food_item"],
                "food_category": fixed_values["food_category"],
            }
            candidate_rows.append(row)

    if not candidate_rows:
        return []

    candidates_df = pd.DataFrame(candidate_rows)[selected_features]

    preds = model.predict(candidates_df)

    # normalize prediction output
    pred_labels = []
    for p in preds:
        try:
            if hasattr(p, "__len__") and not isinstance(p, str):
                pred_labels.append(str(p[0]))
            else:
                pred_labels.append(str(p))
        except Exception:
            pred_labels.append(str(p))

    candidates_df = candidates_df.copy()
    candidates_df["predicted_label"] = pred_labels

    # keep only alternatives predicted as Good, then Okay
    good_df = candidates_df[candidates_df["predicted_label"] == "Good"].copy()
    okay_df = candidates_df[candidates_df["predicted_label"] == "Okay"].copy()

    # remove the exact original pairing from suggestions
    good_df = good_df[
        ~(
            (good_df["wine_type"] == submitted_values.get("wine_type", "")) &
            (good_df["wine_category"] == submitted_values.get("wine_category", ""))
        )
    ]

    okay_df = okay_df[
        ~(
            (okay_df["wine_type"] == submitted_values.get("wine_type", "")) &
            (okay_df["wine_category"] == submitted_values.get("wine_category", ""))
        )
    ]

    suggestions = []

    for _, row in good_df.head(top_k).iterrows():
        suggestions.append({
            "wine_type": row["wine_type"],
            "wine_category": row["wine_category"],
            "predicted_label": row["predicted_label"],
        })

    if len(suggestions) < top_k:
        for _, row in okay_df.head(top_k - len(suggestions)).iterrows():
            suggestions.append({
                "wine_type": row["wine_type"],
                "wine_category": row["wine_category"],
                "predicted_label": row["predicted_label"],
            })

    return suggestions


# =========================
# SINGLE PAGE ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    suggestions = []
    submitted_values = {feature: "" for feature in selected_features}

    if request.method == "POST":
        submitted_values = {
            feature: request.form.get(feature, "")
            for feature in selected_features
        }

        input_df = build_input_dataframe(submitted_values)
        raw_prediction = model.predict(input_df)
        prediction = extract_prediction_label(raw_prediction)

        if prediction == "Bad":
            suggestions = suggest_better_pairings(submitted_values, top_k=3)

    return render_template(
        "index.html",
        feature_options=feature_options,
        selected_features=selected_features,
        prediction=prediction,
        suggestions=suggestions,
        submitted_values=submitted_values,
    )


if __name__ == "__main__":
    app.run(debug=True)