from anvil.tools.registry import tool
from pydantic import BaseModel, Field

class GetWeatherParams(BaseModel):
    city: str = Field(description="City name")

@tool(params_schema=GetWeatherParams)
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"It's sunny in {city}."

result = get_weather.execute(city="Karachi")
print(result)
print("It worked!")