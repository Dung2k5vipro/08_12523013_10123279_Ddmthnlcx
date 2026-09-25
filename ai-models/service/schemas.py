from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PredictInputFeatures(BaseModel):
    """Canonical 7 input features for Vehicle Fuel Consumption Prediction."""
    
    model_year: int = Field(..., description="Năm sản xuất xe (1995 - 2023)")
    make: str = Field(..., description="Hãng sản xuất xe (VD: TOYOTA, HONDA, FORD)")
    vehicle_class: str = Field(..., description="Phân loại xe (VD: COMPACT, SUV - SMALL)")
    engine_size: float = Field(..., description="Dung tích động cơ tính bằng lit (VD: 2.5)")
    cylinders: int = Field(..., description="Số xy-lanh (VD: 4, 6, 8)")
    transmission: str = Field(..., description="Mã hộp số (VD: AS6, M5, A6)")
    fuel_type: str = Field(..., description="Mã loại nhiên liệu (X, Z, D, E, N)")


class PredictRequest(BaseModel):
    """Request payload containing nested features object."""
    
    features: PredictInputFeatures


class PredictResponse(BaseModel):
    """Prediction response payload."""
    
    prediction: float = Field(..., description="Dự đoán mức tiêu thụ nhiên liệu (L/100 km)")
    unit: str = Field(default="L/100 km", description="Đơn vị đo lường")
    model_version: str = Field(default="1.0.0", description="Phiên bản mô hình AI")
    request_id: str = Field(..., description="Mã vết Request ID duy nhất")


class HealthResponse(BaseModel):
    """Health status response payload."""
    
    status: str
    model_loaded: bool
    model_version: str
