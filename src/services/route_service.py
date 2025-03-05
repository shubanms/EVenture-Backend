import os
import folium
import openrouteservice

import numpy as np


from scipy.spatial import cKDTree
from geopy.distance import geodesic


from dotenv import load_dotenv
from src.services.service import load_dataset
from src.services.service import get_openrouteservice_key
from src.core.logger import logger


load_dotenv()


def build_kdtree(route_coords):
    return cKDTree(np.array(route_coords))


def is_near_route(lat, lon, route_tree, threshold=300):
    point = np.array([lat, lon])
    _, nearest_idx = route_tree.query(point)
    nearest_point = route_tree.data[nearest_idx]
    distance = geodesic(point, (nearest_point[0], nearest_point[1])).meters
    return distance < threshold


def generate_route(cords, vehicle_type, charger_type, power_type):
    client = openrouteservice.Client(
        key=get_openrouteservice_key(version='v1'))
    coords = (cords.start[::-1], cords.end[::-1])

    routes = client.directions(
        coordinates=coords,
        profile='driving-car',
        format='geojson',
        alternative_routes={"share_factor": 0.4, "target_count": 2},
    )

    m = folium.Map(location=cords.start, zoom_start=13)
    folium.Marker(cords.start, popup="Start",
                  icon=folium.Icon(color="purple")).add_to(m)
    folium.Marker(cords.end, popup="End",
                  icon=folium.Icon(color="beige")).add_to(m)

    df = load_dataset("src\\data\\EV_data.csv")
    route_station_counts = []
    route_stations = []

    for i, route in enumerate(routes['features']):
        route_coords = [(coord[1], coord[0])
                        for coord in route['geometry']['coordinates']]
        route_tree = build_kdtree(route_coords)

        valid_stations = df[df.apply(lambda row: is_near_route(
            row["latitude"], row["longitude"], route_tree), axis=1)]
        logger.info(
            f"Route {i+1}: Found {len(valid_stations)} valid stations before plotting.")

        route_stations.append(valid_stations)
        route_station_counts.append(len(valid_stations))

    if len(route_station_counts) == 0:
        logger.info("No routes found.")
        return None

    best_route_idx = route_station_counts.index(max(route_station_counts))

    second_best_idx = None
    if len(route_station_counts) > 1:
        second_best_idx = sorted(range(len(
            route_station_counts)), key=lambda i: route_station_counts[i], reverse=True)[1]

    logger.info(
        f"Best Route ({best_route_idx+1}): {route_station_counts[best_route_idx]} valid charging stations")
    if second_best_idx is not None:
        logger.info(
            f"Second Best Route ({second_best_idx+1}): {route_station_counts[second_best_idx]} valid charging stations")

    for i, route in enumerate(routes['features']):
        if i == best_route_idx or (second_best_idx is not None and i == second_best_idx):
            route_coords = [(coord[1], coord[0])
                            for coord in route['geometry']['coordinates']]
            color = "orange" if i == best_route_idx else "green"
            folium.PolyLine(route_coords, color=color,
                            weight=5, opacity=0.7).add_to(m)

            logger.info(f"Plotting stations for Route {i+1}...")
            for _, row in route_stations[i].iterrows():
                folium.Marker(
                    (row["latitude"], row["longitude"]),
                    popup=f"{row['name']} ({row['latitude']}, {row['longitude']})",
                    icon=folium.Icon(color="blue", icon="bolt")
                ).add_to(m)

    logger.info("Generating and saving the route map")

    map_file = r"src//maps//route_map.html"
    m.save(map_file)

    return map_file
