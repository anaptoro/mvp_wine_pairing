# Wine Pairing Classification MVP

This project is a machine learning MVP that predicts the quality of a wine-food pairing using classical classification algorithms from Scikit-learn.

The application allows a user to select a wine and a meal combination in a web interface and receive a predicted class:
- Good
- Okay
- Bad

The project was developed to satisfy the requirements of an MVP involving:
- a classification problem
- model training and comparison
- model export
- a simple full stack application
- an automated PyTest performance check

---

## Problem

Choosing a wine that pairs well with a meal can be difficult for non-experts.  
This project builds a classification model that predicts the quality of a wine-food combination based on categorical features such as wine type, food category, cuisine, and food item.

---

## Dataset

The dataset used in this project is based on wine-food pairing information.

Main input features:
- `wine_type`
- `wine_category`
- `food_item`
- `food_category`
- `cuisine`

Target variable:
- `target_class`

Target classes:
- `Good`
- `Okay`
- `Bad`

Because the dataset contained repeated combinations with conflicting labels, a cleaning step was applied to reduce label noise by aggregating repeated feature combinations and assigning the majority label.

---

## Machine Learning Pipeline

The notebook includes the following steps:
- data loading
- preprocessing
- train/test split using holdout
- categorical encoding with `OneHotEncoder`
- model training with Scikit-learn pipelines
- hyperparameter tuning with `GridSearchCV`
- model comparison
- model evaluation
- model export

### Models compared
The following classical classification algorithms were trained and compared:
- K-Nearest Neighbors (KNN)
- Decision Tree
- Naive Bayes
- Support Vector Machine (SVM)

### Evaluation metrics
The main evaluation metrics used were:
- Accuracy
- Macro F1-score
- Weighted F1-score
- Classification report
- Confusion matrix

The final model was selected based on test performance, with special attention to macro F1 because of class imbalance.

---

## How to Run

### 1. Clone the repository

```bash
git clone <YOUR_REPO_URL>
cd wine_classification

### 2. Create a virtual env and install dependencies

python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt

### 3. Run the Flask application
python app.py

#then open your browser at
http://127.0.0.1:5000
