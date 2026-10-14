from flask import Flask, request, jsonify
import joblib
import pandas as pd
import time
import json
import os
from datetime import datetime, timezone

app = Flask(__name__)

MODEL_PATH = "rice_price_model.joblib"
LOG_PATH = "prediction_logs.jsonl"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"File {MODEL_PATH} belum ada. Jalankan notebook sampai bagian Deployment terlebih dahulu."
    )

artifact = joblib.load(MODEL_PATH)
model = artifact["model"]
feature_columns = artifact["feature_columns"]
outlier_bounds = artifact.get("outlier_bounds", {})
numeric_columns = artifact.get("numeric_columns", [])

# Statistik monitoring disimpan selama aplikasi berjalan.
request_latencies_ms = []
known_actuals = []
known_predictions = []


def log_event(event):
    """Menyimpan catatan permintaan ke file JSON Lines."""
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")


@app.get("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": True})


@app.post("/predict")
def predict():
    started = time.perf_counter()
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or "data" not in payload:
        return jsonify({"error": "Kirim JSON dengan key 'data'."}), 400

    rows = payload["data"]
    if isinstance(rows, dict):
        rows = [rows]
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        return jsonify({"error": "Nilai 'data' harus berupa satu objek fitur atau daftar objek fitur."}), 400

    try:
        input_df = pd.DataFrame(rows)
        missing = [col for col in feature_columns if col not in input_df.columns]
        extra = [col for col in input_df.columns if col not in feature_columns]
        if missing:
            return jsonify({"error": "Fitur wajib belum dikirim.", "missing_features": missing}), 400
        if extra:
            # Kolom tambahan tidak digunakan model, tetapi diberitahukan ke pemanggil.
            input_df = input_df.drop(columns=extra)
        input_df = input_df[feature_columns].copy()

        # Terapkan batas outlier yang dihitung dari data training.
        for col in numeric_columns:
            if col in input_df.columns and col in outlier_bounds:
                low, high = outlier_bounds[col]
                input_df[col] = pd.to_numeric(input_df[col], errors="coerce").clip(lower=low, upper=high)

        predictions = model.predict(input_df).tolist()
        latency_ms = (time.perf_counter() - started) * 1000
        request_latencies_ms.append(latency_ms)

        actual = payload.get("actual_price")
        if actual is not None:
            actual_values = actual if isinstance(actual, list) else [actual]
            if len(actual_values) == len(predictions):
                known_actuals.extend(float(x) for x in actual_values)
                known_predictions.extend(float(x) for x in predictions)

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rows": len(predictions),
            "predictions": predictions,
            "latency_ms": latency_ms,
            "actual_price_provided": actual is not None,
        }
        log_event(event)
        response = {"prediction": predictions, "latency_ms": round(latency_ms, 3)}
        if extra:
            response["ignored_extra_features"] = extra
        return jsonify(response)
    except (TypeError, ValueError) as exc:
        return jsonify({"error": "Format atau tipe data input tidak sesuai.", "detail": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": "Prediksi gagal diproses.", "detail": str(exc)}), 500


@app.get("/monitoring")
def monitoring():
    result = {
        "total_request": len(request_latencies_ms),
        "average_latency_ms": round(sum(request_latencies_ms) / len(request_latencies_ms), 3) if request_latencies_ms else None,
        "max_latency_ms": round(max(request_latencies_ms), 3) if request_latencies_ms else None,
        "evaluated_predictions": len(known_actuals),
        "note": "MSE dan R-squared hanya dihitung jika actual_price dikirim dan tersedia untuk prediksi yang bersangkutan. Statistik request tersimpan di memori selama API berjalan; log permintaan dicatat di prediction_logs.jsonl."
    }
    if known_actuals:
        from sklearn.metrics import mean_squared_error, r2_score
        result["MSE"] = float(mean_squared_error(known_actuals, known_predictions))
        result["R_squared"] = float(r2_score(known_actuals, known_predictions)) if len(known_actuals) >= 2 else None
    else:
        result["MSE"] = None
        result["R_squared"] = None
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
