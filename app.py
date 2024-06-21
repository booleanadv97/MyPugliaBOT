from flask import Flask, request, jsonify
import requests
import googlemaps

# Telegram bot token
BOT_TOKEN = "7359117515:AAGgeMyoN7sQ0VbEMQI0Bnx9B48FMXVMzto"

app = Flask(__name__)

# Google maps configuration
gmaps = googlemaps.Client(key="AIzaSyBCg-wRG41EjUesSn3Z6hEjPoZG3BbDQEE")

# Function to send messages via Telegram API
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print(f"Errore nell'invio del messaggio: {response.text}")

# Function that provides a list of nearby attractions 
def get_attractions(city_name, search_radius=5000):
  try:
    locations = gmaps.geocode(city_name)
    if locations:
      # Extract latitude and longitude from the user's location
      lat = locations[0]["geometry"]["location"]["lat"]
      lng = locations[0]["geometry"]["location"]["lng"]

      # Build the attractions API request
      places = gmaps.places_nearby(
          location=(lat, lng), radius=search_radius, type="tourist_attraction"
      )

      attractions = []
      for place in places["results"]:
        attrazione = {
          "name": place["name"],
          "address": place["vicinity"],
          "lat": place["geometry"]["location"]["lat"],
          "lng": place["geometry"]["location"]["lng"],
        }
        attractions.append(attrazione)
      return attractions
    else:
      print(f"Impossibile trovare la città: {city_name}")
  except googlemaps.exceptions.HTTPError as err:
    print(f"Errore durante la richiesta API: {err}")
  return None

@app.route("/webhook", methods=["POST"])
def process_message():
    data = request.get_json()
    chat_id = data.get("session", {}).split("/")[-1]
    # Extract intent
    intent = data["queryResult"]["intent"]["displayName"]
    # Perform actions based on the intent
    if intent == "Start":
        response = "Ciao, sono il tuo assistente personale durante la tua permanenza in Puglia. Se hai bisogno di aiuto non esitare a chiedere aiuto."
    elif intent == "Help":
        response = "Ciao, posso aiutarti a trovare l'hotel più vicino a te, un posto dove mangiare le tipiche pietanze pugliesi, consigliarti uno dei magici posti della Puglia oppure offrirti aggiornamenti in tempo reale sulle condizioni meteorologiche, sul traffico e sulle condizioni stradali."
    # Request user location in order to find nearby attractions
    elif intent == "RequestAttractions":
        response = "Certo, indicami la tua posizione attuale per poter creare una lista con i posti da visitare più vicini a te."
    # Providing a list of attractions nearby user's location
    elif intent == "UserProvidesLocationForAttractions":
        location = data['queryResult']['parameters'].get('location', None)
        if location:
            attractions = get_attractions(location['city'])
            response = str(attractions)
    send_message(chat_id, response)
    return jsonify({"fulfillmentText": response})   
