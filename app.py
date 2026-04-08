from flask import Flask, render_template, request
import joblib
import pandas as pd
from pathlib import Path


app = Flask(__name__)

# =========================
# LOAD ARTIFACTS
# =========================
APP_DIR = Path(__file__).resolve().parent

MODEL_PATH = APP_DIR / "best_wine_pairing_model.pkl"
FEATURES_PATH = APP_DIR / "selected_features.pkl"
OPTIONS_PATH = APP_DIR / "feature_options.pkl"

WINE_TYPES_BY_CATEGORY_PATH = APP_DIR / "wine_types_by_category.pkl"
WINE_CATEGORIES_BY_TYPE_PATH = APP_DIR / "wine_categories_by_type.pkl"
FOOD_ITEMS_BY_CATEGORY_PATH = APP_DIR / "food_items_by_category.pkl"

wine_types_by_category = joblib.load(WINE_TYPES_BY_CATEGORY_PATH)
wine_categories_by_type = joblib.load(WINE_CATEGORIES_BY_TYPE_PATH)
food_items_by_category = joblib.load(FOOD_ITEMS_BY_CATEGORY_PATH)

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
    Suggest better wine alternatives for the same meal.
    Only returns alternatives predicted as Good or Okay.
    """
    candidate_rows = []

    fixed_values = {
        "food_item": submitted_values.get("food_item", ""),
        "food_category": submitted_values.get("food_category", ""),
    }

    # build only valid wine pairs
    for wine_category, valid_types in wine_types_by_category.items():
        for wine_type in valid_types:
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
    probs = model.predict_proba(candidates_df)

    # normalize prediction labels
    pred_labels = []
    for p in preds:
        try:
            if hasattr(p, "__len__") and not isinstance(p, str):
                pred_labels.append(str(p[0]))
            else:
                pred_labels.append(str(p))
        except Exception:
            pred_labels.append(str(p))

    class_names = list(model.classes_)
    good_idx = class_names.index("Good") if "Good" in class_names else None
    okay_idx = class_names.index("Okay") if "Okay" in class_names else None
    bad_idx = class_names.index("Bad") if "Bad" in class_names else None

    candidates_df = candidates_df.copy()
    candidates_df["predicted_label"] = pred_labels
    candidates_df["prob_good"] = [row[good_idx] if good_idx is not None else 0.0 for row in probs]
    candidates_df["prob_okay"] = [row[okay_idx] if okay_idx is not None else 0.0 for row in probs]
    candidates_df["prob_bad"] = [row[bad_idx] if bad_idx is not None else 0.0 for row in probs]

    # remove the exact original pairing
    candidates_df = candidates_df[
        ~(
            (candidates_df["wine_type"] == submitted_values.get("wine_type", "")) &
            (candidates_df["wine_category"] == submitted_values.get("wine_category", ""))
        )
    ]

    # keep ONLY non-bad alternatives
    candidates_df = candidates_df[
        candidates_df["predicted_label"].isin(["Good", "Okay"])
    ].copy()

    if candidates_df.empty:
        return []

    ranked = candidates_df.sort_values(
        by=["predicted_label", "prob_good", "prob_okay"],
        ascending=[True, False, False],
    ).copy()

    # force Good before Okay
    ranked["label_priority"] = ranked["predicted_label"].map({"Good": 0, "Okay": 1})
    ranked = ranked.sort_values(
        by=["label_priority", "prob_good", "prob_okay"],
        ascending=[True, False, False],
    )

    suggestions = []
    for _, row in ranked.head(top_k).iterrows():
        suggestions.append({
            "wine_type": row["wine_type"],
            "wine_category": row["wine_category"],
            "predicted_label": row["predicted_label"],
            "prob_good": round(float(row["prob_good"]), 3),
            "prob_okay": round(float(row["prob_okay"]), 3),
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
    food_items_by_category=food_items_by_category,
    wine_types_by_category=wine_types_by_category,
    wine_categories_by_type=wine_categories_by_type,
)


if __name__ == "__main__":
    app.run(debug=True)