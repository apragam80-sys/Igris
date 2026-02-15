from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Get API key from Render Environment Variable
API_KEY = os.environ.get("OPENWEATHER_API_KEY")


# ------------------------------
# Emoji helper function
# ------------------------------
def get_weather_emoji(description):
    description = description.lower()

    if "clear" in description:
        return "☀️"
    elif "cloud" in description:
        return "☁️"
    elif "rain" in description:
        return "🌧️"
    elif "storm" in description or "thunder" in description:
        return "🌩️"
    elif "snow" in description:
        return "❄️"
    elif "mist" in description or "haze" in description:
        return "🌫️"
    else:
        return "🌍"


# ------------------------------
# Home Route
# ------------------------------
@app.route("/")
def home():
    return "Weather Bot is Live 🚀"


# ------------------------------
# Webhook Route (Dialogflow)
# ------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    if not req:
        return jsonify({"fulfillmentText": "Invalid request."})

    try:
        city = req["queryResult"]["parameters"].get("geo-city")
        date_param = req["queryResult"]["parameters"].get("date-time")
    except:
        return jsonify({"fulfillmentText": "Missing parameters."})

    if not city:
        return jsonify({"fulfillmentText": "Please provide a city name."})

    # OpenWeather 5-day forecast API
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({
            "fulfillmentText": f"❌ Sorry, I couldn't find weather for {city}."
        })

    data = response.json()

    # -------------------------------------
    # If user asked for specific date
    # -------------------------------------
    if date_param:
        target_date = date_param.split("T")[0]

        for item in data["list"]:
            forecast_date = item["dt_txt"].split(" ")[0]

            if forecast_date == target_date:
                temp = item["main"]["temp"]
                humidity = item["main"]["humidity"]
                wind = item["wind"]["speed"]
                desc = item["weather"][0]["description"]
                emoji = get_weather_emoji(desc)

                return jsonify({
                    "fulfillmentText":
                        f"📅 Weather for {city.title()} on {target_date}\n\n"
                        f"{emoji} {desc.title()}\n"
                        f"🌡 Temperature: {temp}°C\n"
                        f"💧 Humidity: {humidity}%\n"
                        f"🌬 Wind Speed: {wind} m/s"
                })

        return jsonify({
            "fulfillmentText": "Forecast not available for that date."
        })

    # -------------------------------------
    # Otherwise return 5-day forecast
    # -------------------------------------
    forecast_text = f"🌍 5-Day Forecast for {city.title()}\n\n"

    # OpenWeather gives data every 3 hours
    # Every 8th item = next day (approx 24 hours)
    for i in range(0, 40, 8):
        day_data = data["list"][i]

        date_obj = datetime.strptime(
            day_data["dt_txt"], "%Y-%m-%d %H:%M:%S")
        day_name = date_obj.strftime("%a")

        temp = day_data["main"]["temp"]
        humidity = day_data["main"]["humidity"]
        wind = day_data["wind"]["speed"]
        desc = day_data["weather"][0]["description"]
        emoji = get_weather_emoji(desc)

        forecast_text += (
            f"📅 {day_name}\n"
            f"{emoji} {desc.title()}\n"
            f"🌡 {temp}°C | 💧 {humidity}% | 🌬 {wind} m/s\n\n"
        )

    return jsonify({"fulfillmentText": forecast_text})


# ------------------------------
# Run App (Render Compatible)
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
