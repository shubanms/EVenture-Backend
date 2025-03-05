from pydantic import BaseModel
from typing import Tuple, Optional


class Coords(BaseModel):
    start: Tuple[float, float]
    end: Tuple[float, float]


class RouteRequest(BaseModel):
    coords: Coords
    vehicle_type: Optional[str] = None
    charger_type: Optional[str] = None
    power_type: Optional[str] = None
