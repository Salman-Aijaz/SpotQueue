from fastapi import HTTPException
from app.core.config import settings
import httpx
import re

async def get_distance(user_latitude: float, user_longitude: float):
    origin = f"{settings.FIXED_COORDINATES[0]},{settings.FIXED_COORDINATES[1]}"
    destination = f"{user_latitude},{user_longitude}"

    api_key = settings.DISTANCE_MATRIX_API_KEY
    url = f"https://api.distancematrix.ai/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={api_key}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        if data["status"] == "OK":
            distance_text = data["rows"][0]["elements"][0]["distance"]["text"]
            duration_text = data["rows"][0]["elements"][0]["duration"]["text"]  

            distance_value =  float(re.search(r"[\d.]+", distance_text).group()) 
            duration_value = int(re.search(r"\d+", duration_text).group())

            return duration_value, distance_value
        else:
            raise HTTPException(status_code=500, detail="Error fetching distance data.")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to the distance matrix service: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching distance data: {e.response.text}")
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing distance data: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")    
