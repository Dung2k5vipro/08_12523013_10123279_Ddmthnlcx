"""
Vehicle Fuel Consumption API - Automated Test & Spam Load Tool
Author: AI & App Team
Usage:
    python scripts/test_api.py [--url http://localhost:8000] [--spam 50] [--concurrency 5]
"""

import argparse
import json
import random
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

SAMPLE_VEHICLES = [
    {
        "name": "Toyota Corolla (Eco Sedan)",
        "payload": {
            "model_year": 2022,
            "make": "TOYOTA",
            "vehicle_class": "COMPACT",
            "engine_size": 1.8,
            "cylinders": 4,
            "transmission": "AV",
            "fuel_type": "X"
        },
        "expected_range": (6.0, 8.0)
    },
    {
        "name": "Honda Accord (Mid-Size)",
        "payload": {
            "model_year": 2021,
            "make": "HONDA",
            "vehicle_class": "MID-SIZE",
            "engine_size": 2.0,
            "cylinders": 4,
            "transmission": "AS10",
            "fuel_type": "X"
        },
        "expected_range": (7.5, 9.0)
    },
    {
        "name": "Ford F-150 (Truck V8)",
        "payload": {
            "model_year": 2023,
            "make": "FORD",
            "vehicle_class": "PICKUP TRUCK - STANDARD",
            "engine_size": 5.0,
            "cylinders": 8,
            "transmission": "AS10",
            "fuel_type": "X"
        },
        "expected_range": (12.5, 15.0)
    },
    {
        "name": "Porsche 911 (Sports Car)",
        "payload": {
            "model_year": 2023,
            "make": "PORSCHE",
            "vehicle_class": "TWO-SEATER",
            "engine_size": 3.0,
            "cylinders": 6,
            "transmission": "AM8",
            "fuel_type": "Z"
        },
        "expected_range": (10.0, 12.5)
    },
    {
        "name": "Mazda CX-5 (SUV Small)",
        "payload": {
            "model_year": 2022,
            "make": "MAZDA",
            "vehicle_class": "SUV - SMALL",
            "engine_size": 2.5,
            "cylinders": 4,
            "transmission": "AS6",
            "fuel_type": "X"
        },
        "expected_range": (8.0, 10.0)
    }
]

INVALID_SAMPLE = {
    "name": "Invalid Engine Size (Expected 400)",
    "payload": {
        "model_year": 2022,
        "make": "TOYOTA",
        "vehicle_class": "COMPACT",
        "engine_size": 25.0,  # Invalid: max 8.4
        "cylinders": 4,
        "transmission": "AS6",
        "fuel_type": "X"
    }
}


def send_request(url: str, method: str = "GET", body: dict = None, request_id: str = None, timeout: float = 10.0):
    start = time.perf_counter()
    headers = {"Content-Type": "application/json"}
    if request_id:
        headers["X-Request-ID"] = request_id

    data_bytes = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            elapsed_ms = (time.perf_counter() - start) * 1000
            res_body = res.read().decode("utf-8")
            return {
                "status_code": res.status,
                "latency_ms": round(elapsed_ms, 2),
                "data": json.loads(res_body) if res_body else {},
                "error": None
            }
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        res_body = e.read().decode("utf-8")
        try:
            parsed = json.loads(res_body)
        except Exception:
            parsed = {"raw": res_body}
        return {
            "status_code": e.code,
            "latency_ms": round(elapsed_ms, 2),
            "data": parsed,
            "error": f"HTTP {e.code}"
        }
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "status_code": 0,
            "latency_ms": round(elapsed_ms, 2),
            "data": {},
            "error": str(e)
        }


def run_health_check(base_url: str):
    print("=" * 60)
    print("🔍 [STEP 1] KIỂM TRA SỨC KHỎE HỆ THỐNG (/api/health)")
    print("=" * 60)
    health_url = f"{base_url.rstrip('/')}/api/health"
    res = send_request(health_url, method="GET")
    
    if res["status_code"] == 200:
        print(f"✅ Hệ thống sẵn sàng! (Latency: {res['latency_ms']} ms)")
        print(json.dumps(res["data"], indent=2, ensure_ascii=False))
        return True
    else:
        print(f"❌ Kiểm tra sức khỏe THẤT BẠI! Code: {res['status_code']} - Error: {res['error']}")
        print(f"Chi tiết: {res['data']}")
        return False


def run_unit_tests(base_url: str):
    print("\n" + "=" * 60)
    print("🧪 [STEP 2] KIỂM THỬ TỪNG TEST CASE CHUẨN")
    print("=" * 60)
    predict_url = f"{base_url.rstrip('/')}/api/predict"

    all_passed = True
    for i, test in enumerate(SAMPLE_VEHICLES, 1):
        req_id = f"test-case-{i:03d}"
        res = send_request(predict_url, method="POST", body=test["payload"], request_id=req_id)

        if res["status_code"] == 200:
            pred = res["data"].get("prediction")
            unit = res["data"].get("unit", "L/100 km")
            exp_min, exp_max = test["expected_range"]
            in_range = exp_min <= pred <= exp_max
            status_icon = "✅ PASS" if in_range else "⚠️ OUT_OF_RANGE"
            print(f"[{status_icon}] TC-{i:02d}: {test['name']:<30} => Dự đoán: {pred:>5.2f} {unit} (Kỳ vọng: {exp_min}-{exp_max}) | Latency: {res['latency_ms']}ms | ReqID: {req_id}")
            if not in_range:
                all_passed = False
        else:
            print(f"[❌ FAIL] TC-{i:02d}: {test['name']:<30} => Error {res['status_code']}: {res['data']}")
            all_passed = False

    # Test Validation Error
    print("\nKiểm tra bẫy lỗi Validation (Dữ liệu không hợp lệ):")
    res_err = send_request(predict_url, method="POST", body=INVALID_SAMPLE["payload"], request_id="test-err-001")
    if res_err["status_code"] in [400, 422]:
        print(f"✅ PASS: Hệ thống bắt lỗi chính xác ({res_err['status_code']}): {res_err['data'].get('error', {}).get('message')}")
    else:
        print(f"❌ FAIL: Mong đợi lỗi 400/422 nhưng nhận về: {res_err['status_code']}")

    return all_passed


def run_spam_test(base_url: str, total_requests: int = 50, concurrency: int = 5):
    print("\n" + "=" * 60)
    print(f"🚀 [STEP 3] SPAM / LOAD TEST: {total_requests} REQUESTS (ĐỒNG THỜI: {concurrency})")
    print("=" * 60)
    predict_url = f"{base_url.rstrip('/')}/api/predict"

    results = []
    start_total = time.perf_counter()

    def worker(idx):
        sample = random.choice(SAMPLE_VEHICLES)
        req_id = f"spam-req-{idx:04d}"
        res = send_request(predict_url, method="POST", body=sample["payload"], request_id=req_id)
        return idx, res

    print(f"Đang gửi liên tục {total_requests} requests tới {predict_url}...")
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker, i) for i in range(1, total_requests + 1)]
        for future in as_completed(futures):
            idx, res = future.result()
            results.append(res)
            code = res["status_code"]
            lat = res["latency_ms"]
            icon = "🟢" if code == 200 else "🔴"
            print(f"  {icon} Req #{idx:03d} -> Status: {code} | Latency: {lat:>6.2f} ms")

    total_time = time.perf_counter() - start_total
    success_count = sum(1 for r in results if r["status_code"] == 200)
    fail_count = len(results) - success_count
    latencies = [r["latency_ms"] for r in results if r["status_code"] == 200]

    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    min_lat = min(latencies) if latencies else 0
    max_lat = max(latencies) if latencies else 0
    rps = total_requests / total_time if total_time > 0 else 0

    print("\n" + "-" * 60)
    print("📊 BÁO CÁO KẾT QUẢ SPAM / LOAD TEST:")
    print("-" * 60)
    print(f"• Tổng số requests        : {total_requests}")
    print(f"• Thành công (200 OK)     : {success_count} ({success_count/total_requests*100:.1f}%)")
    print(f"• Thất bại / Lỗi          : {fail_count}")
    print(f"• Tổng thời gian thực thi : {total_time:.2f} giây")
    print(f"• Tốc độ xử lý (RPS)      : {rps:.2f} req/s")
    print(f"• Latency trung bình      : {avg_lat:.2f} ms")
    print(f"• Latency thấp nhất (Min) : {min_lat:.2f} ms")
    print(f"• Latency cao nhất (Max)  : {max_lat:.2f} ms")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Vehicle Fuel Consumption API Test Suite")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API Gateway URL (default: http://localhost:8000)")
    parser.add_argument("--spam", type=int, default=50, help="Số lượng request spam test (default: 50)")
    parser.add_argument("--concurrency", type=int, default=5, help="Số worker song song (default: 5)")
    parser.add_argument("--skip-spam", action="store_true", help="Bỏ qua bước spam test")

    args = parser.parse_args()

    print("\n" + "#" * 60)
    print("🚀 BỘ CÔNG CỤ TỰ ĐỘNG TEST & BENCHMARK API HỌC MÁY")
    print(f"Target URL: {args.url}")
    print("#" * 60 + "\n")

    if not run_health_check(args.url):
        print("\n⚠️ Vui lòng bật server trước khi chạy test:")
        print("   Docker:  docker compose up -d")
        print("   Local:   scripts\\run-local.bat")
        sys.exit(1)

    run_unit_tests(args.url)

    if not args.skip_spam:
        run_spam_test(args.url, total_requests=args.spam, concurrency=args.concurrency)


if __name__ == "__main__":
    main()
