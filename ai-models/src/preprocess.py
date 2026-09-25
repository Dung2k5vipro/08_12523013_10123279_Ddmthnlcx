import os
from pathlib import Path
from typing import List, Tuple, Optional
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils import get_ai_models_root

# Default raw data path relative to ai-models root
DEFAULT_RAW_DATA_PATH = get_ai_models_root() / "data" / "raw" / "MY1995-2023-Fuel-Consumption-Ratings.csv"

# Explicit column mapping from raw Kaggle CSV to internal canonical field names
RAW_TO_CANONICAL_MAPPING = {
    "ModelYear": "model_year",
    "Make": "make",
    "VehicleClass": "vehicle_class",
    "EngineSize_L": "engine_size",
    "Cylinders": "cylinders",
    "Transmission": "transmission",
    "FuelType": "fuel_type",
    "Comb_L100km": "fuel_consumption_comb",
}

# Standard canonical feature set (7 input features)
CANONICAL_FEATURES = [
    "model_year",
    "make",
    "vehicle_class",
    "engine_size",
    "cylinders",
    "transmission",
    "fuel_type",
]

# Standard canonical target name
TARGET_NAME = "fuel_consumption_comb"

# Feature dtypes breakdown
NUMERIC_FEATURES = ["model_year", "engine_size", "cylinders"]
CATEGORICAL_FEATURES = ["make", "vehicle_class", "transmission", "fuel_type"]


def get_raw_data_path() -> Path:
    """Returns the default path to the raw dataset CSV file."""
    return DEFAULT_RAW_DATA_PATH


def load_data(file_path: Optional[Path] = None) -> pd.DataFrame:
    """Loads dataset from CSV file. Raises FileNotFoundError if file missing."""
    target_path = Path(file_path) if file_path else get_raw_data_path()
    if not target_path.exists():
        raise FileNotFoundError(f"Dataset CSV not found at: {target_path}")
    df = pd.read_csv(target_path)
    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames raw dataset columns to canonical internal field names."""
    df_renamed = df.copy()
    existing_mapping = {col: RAW_TO_CANONICAL_MAPPING[col] for col in df_renamed.columns if col in RAW_TO_CANONICAL_MAPPING}
    return df_renamed.rename(columns=existing_mapping)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans data by stripping whitespaces and converting categorical strings to uppercase
    (to unify case discrepancies across multi-year data), then dropping exact duplicates.
    """
    df_clean = df.copy()
    
    # Clean categorical text columns (strip spaces & convert to UPPERCASE)
    str_cols = df_clean.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()
    
    # Drop exact duplicate records
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    return df_clean


def select_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Extracts input features X (7 canonical features) and target y (fuel_consumption_comb)."""
    if TARGET_NAME not in df.columns:
        raise KeyError(f"Target column '{TARGET_NAME}' not found in DataFrame.")
    
    missing_features = [col for col in CANONICAL_FEATURES if col not in df.columns]
    if missing_features:
        raise KeyError(f"Missing required canonical features: {missing_features}")
    
    X = df[CANONICAL_FEATURES].copy()
    y = df[TARGET_NAME].copy()
    return X, y


def split_data(
    X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Splits dataset into training and testing sets."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def build_preprocessor(
    numeric_features: Optional[List[str]] = None,
    categorical_features: Optional[List[str]] = None,
) -> ColumnTransformer:
    """Constructs scikit-learn ColumnTransformer for preprocessing numeric and categorical features."""
    if numeric_features is None:
        numeric_features = NUMERIC_FEATURES
    if categorical_features is None:
        categorical_features = CATEGORICAL_FEATURES

    num_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", num_pipe, numeric_features),
            ("categorical", cat_pipe, categorical_features),
        ]
    )

    return preprocessor
