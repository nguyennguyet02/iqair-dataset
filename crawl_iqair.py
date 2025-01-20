from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import csv
import os
import pathlib
from zoneinfo import ZoneInfo

def get_hanoi_time():
    """Get current time in Hanoi timezone (GMT+7)"""
    return datetime.now(ZoneInfo("Asia/Bangkok"))  # Bangkok uses GMT+7 like Hanoi

def crawl_iqair_data():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to IQAir Hanoi page
        url = "https://www.iqair.com/vietnam/hanoi"
        print(f"Accessing {url}...")
        page.goto(url)
        
        # Wait for content to load
        page.wait_for_selector(".aqi-value__estimated")
        
        # Extract data
        aqi = page.query_selector(".aqi-value__estimated").text_content()
        weather_icon = page.query_selector(".air-quality-forecast-container-weather__icon").get_attribute("src")
        wind_speed = page.query_selector(".air-quality-forecast-container-wind__label").text_content()
        humidity = page.query_selector(".air-quality-forecast-container-humidity__label").text_content()
        
        # Create data dictionary with Hanoi time
        current_time = get_hanoi_time()
        data = {
            "timestamp": current_time.isoformat(),
            "aqi": aqi.strip(),
            "weather_icon": weather_icon,
            "wind_speed": wind_speed.strip(),
            "humidity": humidity.strip()
        }
        
        # Close browser
        browser.close()
        
        return data

def save_to_csv(data):
    # Create result directory if not exists
    now = get_hanoi_time()
    result_dir = pathlib.Path("result/hanoi")
    result_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename based on current month
    filename = f"aqi_hanoi_{now.year}_{now.strftime('%b').lower()}.csv"
    filepath = result_dir / filename
    
    # Define CSV headers
    headers = ["timestamp", "aqi", "weather_icon", "wind_speed", "humidity"]
    
    # Check if file exists to determine if we need to write headers
    file_exists = filepath.exists()
    
    with open(filepath, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        
        # Write headers if file is new
        if not file_exists:
            writer.writeheader()
        
        # Write data
        writer.writerow(data)
    
    return filepath

if __name__ == "__main__":
    try:
        print("Starting IQAir data crawler...")
        print(f"Current time in Hanoi: {get_hanoi_time().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        data = crawl_iqair_data()
        
        # Save to CSV
        csv_file = save_to_csv(data)
        print(f"\nData saved to: {csv_file}")
        
        print("\nCrawled data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
