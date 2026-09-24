import sys
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, Header, status
from fastapi.responses import JSONResponse
import pandas as pd

# Ensure service and ai-models directory are in sys.path
service_dir = Path(__file__).resolve().parent
ai_models_dir = service_dir.parent
if str(service_dir) not in sys.path:
    sys.path.insert(0, str(service_dir))
if str(ai_models_dir) not in sys.path:
    sys.path.insert(0, str(ai_models_dir))

from service.config import settings
from service.model_loader import container
from service.schemas import PredictRequest, PredictResponse, HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ai-service")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load ML model ONCE at startup."""
    logger.info("[AI-SERVICE] Initializing application startup...")
    container.load_artifacts()
    yield
    logger.info("[AI-SERVICE] Application shutdown.")


app = FastAPI(
    title="Vehicle Fuel Consumption AI Service",
    description="FastAPI Microservice for Vehicle Fuel Consumption Regression Prediction",
    version="1.0.0",
    lifespan=lifespan,
)


def validate_against_schema(features: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Validates input features against schema.json validation rules."""
    cleaned = {}
    feature_schemas = schema.get("features", {})

    for key, rule in feature_schemas.items():
        if key not in features or features[key] is None:
            return {}, f"Thiếu trường bắt buộc: '{key}'"
        
        val = features[key]
        ftype = rule.get("type")

        # Type conversion & normalization
        if ftype == "category":
            val_str = str(val).strip().upper()
            allowed_vals = rule.get("values", [])
            if allowed_vals and val_str not in allowed_vals:
                return {}, f"Giá trị không hợp lệ cho '{key}': '{val}'. Các giá trị hợp lệ: {allowed_vals[:5]}... (tổng {len(allowed_vals)})"
            cleaned[key] = val_str

        elif ftype == "integer":
            try:
                val_int = int(val)
            except (ValueError, TypeError):
                return {}, f"Trường '{key}' phải là số nguyên (integer)."
            
            allowed_vals = rule.get("values")
            if allowed_vals and val_int not in allowed_vals:
                return {}, f"Giá trị '{key}'={val_int} không thuộc danh sách hợp lệ: {allowed_vals}"
            
            min_val = rule.get("min")
            max_val = rule.get("max")
            if min_val is not None and val_int < min_val:
                return {}, f"Giá trị '{key}'={val_int} nhỏ hơn ngưỡng min={min_val}"
            if max_val is not None and val_int > max_val:
                return {}, f"Giá trị '{key}'={val_int} lớn hơn ngưỡng max={max_val}"
            cleaned[key] = val_int

        elif ftype == "number":
            try:
                val_float = float(val)
            except (ValueError, TypeError):
                return {}, f"Trường '{key}' phải là số (number)."
            
            min_val = rule.get("min")
            max_val = rule.get("max")
            if min_val is not None and val_float < min_val:
                return {}, f"Giá trị '{key}'={val_float} nhỏ hơn ngưỡng min={min_val}"
            if max_val is not None and val_float > max_val:
                return {}, f"Giá trị '{key}'={val_float} lớn hơn ngưỡng max={max_val}"
            cleaned[key] = val_float

    return cleaned, ""


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint to verify service and model status."""
    if not container.is_loaded:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "model_loaded": False,
                "model_version": "unknown",
                "detail": container.error_message or "Model not loaded",
            },
        )
    
    version = container.metadata.get("model_version", "1.0.0") if container.metadata else "1.0.0"
    return HealthResponse(
        status="ok",
        model_loaded=True,
        model_version=version,
    )


@app.get("/model-info")
def get_model_info():
    """Returns metadata details of the loaded production ML model."""
    if not container.is_loaded or not container.metadata:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model metadata is not ready or failed to load.",
        )
    return container.metadata


@app.post("/predict", response_model=PredictResponse)
def predict_fuel_consumption(
    request: PredictRequest,
    x_request_id: Optional[str] = Header(default=None, alias="X-Request-ID"),
):
    """Predicts Vehicle Fuel Consumption (L/100 km) for standard input features."""
    if not container.is_loaded or container.model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Service chưa sẵn sàng: Model chưa được load.",
        )

    request_id = x_request_id if x_request_id else str(uuid.uuid4())
    t0 = time.time()

    # Validate against schema
    feat_dict = request.features.model_dump()
    cleaned_features, error_msg = validate_against_schema(feat_dict, container.schema)
    if error_msg:
        logger.warning(f"req={request_id} validation_error='{error_msg}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )

    try:
        # Convert to 1-row DataFrame
        df_input = pd.DataFrame([cleaned_features])
        
        # Predict
        pred_val = float(container.model.predict(df_input)[0])
        pred_val_rounded = round(pred_val, 2)
        
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        version = container.metadata.get("model_version", "1.0.0") if container.metadata else "1.0.0"

        logger.info(f"req={request_id} prediction={pred_val_rounded} unit='L/100 km' version={version} time={elapsed_ms}ms")

        return PredictResponse(
            prediction=pred_val_rounded,
            unit="L/100 km",
            model_version=version,
            request_id=request_id,
        )
    except Exception as e:
        logger.error(f"req={request_id} prediction_error='{e}'")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống khi dự đoán: {str(e)}",
        )
