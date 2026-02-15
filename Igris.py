from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("9eb5957851c72f50cec49b8c9fa1a424")

@app.route('/')
def home():
    return "Weather Bot is Live 🚀"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    if not req:
        return jsonify({"fulfillmentText": "Invalid request."})

    try:
        city = req['queryResult']['parameters'].get('geo-city')
    except:
        return jsonify({"fulfillmentText": "City not provided."})

    if not city:
        return jsonify({"fulfillmentText": "Please provide a city name."})

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({
            "fulfillmentText": f"Sorry, I couldn't find weather for {city}."
        })

    data = response.json()

    temp = data['main']['temp']
    description = data['weather'][0]['description']

    return jsonify({
        "fulfillmentText": f"The current temperature in {city} is {temp}°C with {description}."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
