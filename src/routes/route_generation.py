from fastapi import APIRouter
from fastapi.responses import HTMLResponse


from src.core.logger import logger
from src.schemas.schema import RouteRequest
from src.services.route_service import generate_route


router = APIRouter()


@router.post("/get-route/")
async def get_route(request: RouteRequest):
    logger.info(f"Generating route for coordinates: {request.coords}")
    logger.info(
        f"Vehicle Information:\n"
        f"Vehicle Type: {request.vehicle_type}\n"
        f"Charger Type: {request.charger_type}\n"
        f"Power Type: {request.power_type}\n"
    )

    map_file = generate_route(
        request.coords, request.vehicle_type, request.charger_type, request.power_type)

    with open(map_file, "r", encoding="utf-8") as f:
        map_html = f.read()

    return HTMLResponse(content=map_html)
