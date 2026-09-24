import sys
import os
import time
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure ai-models directory is in sys.path
ai_models_root = Path(__file__).resolve().parent.parent
if str(ai_models_root) not in sys.path:
    sys.path.insert(0, str(ai_models_root))

from src.preprocess import load_data, rename_columns, clean_data, select_features, split_data, CANONICAL_FEATURES, TARGET_NAME
from src.utils import get_ai_models_root, ensure_dir, save_json

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]


def evaluate_model_pipeline(
    name: str,
    pipeline: Any,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    candidate_path: Path = None,
) -> Dict[str, Any]:
    """Evaluates a single model pipeline on Train and Test sets."""
    # Predict on Train
    y_train_pred = pipeline.predict(X_train)
    r2_train = r2_score(y_train, y_train_pred)

    # Predict on Test (measure inference time)
    t0 = time.time()
    y_test_pred = pipeline.predict(X_test)
    predict_time_sec = time.time() - t0

    # Calculate test metrics
    mae = mean_absolute_error(y_test, y_test_pred)
    mse = mean_squared_error(y_test, y_test_pred)
    rmse = np.sqrt(mse)
    r2_test = r2_score(y_test, y_test_pred)

    # File size
    file_size_kb = candidate_path.stat().st_size / 1024.0 if candidate_path and candidate_path.exists() else 0.0

    return {
        "key": name,
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "r2_test": float(r2_test),
        "r2_train": float(r2_train),
        "predict_time_sec": float(predict_time_sec),
        "file_size_kb": float(file_size_kb),
        "y_test_pred": y_test_pred,
    }


def generate_evaluation_figures(
    results: Dict[str, Dict[str, Any]],
    y_test: pd.Series,
    output_dir: Path,
) -> None:
    """Generates and saves model_comparison.png, actual_vs_predicted.png, and residual_plot.png."""
    ensure_dir(output_dir)

    model_names = [r["key"].replace("_", " ").title() for r in results.values()]
    maes = [r["mae"] for r in results.values()]
    rmses = [r["rmse"] for r in results.values()]
    r2s = [r["r2_test"] for r in results.values()]

    # 1. Model Comparison Chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)
    
    sns.barplot(x=model_names, y=maes, ax=axes[0], palette="Blues_d", hue=model_names, legend=False)
    axes[0].set_title("So sanh MAE (cang thap cang tot)", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("MAE (L/100 km)")
    for i, v in enumerate(maes):
        axes[0].text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=9)

    sns.barplot(x=model_names, y=rmses, ax=axes[1], palette="Oranges_d", hue=model_names, legend=False)
    axes[1].set_title("So sanh RMSE (cang thap cang tot)", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("RMSE (L/100 km)")
    for i, v in enumerate(rmses):
        axes[1].text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=9)

    sns.barplot(x=model_names, y=r2s, ax=axes[2], palette="Greens_d", hue=model_names, legend=False)
    axes[2].set_title("So sanh R² Score (cang cao cang tot)", fontsize=11, fontweight="bold")
    axes[2].set_ylabel("R² Score")
    for i, v in enumerate(r2s):
        axes[2].text(i, v + 0.005, f"{v:.4f}", ha="center", fontsize=9)

    plt.suptitle("DANH GIA VA SO SANH PERFORMANCE CAC MODEL", fontsize=13, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / "model_comparison.png", bbox_inches="tight")
    plt.close()

    # 2. Actual vs Predicted Plot
    plt.figure(figsize=(10, 8), dpi=300)
    colors = ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6"]
    for i, (key, res) in enumerate(results.items()):
        plt.scatter(
            y_test,
            res["y_test_pred"],
            alpha=0.25,
            s=15,
            color=colors[i % len(colors)],
            label=f"{key.replace('_', ' ').title()} (R²={res['r2_test']:.4f})",
        )
    
    min_val = min(y_test.min(), min(r["y_test_pred"].min() for r in results.values()))
    max_val = max(y_test.max(), max(r["y_test_pred"].max() for r in results.values()))
    plt.plot([min_val, max_val], [min_val, max_val], "k--", linewidth=2, label="Duong ly tuong (y = x)")

    plt.title("Biue do Actual vs Predicted cua tat ca cac Model", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Gia tri Thuc te Actual (L/100 km)", fontsize=11)
    plt.ylabel("Gia tri Du doan Predicted (L/100 km)", fontsize=11)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir / "actual_vs_predicted.png", bbox_inches="tight")
    plt.close()

    # 3. Residual Plot
    plt.figure(figsize=(10, 8), dpi=300)
    for i, (key, res) in enumerate(results.items()):
        residuals = y_test - res["y_test_pred"]
        plt.scatter(
            res["y_test_pred"],
            residuals,
            alpha=0.25,
            s=15,
            color=colors[i % len(colors)],
            label=f"{key.replace('_', ' ').title()} (MAE={res['mae']:.3f})",
        )
    
    plt.axhline(0, color="black", linestyle="--", linewidth=2)
    plt.title("Biue do Residuals (y_true - y_pred) theo Gia tri Du doan", fontsize=13, fontweight="bold", pad=12)
    plt.xlabel("Gia tri Du doan Predicted (L/100 km)", fontsize=11)
    plt.ylabel("Phan du Residual (L/100 km)", fontsize=11)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_dir / "residual_plot.png", bbox_inches="tight")
    plt.close()

    print(f"Generated all evaluation figures in: {output_dir}")


def evaluate_and_export_best_model() -> Tuple[str, Dict[str, Any]]:
    """Evaluates candidates, selects best model, exports model.joblib & metadata.json."""
    print("=== BAT DAU DANH GIA VÀ EXPORT MODEL CUOI ===")
    
    # Load dataset & split
    df_raw = load_data()
    df_clean = clean_data(rename_columns(df_raw))
    X, y = select_features(df_clean)
    X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)

    candidates_dir = get_ai_models_root() / "models" / "candidates"
    models_dir = get_ai_models_root() / "models"
    versions_dir = ensure_dir(models_dir / "versions")
    fig_dir = get_ai_models_root().parent / "docs" / "figures" / "evaluation"

    candidate_files = {
        "linear_regression": candidates_dir / "linear_regression.joblib",
        "decision_tree": candidates_dir / "decision_tree.joblib",
        "knn": candidates_dir / "knn.joblib",
        "svr": candidates_dir / "svr.joblib",
    }

    eval_results = {}
    for name, path in candidate_files.items():
        if not path.exists():
            raise FileNotFoundError(f"Candidate model file missing: {path}")
        pipe = joblib.load(path)
        eval_results[name] = evaluate_model_pipeline(name, pipe, X_train, X_test, y_train, y_test, path)
        print(f"Model {name.upper()}: MAE={eval_results[name]['mae']:.4f}, RMSE={eval_results[name]['rmse']:.4f}, R2={eval_results[name]['r2_test']:.4f}")

    # Generate Figures
    generate_evaluation_figures(eval_results, y_test, fig_dir)

    # Select Best Model based on Lowest MAE / RMSE and Highest R2
    best_name = min(eval_results, key=lambda k: eval_results[k]["mae"])
    best_info = eval_results[best_name]
    best_pipeline = joblib.load(candidate_files[best_name])

    print(f"\n=== MODEL TOT NHAT DUOC CHON: {best_name.upper()} ===")
    print(f"   MAE:  {best_info['mae']:.4f} L/100 km")
    print(f"   RMSE: {best_info['rmse']:.4f} L/100 km")
    print(f"   R2:   {best_info['r2_test']:.4f}")

    # Export Production model.joblib
    prod_model_path = models_dir / "model.joblib"
    version_model_path = versions_dir / "model_v1.0.0.joblib"
    
    joblib.dump(best_pipeline, prod_model_path)
    joblib.dump(best_pipeline, version_model_path)

    # Export metadata.json
    import sklearn
    metadata = {
        "model_name": best_name,
        "model_version": "1.0.0",
        "problem_type": "regression",
        "target": TARGET_NAME,
        "target_unit": "L/100 km",
        "features": CANONICAL_FEATURES,
        "metrics": {
            "mae": round(best_info["mae"], 4),
            "mse": round(best_info["mse"], 4),
            "rmse": round(best_info["rmse"], 4),
            "r2": round(best_info["r2_test"], 4),
            "r2_train": round(best_info["r2_train"], 4),
        },
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "library_versions": {
            "python": sys.version.split()[0],
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
    }
    save_json(metadata, models_dir / "metadata.json")

    print(f"Saved production model to: {prod_model_path}")
    print(f"Saved versioned model to:  {version_model_path}")
    print(f"Saved metadata to:         {models_dir / 'metadata.json'}")

    return best_name, eval_results


if __name__ == "__main__":
    evaluate_and_export_best_model()
