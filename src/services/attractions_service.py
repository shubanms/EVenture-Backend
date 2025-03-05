import folium
import requests
import openrouteservice


from fastapi import HTTPException


from src.services.service import get_openrouteservice_key, get_foursquare_key
from src.core.logger import logger


ORS_API_KEY = get_openrouteservice_key(version='v2')
ors_client = openrouteservice.Client(key=ORS_API_KEY)

FOURSQUARE_API_KEY = get_foursquare_key()


def get_route(start, end):
    """Fetch route coordinates from OpenRouteService"""
    try:
        route = ors_client.directions(
            coordinates=[start, end],
            profile='driving-car',
            format='geojson'
        )
        return route['features'][0]['geometry']['coordinates']
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching route data: {e}")


def get_pois_along_route(route_coords):
    """Fetch entertainment places along the route from Foursquare"""
    pois = []

    # Sample every 10th point for POI query
    for idx, coord in enumerate(route_coords[::25]):
        lon, lat = coord

        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            "Accept": "application/json",
            "Authorization": FOURSQUARE_API_KEY
        }
        params = {
            "ll": f"{lat},{lon}",
            "radius": 1000,
            "categories": "10000,13000,16000,18000",
            "limit": 2
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            pois.extend(response.json().get("results", []))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching POIs: {e}")

    return pois


def generate_map(route_coords, attractions):
    """Create a Folium map and save it as attraction.html"""
    if not route_coords:
        raise ValueError("Route coordinates are empty")

    start_lat, start_lon = route_coords[0][1], route_coords[0][0]
    m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

    folium.PolyLine(
        locations=[[lat, lon] for lon, lat in route_coords],
        color="blue",
        weight=5,
        opacity=0.7
    ).add_to(m)

    for attraction in attractions:
        lat = attraction["geocodes"]["main"]["latitude"]
        lon = attraction["geocodes"]["main"]["longitude"]
        name = attraction["name"]
        address = attraction["location"].get(
            "formatted_address", "Address not available")
        category = attraction["categories"][0]["name"] if attraction["categories"] else "Unknown"
        link = f"https://foursquare.com/v/{attraction['fsq_id']}"

        popup_content = f"""
        <b>{name}</b><br>
        <i>{category}</i><br>
        {address}<br>
        <a href="{link}" target="_blank">View on Foursquare</a>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=name,
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(m)

    logger.info("Generating and saving the map")

    map_filename = r"src//maps//attractions.html"
    m.save(map_filename)

    return map_filename
