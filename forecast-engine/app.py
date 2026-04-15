import os
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.get('/')
def index():
    return jsonify({"service": "forecast-engine", "status": "running"})


@app.get('/health')
def health():
    return jsonify({"status": "ok"})


@app.post('/forecast')
def forecast():
    payload = request.get_json(force=True)
    mode = payload.get("mode", "history")
    base_volume = float(payload.get("baseVolume", 0))
    growth_percent = float(payload.get("growthPercent", 0))
    market_factor = float(payload.get("marketFactor", 0))

    if mode == "history":
        multiplier = 1.10
        confidence = 0.80
    elif mode == "user_growth":
        multiplier = 1 + (growth_percent / 100.0)
        confidence = 0.75
    elif mode == "market_intelligence":
        multiplier = 1 + (market_factor / 100.0)
        confidence = 0.78
    else:
        multiplier = 1.0
        confidence = 0.60

    forecast_volume = round(max(0, base_volume * multiplier))

    return jsonify({
        "forecastVolume": int(forecast_volume),
        "confidence": confidence
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', '5001'))
    app.run(host='0.0.0.0', port=port)
