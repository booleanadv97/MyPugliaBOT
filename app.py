from flask import Flask, request, jsonify
import json
import requests
import googlemaps

# Telegram bot token
BOT_TOKEN = "7359117515:AAGgeMyoN7sQ0VbEMQI0Bnx9B48FMXVMzto"
WEATHER_API_KEY = "a26d52cbb20d67a2adb5379a13c920a7"

app = Flask(__name__)

# Google maps configuration
gmaps = googlemaps.Client(key="AIzaSyBCg-wRG41EjUesSn3Z6hEjPoZG3BbDQEE")

# Function to send messages via Telegram API
def send_message(chat_id, text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text}
  response = requests.post(url, json=payload)
  if response.status_code != 200:
    print(f"Error while sending the message: {response.text}")

def build_list_of_places(places):
  result = ""
  for place in places:
    result += place["name"]+". Address: "+place["address"]+".\n\n"
  return result

def get_current_weather(api_key, city_name):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "units": "metric",
        "appid": api_key,
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        if data["cod"] == 200:
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            return f"Current weather in {city_name}: {weather_description}, Temperature: {temperature}°C, Humidity: {humidity}%"
        else:
            return "City not found."
    except Exception as e:
        return f"Error fetching weather data: {e}"

def get_places(city_name, search_type, search_radius=5000):
  try:
    locations = gmaps.geocode(city_name)
    if locations:
      # Extract latitude and longitude from the user's location
      lat = locations[0]["geometry"]["location"]["lat"]
      lng = locations[0]["geometry"]["location"]["lng"]

      # Build the attractions API request
      places = gmaps.places_nearby(
          location=(lat, lng), radius=search_radius, type=search_type
      )

      result = []
      for place in places["results"]:
        place_data = {
          "name": place["name"],
          "address": place["vicinity"],
          "lat": place["geometry"]["location"]["lat"],
          "lng": place["geometry"]["location"]["lng"],
        }
        result.append(place_data)
      return result
    else:
      print(f"Error city not found: {city_name}")
  except googlemaps.exceptions.HTTPError as err:
    print(f"Error during API request: {err}")
  return None

@app.route("/webhook", methods=["POST"])
def process_message():
  data = request.get_json()
  chat_id = data.get("session", {}).split("/")[-1]
  # Extract intent
  intent = data["queryResult"]["intent"]["displayName"]
  # Perform actions based on the intent
  if intent == "Start":
    response = "Hello, I am your personal assistant during your stay in Puglia. If you need help, don\'t hesitate to ask."
  elif intent == "Help":
    response = "Hello, I can help you find the nearest hotel, recommend a place to enjoy typical Apulian dishes, suggest one of the magical spots in Puglia, or provide real-time updates on weather, traffic, and road conditions."
  elif intent == "RequestLodging":
    response = "Sure, please provide your current location so that I can create a list of accommodations closest to you."
  # Request user location in order to find nearby attractions
  elif intent == "RequestAttractions":
    response = "Sure, please provide your current location so that I can create a list of nearby places to visit."
  elif intent == "RequestWeatherUpdate":
    response = "Sure, please provide your current location so that I can provide you real-time weather information."
  # Providing a list of attractions nearby user's location
  elif intent == "UserProvidesLocation":
    location = data['queryResult']['parameters'].get('location', None)
    if location:
      context = data['queryResult']['outputContexts'][0]['name']
      if "userrequestattractions" in context:
        attractions = get_places(location['city'],"tourist_attraction")
        response = build_list_of_places(attractions)
      elif "userrequestlodging" in context:
        accomodations = get_places(location['city'], "lodging")
        response = build_list_of_places(accomodations)
      elif "userrequestweatherupdate" in context:
        response = get_current_weather(WEATHER_API_KEY, location['city'])
  send_message(chat_id, response)
  return jsonify({"fulfillmentText": response})   
