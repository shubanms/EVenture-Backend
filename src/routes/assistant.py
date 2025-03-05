import dotenv
import openai


from fastapi import APIRouter, Query


from src.services.service import get_openai_key
from src.services.assistant_service import find_top_3_stations, get_travel_time, generate_map


router = APIRouter()


dotenv.load_dotenv()


openai.api_key = get_openai_key()


@router.get("/find_nearest_stations/")
def nearest_stations(lat: float, lng: float, vehicle_type: str, power_type: str):
    stations = find_top_3_stations(lat, lng, vehicle_type, power_type)
    station_data = []
    for station, distance in stations:
        travel_time = get_travel_time(
            lat, lng, station['latitude'], station['longitude'])
        station_data.append({
            "station_name": station['name'],
            "vendor": station['vendor_name'],
            "address": station['address'],
            "distance_km": round(distance, 2),
            "estimated_travel_time_min": travel_time if travel_time else "N/A",
            "cost_per_unit": station['cost_per_unit'],
            "power_type": station['power_type'],
            "vehicle_type": station['vehicle_type']
        })

    ev_map_file = generate_map(lat, lng, stations)
    return {"stations": station_data, "map_file": ev_map_file}


@router.post("/chat/")
def chat(query: str, vehicle_type: str, power_type: str, lat: float = Query(None), lng: float = Query(None)):
    emergency_phrases = ["out of charge",
                         "broke down", "stuck", "need help", "asap"]
    is_emergency = any(phrase in query.lower() for phrase in emergency_phrases)

    if lat is not None and lng is not None:
        station_info = nearest_stations(lat, lng, vehicle_type, power_type)
        response_text = "I understand how urgent this is for you! Here are the top 3 nearest EV charging stations:\n"
        for station in station_info["stations"]:
            response_text += (f"- {station['station_name']} (Vendor: {station['vendor']})\n"
                              f"  Address: {station['address']}\n"
                              f"  Cost: {station['cost_per_unit']}, Power: {station['power_type']}\n"
                              f"  Vehicle Type: {station['vehicle_type']}\n"
                              f"  Distance: {station['distance_km']} km, Estimated Travel Time: {station['estimated_travel_time_min']} mins.\n\n")
        if is_emergency:
            response_text += "It sounds like you're in a tough spot. If you're completely out of charge, check if the nearest station offers emergency charging. You might also consider contacting roadside assistance. Let me know how else I can help, and please stay safe!"
        else:
            response_text += "Let me know if you need anything else. Safe travels!"

        return {"response": response_text, "map_file": station_info["map_file"]}

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant that provides EV charging station information and real-time traffic insights."},
                  {"role": "user", "content": query}]
    )
    return {"response": response["choices"][0]["message"]["content"]}
