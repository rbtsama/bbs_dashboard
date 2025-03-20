import os
import urllib.request

# 确保目录存在
font_dir = os.path.join("data", "config", "fonts")
os.makedirs(font_dir, exist_ok=True)

# 下载字体文件
font_url = "https://raw.githubusercontent.com/matomo-org/travis-scripts/master/fonts/SimHei.ttf"
font_path = os.path.join(font_dir, "SimHei.ttf")

print(f"开始下载字体文件: {font_url}")
try:
    urllib.request.urlretrieve(font_url, font_path)
    print(f"字体文件已下载到: {font_path}")
except Exception as e:
    print(f"下载字体文件时出错: {e}") 