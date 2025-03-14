from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import csv
import os
import pathlib
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional
import re
# Define cities data
CITIES = [
    {
        "name": "hanoi",
        "display_name": "Hà Nội",
        "url": "https://www.iqair.com/vi/vietnam/hanoi/hanoi"
    },
    {
        "name": "ho-chi-minh-city",
        "display_name": "Hồ Chí Minh",
        "url": "https://www.iqair.com/vi/vietnam/ho-chi-minh-city/ho-chi-minh-city"
    },
    {
        "name": "da-nang",
        "display_name": "Đà Nẵng",
        "url": "https://www.iqair.com/vi/vietnam/da-nang/da-nang"
    },
    {
        "name": "hai-phong",
        "display_name": "Hải Phòng",
        "url": "https://www.iqair.com/vietnam/thanh-pho-hai-phong/haiphong"
    },
    {
        "name": "nha-trang",
        "display_name": "Nha Trang",
        "url": "https://www.iqair.com/vi/vietnam/khanh-hoa/nha-trang"
    },
    {
        "name": "can-tho",
        "display_name": "Cần Thơ",
        "url": "https://www.iqair.com/vi/vietnam/thanh-pho-can-tho/can-tho"
    },
    {
        "name": "hue",
        "display_name": "Huế",
        "url": "https://www.iqair.com/vietnam/tinh-thua-thien-hue/hue"
    },
    {
        "name": "vinh",
        "display_name": "Vinh",
        "url": "https://www.iqair.com/vi/vietnam/tinh-nghe-an/vinh"
    },
    {
        "name": "thai-nguyen",
        "display_name": "Thái Nguyên",
        "url": "https://www.iqair.com/vi/vietnam/tinh-thai-nguyen/thai-nguyen"
    },
    {
        "name": "hai-duong",
        "display_name": "Hải Dương",
        "url": "https://www.iqair.com/vi/vietnam/tinh-hai-duong/hai-duong"
    },
    {
        "name": "bac-ninh",
        "display_name": "Bắc Ninh",
        "url": "https://www.iqair.com/vi/vietnam/tinh-bac-ninh/bac-ninh"
    },
    {
        "name": "tra-vinh",
        "display_name": "Trà Vinh",
        "url": "https://www.iqair.com/vi/vietnam/tinh-tra-vinh/tra-vinh"
    }
]

def get_vietnam_time():
    """Get current time in Vietnam timezone (GMT+7)"""
    return datetime.now(ZoneInfo("Asia/Bangkok"))  # Bangkok uses GMT+7 like Vietnam


def validate_aqi(aqi: str) -> Optional[str]:
    """Validate AQI value"""
    try:
        # Remove any non-digit characters and convert to int
        aqi_value = int(re.sub(r'\D', '', aqi))
        if 0 <= aqi_value <= 500:  # Valid AQI range
            return str(aqi_value)
    except (ValueError, TypeError):
        pass
    return None

def validate_weather_icon(icon: str) -> Optional[str]:
    """Validate weather icon URL"""
    if icon and isinstance(icon, str) and icon.startswith('/dl/web/weather/'):
        return icon
    return None

def validate_wind_speed(speed: str) -> Optional[str]:
    """Validate wind speed"""
    try:
        # Check if matches pattern like "10.2 km/h" or "8.5 mph"
        if re.match(r'^\d+(\.\d+)?\s*(km/h|mph)$', speed.strip()):
            # Convert mph to km/h if needed
            speed = speed.strip()
            if 'mph' in speed:
                # Extract numeric value
                value = float(re.match(r'^\d+(\.\d+)?', speed).group())
                # Convert to km/h (1 mile = 1.60934 kilometers)
                km_value = value * 1.60934
                return f"{km_value:.1f} km/h"
            return speed
    except (ValueError, TypeError, AttributeError):
        pass
    return None

def validate_humidity(humidity: str) -> Optional[str]:
    """Validate humidity"""
    try:
        # Check if matches pattern like "39%"
        if re.match(r'^\d{1,3}%$', humidity.strip()):
            return humidity.strip()
    except (ValueError, TypeError, AttributeError):
        pass
    return None

def validate_temperature(temp: str) -> Optional[str]:
    """Validate temperature value (convert from Fahrenheit to Celsius if needed)"""
    try:
        # Remove any non-digit characters and convert to float
        temp_value = float(re.sub(r'[^\d.-]', '', temp))

        # Check if the temperature is abnormally high (likely in Fahrenheit)
        if temp_value > 50:  # IQAir có thể dùng Fahrenheit
            temp_value = (temp_value - 32) * 5 / 9  # Chuyển đổi từ F sang C

        # Kiểm tra khoảng hợp lệ (-50°C đến 50°C)
        if -50 <= temp_value <= 50:
            return f"{temp_value:.1f}°C"  # Format as Celsius

    except (ValueError, TypeError):
        pass
    return None

def validate_pollutant(value: str) -> Optional[str]:
    """Validate pollutant value"""
    try:
        # Loại bỏ ký tự không phải số và chuyển đổi thành float
        cleaned_value = re.sub(r'[^\d.]', '', value)
        if not cleaned_value:
            return None
        value_float = float(cleaned_value)
        if 0 <= value_float <= 10000:  # Ngưỡng hợp lý
            return f"{value_float:.1f}"
    except (ValueError, TypeError):
        pass
    return None

def crawl_city_data(page, city: Dict) -> Optional[Dict]:
    """Crawl data for a specific city"""
    print(f"\nAccessing {city['display_name']} ({city['url']})...")
    
    try:
        page.goto(city['url'])
        page.wait_for_selector(".aqi-value__estimated")

        # Extract AQI & Weather Data
        aqi_raw = page.query_selector(".aqi-value__estimated").text_content()
        weather_icon_raw = page.query_selector(".air-quality-forecast-container-weather__icon").get_attribute("src")
        wind_speed_raw = page.query_selector(".air-quality-forecast-container-wind__label").text_content()
        humidity_raw = page.query_selector(".air-quality-forecast-container-humidity__label").text_content()
        temperature_raw = page.query_selector(".air-quality-forecast-container-weather__label").text_content()

        # Validate all fields
        aqi = validate_aqi(aqi_raw)
        weather_icon = validate_weather_icon(weather_icon_raw)
        wind_speed = validate_wind_speed(wind_speed_raw)
        humidity = validate_humidity(humidity_raw)
        temperature = validate_temperature(temperature_raw)

        # Trích xuất danh sách chất ô nhiễm từ trang web
        pollutant_labels = page.query_selector_all(".card-wrapper-info__title")
        pollutant_values = page.query_selector_all(".measurement-wrapper__value")

        pollutant_data = {}
        
        if pollutant_labels and pollutant_values:
            labels = [label.text_content().strip() for label in pollutant_labels if label]
            values = [value.text_content().strip().replace("*", "") for value in pollutant_values if value]
            
            print("Pollutant Labels:", labels)
            print("Pollutant Values:", values)
            
            for label, value in zip(labels, values):
                pollutant_name = label.lower()
                pollutant_value = validate_pollutant(value)

                # Ánh xạ tên chất ô nhiễm
                pollutant_map = {
                    "pm2.5": "pm25",
                    "pm10": "pm10",
                    "o₃": "o3",
                    "no₂": "no2",
                    "so₂": "so2",
                    "co": "co"
                }
                pollutant_key = pollutant_map.get(pollutant_name, pollutant_name)

                pollutant_data[pollutant_key] = pollutant_value

        # Chỉ thêm "N/A" nếu không tìm thấy dữ liệu
        all_pollutants = ["pm25", "pm10", "o3", "no2", "so2", "co"]
        for p in all_pollutants:
            if p not in pollutant_data:
                pollutant_data[p] = "N/A"

        # Trả về dữ liệu hoàn chỉnh
        return {
            "timestamp": get_vietnam_time().isoformat(),
            "city": city['display_name'],
            "aqi": aqi,
            "weather_icon": weather_icon,
            "wind_speed": wind_speed,
            "humidity": humidity,
            "temperature": temperature,
            **pollutant_data
        }

    except Exception as e:
        print(f"Error extracting data for {city['display_name']}: {str(e)}")
        return None



def save_to_csv(data: Dict, city_name: str):
    """Save data to CSV file for a specific city"""
    now = get_vietnam_time()
    result_dir = pathlib.Path(f"result/{city_name}")
    result_dir.mkdir(parents=True, exist_ok=True)
    
    # Create filename based on current month
    filename = f"aqi_{city_name}_{now.year}_{now.strftime('%b').lower()}.csv"
    filepath = result_dir / filename
    
    # Define CSV headers
    headers = ["timestamp", "city", "aqi", "weather_icon", "wind_speed", "humidity", "temperature", "pm25", "pm10","o3","no2", "so2", "co"]
    
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

def crawl_all_cities():
    """Crawl data for all cities"""
    results = []
    for city in CITIES:
        print(f"\n{'='*50}")
        print(f"Processing {city['display_name']}...")
        try:
            with sync_playwright() as p:
                try:
                    # Launch new browser for each city
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    
                    # Set viewport size for better rendering
                    page.set_viewport_size({"width": 1280, "height": 720})
                    
                    # Add small delay for stability
                    page.set_default_timeout(15000)  # 15 seconds timeout
                    
                    data = crawl_city_data(page, city)
                    if data:  # Only process valid data
                        results.append(data)
                        # Save to CSV
                        csv_file = save_to_csv(data, city['name'])
                        print(f"Data saved to: {csv_file}")
                    else:
                        print(f"Skipping invalid data for {city['display_name']}")
                
                except Exception as e:
                    print(f"Browser error for {city['display_name']}: {str(e)}")
                    continue
                
                finally:
                    if 'browser' in locals():
                        browser.close()
        
        except Exception as e:
            print(f"Playwright error for {city['display_name']}: {str(e)}")
            continue
            
    return results

if __name__ == "__main__":
    try:
        print("Starting IQAir data crawler...")
        print(f"Current time in Vietnam: {get_vietnam_time().strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        results = crawl_all_cities()
        
        print("\nCrawled data:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise e
