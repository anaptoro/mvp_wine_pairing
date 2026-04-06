import joblib
import pandas as pd

from sklearn.metrics import accuracy_score, f1_score


MODEL_PATH = "best_wine_pairing_model.pkl"
X_TEST_PATH = "X_test.csv"
Y_TEST_PATH = "y_test.csv"

# Performance requirements you define
MIN_ACCURACY = 0.85
MIN_MACRO_F1 = 0.65


def test_model_performance():
    # Load model
    model = joblib.load(MODEL_PATH)

    # Load test data
    X_test = pd.read_csv(X_TEST_PATH)
    y_test = pd.read_csv(Y_TEST_PATH)["target_class"]

    # Predict
    y_pred = model.predict(X_test)

    # Compute metrics
    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    # Helpful output in pytest logs
    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")

    # Assertions
    assert accuracy >= MIN_ACCURACY, (
        f"Model accuracy below threshold: {accuracy:.4f} < {MIN_ACCURACY:.4f}"
    )
    assert macro_f1 >= MIN_MACRO_F1, (
        f"Model macro F1 below threshold: {macro_f1:.4f} < {MIN_MACRO_F1:.4f}"
    )