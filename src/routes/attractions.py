import dotenv
import openrouteservice


from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse


from src.schemas.schema import Coords
from src.services.service import get_openrouteservice_key, get_foursquare_key
from src.services.attractions_service import get_route, get_pois_along_route, generate_map


router = APIRouter()

dotenv.load_dotenv()

ORS_API_KEY = get_openrouteservice_key(version='v2')
FOURSQUARE_API_KEY = get_foursquare_key()

ors_client = openrouteservice.Client(key=ORS_API_KEY)


@router.post("/get-attractions/")
def get_attractions(
    cords: Coords
):
    """API endpoint to get entertainment attractions along a route"""

    start = [cords.start[1], cords.start[0]]
    end = [cords.end[1], cords.end[0]]

    try:
        route_coords = get_route(start, end)
        pois = get_pois_along_route(route_coords)
        map_file = generate_map(route_coords, pois)

        with open(map_file, "r", encoding="utf-8") as f:
            map_html = f.read()

        return HTMLResponse(content=map_html)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
