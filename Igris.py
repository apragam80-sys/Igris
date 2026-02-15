import os
from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

API_KEY = os.environ.get("OPENWEATHER_API_KEY")

@app.route("/")
def home():
    return "Weather Bot is Live 🚀"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    if not req:
        return jsonify({"fulfillmentText": "Invalid request."})

    try:
        city = req["queryResult"]["parameters"].get("geo-city")
    except:
        return jsonify({"fulfillmentText": "City not provided."})

    if not city:
        return jsonify({"fulfillmentText": "Please provide a city name."})

    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({
            "fulfillmentText": f"❌ Sorry, I couldn't find weather for {city}."
        })

    data = response.json()

    forecast_text = f"🌍 5-Day Weather Forecast for *{city.title()}*\n\n"

    # Emoji mapping
    def get_emoji(description):
        description = description.lower()
        if "rain" in description:
            return "🌧️"
        elif "cloud" in description:
            return "☁️"
        elif "clear" in description:
            return "☀️"
        elif "storm" in description or "thunder" in description:
            return "⛈️"
        elif "snow" in description:
            return "❄️"
        else:
            return "🌤️"

    # Take one forecast per day (every 8th record = 24 hours)
    for i in range(0, 40, 8):
        day_data = data["list"][i]

        date_str = day_data["dt_txt"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        day_name = date_obj.strftime("%a")  # Mon, Tue, Wed

        temp = day_data["main"]["temp"]
        humidity = day_data["main"]["humidity"]
        wind_speed = day_data["wind"]["speed"]
        description = day_data["weather"][0]["description"]
        emoji = get_emoji(description)

        forecast_text += (
            f"{emoji} *{day_name}*\n"
            f"   🌡 Temp: {temp}°C\n"
            f"   💧 Humidity: {humidity}%\n"
            f"   🌬 Wind: {wind_speed} m/s\n"
            f"   📝 {description.title()}\n\n"
        )

    return jsonify({
        "fulfillmentText": forecast_text
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
