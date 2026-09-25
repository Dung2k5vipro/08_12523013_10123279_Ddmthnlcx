import json
from pathlib import Path

def create_eda_notebook(project_root: Path) -> Path:
    eda_nb_path = project_root / "ai-models" / "colab" / "01_eda.ipynb"
    
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Exploratory Data Analysis (EDA)\n",
                "\n",
                "## 1. Mở Đầu\n",
                "\n",
                "- **Đề tài**: Dự đoán mức tiêu hao nhiên liệu của xe\n",
                "- **Loại bài toán**: Regression (Dự đoán giá trị thực định lượng)\n",
                "- **Target**: Fuel Consumption Comb (L/100 km)\n",
                "- **Tên chuẩn nội bộ target**: `fuel_consumption_comb`\n",
                "- **Đơn vị**: L/100 km\n",
                "\n",
                "### Mục tiêu EDA\n",
                "1. Hiểu cấu trúc dữ liệu tổng quan (số dòng, số cột, kiểu dữ liệu).\n",
                "2. Phát hiện và đánh giá dữ liệu thiếu (missing values) cũng như dữ liệu trùng lặp (duplicates).\n",
                "3. Kiểm tra phân bố của biến mục tiêu `fuel_consumption_comb` và phát hiện outlier.\n",
                "4. Phân tích mối quan hệ tương quan giữa các đặc trưng (features) và biến mục tiêu.\n",
                "5. Nhận diện các biến gây ra rò rỉ dữ liệu (Data Leakage) để loại bỏ.\n",
                "6. Tổng hợp các quyết định xử lý để chuẩn bị cho notebook Preprocessing tiếp theo."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Load Dữ Liệu\n",
                "\n",
                "Xác định đường dẫn dữ liệu tương đối linh hoạt từ root dự án bằng `pathlib`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import os\n",
                "from pathlib import Path\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "\n",
                "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n",
                "plt.rcParams['figure.dpi'] = 150\n",
                "plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']\n",
                "\n",
                "current_dir = Path.cwd()\n",
                "project_root = current_dir.parent.parent if current_dir.name == 'colab' else current_dir\n",
                "raw_csv_path = project_root / 'ai-models' / 'data' / 'raw' / 'MY1995-2023-Fuel-Consumption-Ratings.csv'\n",
                "figures_dir = project_root / 'docs' / 'figures' / 'eda'\n",
                "figures_dir.mkdir(parents=True, exist_ok=True)\n",
                "\n",
                "print('Đường dẫn CSV dataset:', raw_csv_path)\n",
                "df_raw = pd.read_csv(raw_csv_path)\n",
                "print(f'Load dữ liệu thành công! Kích thước raw: {df_raw.shape}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Tổng Quan Dữ Liệu Raw\n",
                "\n",
                "Hiển thị thông tin thống kê tổng quan của dataset gốc."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print('=== KÍCH THƯỚC DATASET ===')\n",
                "print(f'Số dòng: {df_raw.shape[0]}, Số cột: {df_raw.shape[1]}')\n",
                "\n",
                "print('\\n=== 5 DÒNG ĐẦU TIÊN ===')\n",
                "display(df_raw.head())\n",
                "\n",
                "print('\\n=== 5 DÒNG CUỐI CÙNG ===')\n",
                "display(df_raw.tail())\n",
                "\n",
                "print('\\n=== THÔNG TIN KIỂU DỮ LIỆU ===')\n",
                "df_raw.info()\n",
                "\n",
                "print('\\n=== DANH SÁCH TẤT CẢ CÁC CỘT ===')\n",
                "print(df_raw.columns.tolist())\n",
                "\n",
                "print('\\n=== THỐNG KÊ CÁC CỘT SỐ (NUMERIC) ===')\n",
                "display(df_raw.describe())\n",
                "\n",
                "print('\\n=== THỐNG KÊ CÁC CỘT PHÂN LOẠI (CATEGORICAL) ===')\n",
                "display(df_raw.describe(include=['object', 'string']))"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Kiểm Tra Dữ Liệu Thiếu (Missing Values)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "missing_count = df_raw.isnull().sum()\n",
                "missing_percent = (missing_count / len(df_raw)) * 100\n",
                "\n",
                "missing_df = pd.DataFrame({\n",
                "    'column': missing_count.index,\n",
                "    'missing_count': missing_count.values,\n",
                "    'missing_percent': missing_percent.values\n",
                "}).sort_values(by='missing_count', ascending=False).reset_index(drop=True)\n",
                "\n",
                "display(missing_df)\n",
                "\n",
                "plt.figure(figsize=(10, 5), dpi=300)\n",
                "filtered_missing = missing_df[missing_df['missing_count'] > 0]\n",
                "if len(filtered_missing) > 0:\n",
                "    bars = sns.barplot(data=filtered_missing, x='missing_percent', y='column', hue='column', palette='Reds_r', legend=False)\n",
                "    plt.title('Tỷ lệ Missing Value (%) theo Cột', fontsize=13, fontweight='bold', pad=12)\n",
                "    plt.xlabel('Tỷ lệ Missing (%)', fontsize=11)\n",
                "    for i, v in enumerate(filtered_missing['missing_percent']):\n",
                "        bars.text(v + 0.5, i, f'{v:.1f}% ({filtered_missing[\"missing_count\"].iloc[i]} dòng)', va='center', fontsize=10)\n",
                "else:\n",
                "    plt.text(0.5, 0.5, 'Dataset không phát hiện missing value ở các feature chính', ha='center', va='center', fontsize=14)\n",
                "plt.tight_layout()\n",
                "plt.savefig(figures_dir / 'missing_values.png')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Kiểm Tra Dữ Liệu Trùng Lặp (Duplicate Rows)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "dup_count = df_raw.duplicated().sum()\n",
                "print(f'Số lượng bản ghi trùng lặp (Duplicates): {dup_count}')\n",
                "if dup_count > 0:\n",
                "    display(df_raw[df_raw.duplicated(keep=False)])"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Phân Tích Biến Mục Tiêu (Target Analysis)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "target = df_raw['Comb_L100km']\n",
                "print('=== THỐNG KÊ MÔ TẢ BIẾN TARGET ===')\n",
                "print(f'Mean: {target.mean():.3f}, Median: {target.median():.3f}, Std: {target.std():.3f}')\n",
                "print(f'Min:  {target.min():.3f}, Max: {target.max():.3f}')\n",
                "\n",
                "plt.figure(figsize=(8, 5), dpi=300)\n",
                "sns.histplot(target, kde=True, color='#2b5c8f', bins=40, edgecolor='white')\n",
                "plt.title('Phân bố Target: Fuel Consumption Comb (L/100 km)', fontsize=13, fontweight='bold', pad=12)\n",
                "plt.axvline(target.mean(), color='#e74c3c', linestyle='--', linewidth=2, label=f'Mean: {target.mean():.2f}')\n",
                "plt.axvline(target.median(), color='#2ecc71', linestyle='-', linewidth=2, label=f'Median: {target.median():.2f}')\n",
                "plt.legend(fontsize=10)\n",
                "plt.tight_layout()\n",
                "plt.savefig(figures_dir / 'target_distribution.png')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Trực Quan Hóa Chi Tiết & Phân Tích Mối Quan Hệ"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Engine Size vs Target\n",
                "plt.figure(figsize=(8, 5), dpi=300)\n",
                "sns.scatterplot(data=df_raw, x='EngineSize_L', y='Comb_L100km', alpha=0.3, color='#2c3e50', s=20)\n",
                "sns.regplot(data=df_raw, x='EngineSize_L', y='Comb_L100km', scatter=False, color='#e74c3c', line_kws={'linewidth': 2})\n",
                "plt.title('Quan hệ giữa Dung tích động cơ (Engine Size) và Tiêu hao nhiên liệu', fontsize=13, fontweight='bold', pad=12)\n",
                "plt.tight_layout()\n",
                "plt.savefig(figures_dir / 'engine_size_vs_target.png')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 8. Kết Luận EDA & Quyết Định Preprocessing"
            ]
        }
    ]
    
    nb = {"cells": cells, "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    with open(eda_nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    return eda_nb_path


def create_preprocess_notebook(project_root: Path) -> Path:
    prep_nb_path = project_root / "ai-models" / "colab" / "02_preprocess.ipynb"
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# Data Preprocessing & Pipeline Construction\n", "\n", "## 1. Mục Tiêu Notebook\n", "- Preprocessing data & pipeline build."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "from pathlib import Path\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "\n",
                "current_dir = Path.cwd()\n",
                "project_root = current_dir.parent.parent if current_dir.name == 'colab' else current_dir\n",
                "ai_models_dir = project_root / 'ai-models'\n",
                "if str(ai_models_dir) not in sys.path:\n",
                "    sys.path.insert(0, str(ai_models_dir))\n",
                "\n",
                "from src.preprocess import load_data, rename_columns, clean_data, select_features, split_data, build_preprocessor\n",
                "\n",
                "df_raw = load_data()\n",
                "df_clean = clean_data(rename_columns(df_raw))\n",
                "X, y = select_features(df_clean)\n",
                "X_train, X_test, y_train, y_test = split_data(X, y, test_size=0.2, random_state=42)\n",
                "preprocessor = build_preprocessor()\n",
                "preprocessor.fit(X_train)\n",
                "X_train_trans = preprocessor.transform(X_train)\n",
                "X_test_trans = preprocessor.transform(X_test)\n",
                "print('Preprocessed successfully! X_train shape:', X_train_trans.shape, 'X_test shape:', X_test_trans.shape)"
            ]
        }
    ]
    nb = {"cells": cells, "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    with open(prep_nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    return prep_nb_path


def create_train_notebook(project_root: Path) -> Path:
    train_nb_path = project_root / "ai-models" / "colab" / "03_train.ipynb"
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Training Models\n",
                "\n",
                "## 1. Load dữ liệu & Preprocessing\n",
                "## 2. Train/Test Split (80/20, random_state=42)\n",
                "## 3. Baseline Model (DummyRegressor mean)\n",
                "## 4. Linear Regression\n",
                "## 5. Decision Tree Regressor (GridSearchCV)\n",
                "## 6. KNN Regressor (GridSearchCV)\n",
                "## 7. Support Vector Regression - SVR (GridSearchCV)\n",
                "## 8. Hyperparameter Tuning & Cross Validation"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "from pathlib import Path\n",
                "\n",
                "current_dir = Path.cwd()\n",
                "project_root = current_dir.parent.parent if current_dir.name == 'colab' else current_dir\n",
                "ai_models_dir = project_root / 'ai-models'\n",
                "if str(ai_models_dir) not in sys.path:\n",
                "    sys.path.insert(0, str(ai_models_dir))\n",
                "\n",
                "from src.train import train_all_models\n",
                "\n",
                "trained_pipelines, training_info, (X_train, X_test, y_train, y_test) = train_all_models()\n",
                "print('Training all 4 models completed successfully!')"
            ]
        }
    ]
    nb = {"cells": cells, "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    with open(train_nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    return train_nb_path


def create_evaluate_notebook(project_root: Path) -> Path:
    eval_nb_path = project_root / "ai-models" / "colab" / "04_evaluate.ipynb"
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Model Evaluation & Selection\n",
                "\n",
                "## 1. Load Best Estimator của từng Model từ Candidates\n",
                "## 2. Dự đoán trên Test Set & Tính Metrics (MAE, MSE, RMSE, R²)\n",
                "## 3. Trực quan hóa & So sánh Performance (model_comparison.png, actual_vs_predicted.png, residual_plot.png)\n",
                "## 4. Phân tích Residual & Overfitting / Underfitting\n",
                "## 5. Chọn Model cuối cùng & Export model.joblib + metadata.json"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "from pathlib import Path\n",
                "\n",
                "current_dir = Path.cwd()\n",
                "project_root = current_dir.parent.parent if current_dir.name == 'colab' else current_dir\n",
                "ai_models_dir = project_root / 'ai-models'\n",
                "if str(ai_models_dir) not in sys.path:\n",
                "    sys.path.insert(0, str(ai_models_dir))\n",
                "\n",
                "from src.evaluate import evaluate_and_export_best_model\n",
                "\n",
                "best_name, eval_results = evaluate_and_export_best_model()\n",
                "print(f'Evaluation finished successfully! Best model selected: {best_name}')"
            ]
        }
    ]
    nb = {"cells": cells, "metadata": {"language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    with open(eval_nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    return eval_nb_path


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    create_eda_notebook(root)
    create_preprocess_notebook(root)
    create_train_notebook(root)
    create_evaluate_notebook(root)
