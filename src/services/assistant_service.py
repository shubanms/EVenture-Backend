import folium
import openrouteservice


from geopy.distance import geodesic


from src.services.service import load_dataset
from src.services.service import get_openrouteservice_key
from src.core.logger import logger


ev_stations = load_dataset(r"src/data/EV_data.csv")


ORS_API_KEY = get_openrouteservice_key(version='v2')
client = openrouteservice.Client(key=ORS_API_KEY)


def find_top_3_stations(user_lat, user_lng, vehicle_type, power_type):
    user_location = (user_lat, user_lng)
    distances = []

    filtered_stations = ev_stations[(ev_stations['vehicle_type'] == vehicle_type) & (
        ev_stations['power_type'] == power_type)]

    for _, row in filtered_stations.iterrows():
        station_location = (row['latitude'], row['longitude'])
        distance = geodesic(user_location, station_location).km
        distances.append((row, distance))

    distances.sort(key=lambda x: x[1])  # Sort by distance
    return distances[:3]  # Return top 3 nearest stations


def get_travel_time(user_lat, user_lng, station_lat, station_lng):
    try:
        route = client.directions(
            coordinates=[[user_lng, user_lat], [station_lng, station_lat]],
            profile='driving-car',
            format='geojson'
        )
        # Convert seconds to minutes
        duration = route['features'][0]['properties']['segments'][0]['duration'] / 60
        return round(duration, 2)
    except Exception as e:
        logger.error(f"Error fetching travel time: {e}")
        return None


def generate_map(user_lat, user_lng, stations):
    m = folium.Map(location=[user_lat, user_lng], zoom_start=12)
    folium.Marker([user_lat, user_lng], popup="Your Location",
                  icon=folium.Icon(color="blue")).add_to(m)

    colors = ["red", "purple", "orange"]
    for i, (station, distance) in enumerate(stations):
        popup_text = (f"{station['name']}\nVendor: {station['vendor_name']}\n"
                      f"Cost: {station['cost_per_unit']}\nPower: {station['power_type']}\n"
                      f"Vehicle Type: {station['vehicle_type']}\nDistance: {distance:.2f} km")
        folium.Marker([
            station['latitude'], station['longitude']],
            popup=popup_text,
            icon=folium.Icon(color=colors[i % len(colors)])
        ).add_to(m)

        try:
            route = client.directions(
                coordinates=[[user_lng, user_lat], [
                    station['longitude'], station['latitude']]],
                profile='driving-car',
                format='geojson'
            )
            route_coords = [(coord[1], coord[0])
                            for coord in route['features'][0]['geometry']['coordinates']]
            folium.PolyLine(route_coords, color=colors[i % len(
                colors)], weight=5, opacity=0.7).add_to(m)
        except Exception as e:
            logger.error(f"Error generating route: {e}")

    map_filename = r"src//maps//ev_map.html"

    logger.info("Generating and saving map")

    m.save(map_filename)
    
    return map_filename
