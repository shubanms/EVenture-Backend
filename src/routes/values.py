from fastapi import APIRouter

from src.core.logger import logger

route = APIRouter()


@route.post("/get-values/")
def get_values():

    logger.info("Getting values")

    return {
        'vehicle_type': ['2W', '3W', '4W'],
        'charger_type': ['BEVC DC 001', 'BEVC AC 001', 'AC Type 2',
                         'CCS2/CHADEMO/TYPE 2 AC', 'CCS/ CHAdeMO', 'DC-001',
                         'IEC-62196-T2-COMBO', 'CHADEMO', 'IEC-62196-T2', 'BEVC-AC001',
                         '5A/15A Socket', 'Type 2 Plug', 'TYPE - 2', 'AC001', 'T2', 'DC',
                         'EVRE AC001', 'EVRE DC001', 'IEC_60309', 'GBT', 'CCS',
                         'battery_swapping', 'TYPE 2 AC', 'DC001', 'CCS-2', 'TYPE - 2 (AC)',
                         'CCS (DC)', 'CHAdeMO (DC)', 'IEC AC', 'GB/T'],
        'power_type': ['DC', 'AC']
    }
