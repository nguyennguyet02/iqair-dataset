import pandas as pd
import glob
import os

# Danh sách thành phố bạn muốn lấy dữ liệu
desired_cities = ["hanoi", "thai-nguyen", "ho-chi-minh-city", "tra-vinh","hai-duong", "hue"]  # Thêm "ho-chi-minh" nếu cần

csv_files = glob.glob('result/**/*.csv', recursive=True)

df_list = []
for file in csv_files:
    # Nếu tên file chứa 1 trong các thành phố mong muốn
    if any(city in file for city in desired_cities):
        df = pd.read_csv(file)
        # Tùy ý: Thêm cột city dựa trên tên file
        # city_name = os.path.basename(file).split('_')[1]  # ví dụ cắt chuỗi
        # df['city'] = city_name
        df_list.append(df)

combined_df = pd.concat(df_list, ignore_index=True)
combined_df.to_csv('aqi_selected_cities.csv', index=False)
print("Đã gộp xong các file CSV cho những thành phố chỉ định.")



"""
Nếu gộp tất cả các file CSV trong thư mục result, bạn có thể sử dụng:
import pandas as pd
import glob
import os

# Giả sử bạn đang ở thư mục gốc chứa folder "result"
# Sử dụng pattern 'result/**/*.csv' để quét mọi file CSV trong tất cả thư mục con
csv_files = glob.glob('result/**/*.csv', recursive=True)

# Tạo một list để lưu các DataFrame
df_list = []

for file in csv_files:
    # Đọc từng file CSV
    df = pd.read_csv(file)
    
    # Tuỳ ý: Tự động gắn cột 'city' hoặc 'filename' để biết dữ liệu này từ đâu
    # Lấy tên file hoặc tên folder làm city, ví dụ:
    # city_name = os.path.basename(file).split('_')[1]  # tách chuỗi nếu file có định dạng aqi_ha-noi_2025_jan.csv
    # df['city'] = city_name
    
    df_list.append(df)

# Gộp tất cả DataFrame trong df_list
combined_df = pd.concat(df_list, ignore_index=True)

# Xuất ra 1 file CSV tổng
combined_df.to_csv('aqi_all_cities_2025.csv', index=False)
print("Đã gộp xong tất cả file CSV thành aqi_all_cities_2025.csv")

"""