import sys
from backend.app.services.aqi_service import AqiService
from backend.app.main import app

def test_service():
    print("Testing AqiService...")
    stations = AqiService.get_stations()
    assert len(stations) > 0, "No stations returned"
    print(f"Stations count: {len(stations)}")
    
    current = AqiService.get_current_aqi("delhi-anand-vihar")
    assert current.aqi > 0, "AQI should be positive"
    assert current.is_demo_data is True, "Demo data flag should be True"
    print(f"Current AQI for {current.station.name}: {current.aqi} ({current.category.value})")
    print(f"Prominent Pollutant: {current.prominent_pollutant}")
    print(f"PM2.5: {current.pollutants['PM2.5'].value} {current.pollutants['PM2.5'].unit}")
    
    forecast = AqiService.get_forecast("delhi-anand-vihar")
    assert len(forecast.forecast_24h) == 24, "Should return 24 hours of forecast"
    print(f"Forecast hours: {len(forecast.forecast_24h)}")
    print(f"Peak window: {forecast.peak_aqi_window}")
    print("Service tests passed successfully!")

if __name__ == "__main__":
    test_service()
