import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib

# Fix Windows console UTF-8 output encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure ai-models directory is in sys.path
ai_models_root = Path(__file__).resolve().parent.parent
if str(ai_models_root) not in sys.path:
    sys.path.insert(0, str(ai_models_root))

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.dummy import DummyRegressor
from sklearn.model_selection import GridSearchCV, KFold

from src.preprocess import (
    load_data,
    rename_columns,
    clean_data,
    select_features,
    split_data,
    build_preprocessor,
)
from src.utils import get_ai_models_root, ensure_dir


def train_all_models(
    random_state: int = 42,
    cv_splits: int = 5,
    n_jobs: int = 2,
) -> Tuple[Dict[str, Pipeline], Dict[str, Dict[str, Any]], Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]]:
    """
    Trains baseline and 4 primary ML regression models (Linear Regression, Decision Tree, KNN, SVR)
    using sklearn Pipelines and Cross Validation / Hyperparameter Tuning on train set only.
    Exports candidates to ai-models/models/candidates/.
    """
    print("=== BAT DAU QUY TRINH HUAN LUYEN MODEL ===", flush=True)
    
    # 1. Load & Preprocess Data
    print("1. Loading raw dataset...", flush=True)
    df_raw = load_data()
    df_renamed = rename_columns(df_raw)
    df_clean = clean_data(df_renamed)
    X, y = select_features(df_clean)
    
    # 2. Train/Test Split (80/20, random_state=42)
    print("2. Phan chia Train/Test set (80/20)...", flush=True)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=random_state)
    print(f"   X_train shape: {X_train.shape}, X_test shape: {X_test.shape}", flush=True)
    
    # 3. Build Preprocessor
    preprocessor = build_preprocessor()
    cv = KFold(n_splits=cv_splits, shuffle=True, random_state=random_state)
    
    candidates_dir = ensure_dir(get_ai_models_root() / "models" / "candidates")
    trained_pipelines: Dict[str, Pipeline] = {}
    training_info: Dict[str, Dict[str, Any]] = {}

    # -------------------------------------------------------------
    # 0. Baseline Model (DummyRegressor)
    # -------------------------------------------------------------
    print("\n3. Training Baseline Model (DummyRegressor mean)...", flush=True)
    pipe_baseline = Pipeline([("preprocessor", preprocessor), ("model", DummyRegressor(strategy="mean"))])
    t0 = time.time()
    pipe_baseline.fit(X_train, y_train)
    t_fit = time.time() - t0
    trained_pipelines["baseline"] = pipe_baseline
    training_info["baseline"] = {
        "name": "Dummy Regressor (Mean Baseline)",
        "fit_time_sec": t_fit,
        "best_params": {"strategy": "mean"},
        "cv_score_mean": float("nan"),
        "cv_score_std": float("nan"),
    }

    # -------------------------------------------------------------
    # 1. Linear Regression
    # -------------------------------------------------------------
    print("\n4. Training Model 1/4: Linear Regression...", flush=True)
    pipe_lr = Pipeline([("preprocessor", preprocessor), ("model", LinearRegression())])
    t0 = time.time()
    pipe_lr.fit(X_train, y_train)
    t_fit = time.time() - t0
    
    joblib.dump(pipe_lr, candidates_dir / "linear_regression.joblib")
    trained_pipelines["linear_regression"] = pipe_lr
    training_info["linear_regression"] = {
        "name": "Linear Regression",
        "fit_time_sec": t_fit,
        "best_params": {"fit_intercept": True},
        "cv_score_mean": float("nan"),
        "cv_score_std": float("nan"),
    }
    print(f"   Linear Regression completed in {t_fit:.2f}s", flush=True)

    # -------------------------------------------------------------
    # 2. Decision Tree Regressor
    # -------------------------------------------------------------
    print("\n5. Training Model 2/4: Decision Tree Regressor (GridSearchCV)...", flush=True)
    pipe_dt = Pipeline([("preprocessor", preprocessor), ("model", DecisionTreeRegressor(random_state=random_state))])
    dt_grid = {
        "model__max_depth": [5, 10, 15, 20],
        "model__min_samples_split": [2, 5, 10],
        "model__min_samples_leaf": [1, 2, 4],
    }
    gs_dt = GridSearchCV(pipe_dt, dt_grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=n_jobs)
    t0 = time.time()
    gs_dt.fit(X_train, y_train)
    t_fit = time.time() - t0
    
    best_dt = gs_dt.best_estimator_
    joblib.dump(best_dt, candidates_dir / "decision_tree.joblib")
    trained_pipelines["decision_tree"] = best_dt
    training_info["decision_tree"] = {
        "name": "Decision Tree Regressor",
        "fit_time_sec": t_fit,
        "best_params": gs_dt.best_params_,
        "cv_score_mean": -float(gs_dt.best_score_),
        "cv_score_std": float(gs_dt.cv_results_["std_test_score"][gs_dt.best_index_]),
    }
    print(f"   Decision Tree completed in {t_fit:.2f}s. Best MAE CV: {-gs_dt.best_score_:.4f}", flush=True)

    # -------------------------------------------------------------
    # 3. KNN Regressor
    # -------------------------------------------------------------
    print("\n6. Training Model 3/4: K-Nearest Neighbors Regressor (GridSearchCV)...", flush=True)
    pipe_knn = Pipeline([("preprocessor", preprocessor), ("model", KNeighborsRegressor())])
    knn_grid = {
        "model__n_neighbors": [3, 5, 7, 9],
        "model__weights": ["uniform", "distance"],
        "model__p": [1, 2],
    }
    gs_knn = GridSearchCV(pipe_knn, knn_grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=n_jobs)
    t0 = time.time()
    gs_knn.fit(X_train, y_train)
    t_fit = time.time() - t0
    
    best_knn = gs_knn.best_estimator_
    joblib.dump(best_knn, candidates_dir / "knn.joblib")
    trained_pipelines["knn"] = best_knn
    training_info["knn"] = {
        "name": "K-Nearest Neighbors Regressor",
        "fit_time_sec": t_fit,
        "best_params": gs_knn.best_params_,
        "cv_score_mean": -float(gs_knn.best_score_),
        "cv_score_std": float(gs_knn.cv_results_["std_test_score"][gs_knn.best_index_]),
    }
    print(f"   KNN completed in {t_fit:.2f}s. Best MAE CV: {-gs_knn.best_score_:.4f}", flush=True)

    # -------------------------------------------------------------
    # 4. SVR (Support Vector Regression)
    # -------------------------------------------------------------
    print("\n7. Training Model 4/4: Support Vector Regression - SVR (GridSearchCV)...", flush=True)
    pipe_svr = Pipeline([("preprocessor", preprocessor), ("model", SVR())])
    svr_grid = {
        "model__C": [1.0, 10.0],
        "model__epsilon": [0.1],
        "model__kernel": ["rbf"],
        "model__gamma": ["scale"],
    }
    gs_svr = GridSearchCV(pipe_svr, svr_grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=n_jobs)
    t0 = time.time()
    gs_svr.fit(X_train, y_train)
    t_fit = time.time() - t0
    
    best_svr = gs_svr.best_estimator_
    joblib.dump(best_svr, candidates_dir / "svr.joblib")
    trained_pipelines["svr"] = best_svr
    training_info["svr"] = {
        "name": "Support Vector Regression (SVR)",
        "fit_time_sec": t_fit,
        "best_params": gs_svr.best_params_,
        "cv_score_mean": -float(gs_svr.best_score_),
        "cv_score_std": float(gs_svr.cv_results_["std_test_score"][gs_svr.best_index_]),
    }
    print(f"   SVR completed in {t_fit:.2f}s. Best MAE CV: {-gs_svr.best_score_:.4f}", flush=True)

    print("\n=== HOAN THANH QUY TRINH HUAN LUYEN 4 MODEL ===", flush=True)
    return trained_pipelines, training_info, (X_train, X_test, y_train, y_test)


if __name__ == "__main__":
    train_all_models()
