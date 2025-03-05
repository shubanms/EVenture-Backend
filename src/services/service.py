import os
import dotenv


import pandas as pd


dotenv.load_dotenv()


def get_openrouteservice_key(version: str = 'v1') -> str:
    if version == 'v1':
        return str(os.getenv("openrouteservice_api_key_v1"))
    else:
        return str(os.getenv("openrouteservice_api_key_v2"))
    
def get_foursquare_key() -> str:
    return str(os.getenv("FOUR_SQUARE_API_KEY"))

def get_openai_key() -> str:
    return str(os.getenv("OPENAI_API_KEY"))

def load_dataset(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)
