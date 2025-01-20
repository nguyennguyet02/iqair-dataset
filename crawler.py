from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import json

def crawl_iqair():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to IQAir Hanoi page
        url = "https://www.iqair.com/vietnam/hanoi"
        page.goto(url)
        
        # Wait for content to load
        page.wait_for_selector(".aqi-value__estimated")
        
        # Extract data
        aqi = page.query_selector(".aqi-value__estimated").text_content()
        weather_icon = page.query_selector(".air-quality-forecast-container-weather__icon").get_attribute("src")
        wind_speed = page.query_selector(".air-quality-forecast-container-wind__label").text_content()
        humidity = page.query_selector(".air-quality-forecast-container-humidity__label").text_content()
        
        # Create data dictionary
        data = {
            "timestamp": datetime.now().isoformat(),
            "aqi": aqi.strip(),
            "weather_icon": weather_icon,
            "wind_speed": wind_speed.strip(),
            "humidity": humidity.strip()
        }
        
        # Close browser
        browser.close()
        
        return data

if __name__ == "__main__":
    try:
        data = crawl_iqair()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
