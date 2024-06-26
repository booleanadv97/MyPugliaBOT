from flask import Flask, request, jsonify
import json
import requests
import googlemaps
import random

# API keys
BOT_TOKEN = "REPLACE_WITH_YOUR_TELEGRAM_API_KEY"
TOMTOM_API = "REPLACE_WITH_YOUR_TOMTOM_API_KEY"
WEATHER_API_KEY = "REPLACE_WITH_YOUR_WEATHER_API_KEY"

app = Flask(__name__)

# Google maps configuration
gmaps = googlemaps.Client(key="AIzaSyBCg-wRG41EjUesSn3Z6hEjPoZG3BbDQEE")

def puglia_facts(lang='en'):
    facts = {
        'en': [
            "Miracles in Lecce: In Piazza Sant'Oronzo, the eighteenth-century statue of the Patron Saint sits on a bare column, originally from the town of Brindisi. This column marked the end of the Via Appia, one of the most important roads in Ancient Rome. It was donated by the people of Brindisi to the Patron Saint of Lecce, when the town was miraculously spared by the plague that ravaged Salento in the seventeenth century.",
            "Swindlers in Alberobello: Famous for its trulli, one of the house styles you can only find in Puglia, this town was gifted to the first Count of Conversano by Robert of Anjou, as a reward for taking part in the Crusades. The oldest trulli date back to the fourteenth century and they were built without mortar so that they could be easily dismantled in case the emissaries of the Kingdom of Naples, which imposed heavy taxes on any new house, came by to check on the inhabitants.",
            "Gods and dolphins in Taranto: According to Greek mythology, Taras was the son of the nymph Satyria and Neptune, the god of the sea. He was the head of a fleet that arrived on the banks of the river where the town was later built. He immediately started offering sacrifices to thank his father for the good voyage they had and to enquire whether it was wise to build a town here when suddenly he saw a dolphin jump into the waters of the river. The young man interpreted this apparition as a sign of Neptune's encouragement to found Taranto.",
            "Along the Templar trail in Puglia: The history of the Knights Templar is certainly one of the most famous and fascinating in Christian history. Many people are familiar with it but few know that the Knights of Christ and the Temple of Solomon were also present in Puglia. The first official document attesting to the presence of the Templars in the region dates back to 1143.",
            "Puglia is home to over 50 million olive trees: Many of them centuries old. Puglia needed to enact laws to deter people from other parts of Italy coming down and digging up those valuable olive trees to bring them back and plant them on their land. It's now illegal to dig up a tree from Puglian soil.",
            "Puglia is famous for its olive oil production: The region provides around 40% of the country's olive oil, which amounts to around 300,000 tonnes every single year.",
            "Puglia has the longest coastline of any Italian mainland region: The heel of Italy's boot-like shape is the defining geographical feature of the area, and is a key reason behind the flowing lengths of coast, totalling around 800km.",
            "Puglia was originally colonised by Mycenaean Greeks: One of Italy's most archaeologically interesting areas, Puglia is an absolute hub for history.",
            "Puglia is pure magic."
        ],
        'it': [
            "Miracoli a Lecce: In Piazza Sant'Oronzo, la statua settecentesca del Santo Patrono si trova su una colonna nuda, originariamente della città di Brindisi. Questa colonna segnava la fine della Via Appia, una delle strade più importanti dell'Antica Roma. Fu donata dal popolo di Brindisi al Santo Patrono di Lecce, quando la città fu miracolosamente risparmiata dalla peste che devastò il Salento nel XVII secolo.",
            "Truffatori ad Alberobello: Famosa per i suoi trulli, uno degli stili di casa che si possono trovare solo in Puglia, questa città fu donata al primo Conte di Conversano da Roberto d'Angiò, come ricompensa per aver partecipato alle Crociate. I trulli più antichi risalgono al XIV secolo e furono costruiti senza malta in modo che potessero essere facilmente smontati nel caso in cui gli emissari del Regno di Napoli, che imponevano pesanti tasse su ogni nuova casa, passassero a controllare gli abitanti.",
            "Dei e delfini a Taranto: Secondo la mitologia greca, Taras era il figlio della ninfa Satyria e di Nettuno, il dio del mare. Era a capo di una flotta che arrivò sulle rive del fiume dove in seguito fu costruita la città. Iniziò subito ad offrire sacrifici per ringraziare suo padre per il buon viaggio che avevano fatto e per chiedere se fosse saggio costruire una città qui quando all'improvviso vide un delfino saltare nelle acque del fiume. Il giovane interpretò questa apparizione come un segno dell'incoraggiamento di Nettuno a fondare Taranto.",
            "Lungo la via dei Templari in Puglia: La storia dei Cavalieri Templari è certamente una delle più famose e affascinanti della storia cristiana. Molte persone la conoscono ma pochi sanno che i Cavalieri di Cristo e del Tempio di Salomone erano presenti anche in Puglia. Il primo documento ufficiale che attesta la presenza dei Templari nella regione risale al 1143.",
            "La Puglia ospita oltre 50 milioni di ulivi: Molti di essi secolari. La Puglia ha dovuto emanare leggi per dissuadere le persone da altre parti d'Italia a scendere e scavare quegli ulivi preziosi per riportarli indietro e piantarli sulla loro terra. Ora è illegale scavare un albero dal suolo pugliese.",
            "La Puglia è famosa per la sua produzione di olio d'oliva: La regione fornisce circa il 40% dell'olio d'oliva del paese, che ammonta a circa 300.000 tonnellate ogni anno.",
            "La Puglia ha la costa più lunga di qualsiasi regione italiana continentale: Il tacco della forma a stivale dell'Italia è la caratteristica geografica che definisce l'area, ed è la ragione principale dietro le lunghezze fluttuanti della costa, che totalizzano circa 800km.",
            "La Puglia fu originariamente colonizzata dai Greci Micenei: Una delle aree archeologicamente più interessanti d'Italia, la Puglia è un vero e proprio centro per la storia.",
            "La Puglia è pura magia."
        ]
    }
    number = int(random.uniform(0, len(facts[lang])))
    return facts[lang][number]



# Function to send messages via Telegram API
def send_message(chat_id, text):
  url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  payload = {"chat_id": chat_id, "text": text}
  response = requests.post(url, json=payload)
  if response.status_code != 200:
    print(f"Error while sending the message: {response.text}")


def is_in_apulia(address):
  coords = gmaps.geocode(address)
  if coords:
    lat = coords[0]["geometry"]["location"]["lat"]
    lng = coords[0]["geometry"]["location"]["lng"]
    reverse_geocode_result = gmaps.reverse_geocode((lat, lng))
    for result in reverse_geocode_result:
        for component in result['address_components']:
            if 'administrative_area_level_1' in component['types']:  
                region = component['long_name']
                break
    return region == "Apulia"

def get_coords(place):
  coords = gmaps.geocode(place)
  if coords:
    lat = coords[0]["geometry"]["location"]["lat"]
    lng = coords[0]["geometry"]["location"]["lng"]
    return lat,lng
  return None

def get_traffic_flow(city, language):
  lat,lng = get_coords(city)
  if lat and lng:
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lng}&key={TOMTOM_API}"
    response = requests.get(url)
    data = json.loads(response.text)
    current_speed = data['flowSegmentData']['currentSpeed']
    free_flow_speed = data['flowSegmentData']['freeFlowSpeed']
    if current_speed < free_flow_speed * 0.7:  
        if language == "it":
          return "C\'è congestione del traffico nella posizione fornita."
        else:
          return "There is traffic congestion in the given location."
    else:
        if language == "it":
          return "Il traffico scorre fluidamente nella posizione fornita."
        else:
          return "Traffic is flowing smoothly in the given location."
  else:
    return "Could not retrieve location."

def build_list_of_places(places, language):
  result = ""
  for place in places:
    if language == "it":
      result += place["name"]+". Indirizzo: "+place["address"]+".\n\n"
    else:
      result += place["name"]+". Address: "+place["address"]+".\n\n" 
  return result

def get_current_weather(api_key, city_name, language):
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
            if language == "it":
              return f"Condizioni meteo attuali in {city_name}: {weather_description}, Temperatura: {temperature}°C, Umidità: {humidity}%"
            else:
              return f"Weather conditions in {city_name}: {weather_description}, Temperature: {temperature}°C, Humidity: {humidity}%"
        else:
            return "City not found."
    except Exception as e:
        return f"Error fetching weather data: {e}"

def get_places(position, search_type, search_radius=5000):
  try:
      lat,lng = get_coords(position)
      if lat and lng:
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
        print(f"Error location not found: {position}")
  except googlemaps.exceptions.HTTPError as err:
    print(f"Error during API request: {err}")
  return None

@app.route("/webhook", methods=["POST"])
def process_message():
  data = request.get_json()
  chat_id = data.get("session", {}).split("/")[-1]
  # Extract intent
  intent = data["queryResult"]["intent"]["displayName"]
  language = data.get('queryResult', {}).get('languageCode')
  # Perform actions based on the intent
  if intent == "Start":
    if language == "it":
      response = "Ciao, sono il tuo assistente personale durante il tuo soggiorno in Puglia. Per iniziare prova a chiedere 'aiuto'."
    else:
      response = "Hello, I am your personal assistant during your stay in Puglia. To begin you can ask for 'help'."
  elif intent == "Help":
    if language == "it":
      response = "Ciao, posso aiutarti a trovare l\'hotel più vicino, consigliarti un posto dove gustare piatti tipici pugliesi, suggerirti uno dei luoghi magici in Puglia, fornirti aggiornamenti in tempo reale sul meteo, il traffico e le condizioni stradali o semplicemente rendere la tua giornata migliore con una curiosità."
    else:
      response = "Hello, I can help you find the nearest hotel, recommend a place to enjoy typical Apulian dishes, suggest one of the magical spots in Apulia, provide real-time updates on weather, traffic, and road conditions or simply make your day better with a trivia."
  elif intent == "RequestLodging":
    if language == "it":
      response = "Certamente, per favore fornisci la tua posizione attuale in modo che io possa creare un elenco di alloggi più vicini a te."
    else:
      response = "Sure, please provide your current location so that I can create a list of accommodations closest to you."
  elif intent == "RequestTrafficUpdate":
    if language == "it":
      response = "Certamente, per favore fornisci la tua posizione attuale in modo che io possa informarti sullo stato attuale del flusso del traffico."
    else:
      response = "Sure, please provide your current location so that I can inform you about current traffic flow status."
  elif intent == "RequestAttractions":
    if language == "it":
      response = "Certamente, per favore fornisci la tua posizione attuale in modo che io possa creare un elenco di luoghi vicini da visitare."
    else:
      response = "Sure, please provide your current location so that I can create a list of nearby places to visit."
  elif intent == "RequestRestaurantsNearby":
    if language == "it":
      response = "Certamente, per favore fornisci la tua posizione attuale in modo che io possa creare un elenco di ristoranti nelle vicinanze dove puoi mangiare."
    else:
      response = "Sure, please provide your current location so that I can create a list of nearby restaurants where you can eat."
  elif intent == "RequestWeatherUpdate":
    if language == "it":
      response = "Certamente, per favore fornisci la tua posizione attuale in modo che io possa fornirti informazioni meteo in tempo reale."
    else:
      response = "Sure, please provide your current location so that I can provide you real-time weather information."
  elif intent == "Trivia":
    if language == "it":
      response = "Ecco un fatto interessante sulla Puglia: \n\n" + puglia_facts("it")
    else: 
      response = "Here's an interesting fact about Puglia: \n\n" + puglia_facts("en")
  elif intent == "UserProvidesLocation":
    location = data['queryResult']['parameters'].get('location', None)
    response = str(location)
    if location and is_in_apulia(location['city']):
      context = data['queryResult']['outputContexts'][0]['name']
      if "userrequestattractions" in context:
          attractions = get_places(location['street-address'] +", "+ location['city'],"tourist_attraction")
          response = "Ecco una lista di attrazioni vicine: \n\n" + build_list_of_places(attractions, language)
      elif "userrequestlodging" in context:
        accomodations = get_places(location['street-address'] +", "+ location['city'], "lodging")
        response = "Ecco una lista di alloggi vicini: \n\n" + build_list_of_places(accomodations, language)
      elif "userrequestrestaurant" in context:
        restaurants = get_places(location['street-address'] +", "+ location['city'], "restaurant")
        response = "Ecco una lista di ristoranti in vicinanza: \n\n" + build_list_of_places(restaurants, language)
      elif "userrequestweatherupdate" in context:
        response = get_current_weather(WEATHER_API_KEY, location['city'], language)
      elif "userrequesttrafficupdate" in context:
        response = get_traffic_flow(location['street-address'] +", "+ location['city'], language)
    else:
      if language == "it":
         response = "Posizione non valida, fornisci una posizione corretta all\'interno della Puglia."
      else:
        response = "Invalid location, please provide a correct location within Apulia."
  send_message(chat_id, response)
  return jsonify({"fulfillmentText": response})   
