import os
from ipaddress import ip_address, IPv6Address, IPv4Address
from PIL import Image, ImageDraw, ImageFont
from requests_html import HTMLSession
import time
import requests
from requests.adapters import HTTPAdapter

icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets/image/icons')


class WeatherManager(object):
    # 高德key
    amapKey = "4260a258fe3640778a76adcdeccda588"

    # 和风key
    qWeatherKey = "cfad7e010122476bbf94b6183f8904ec"

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.network = requests.Session()
        self.network.mount('http://', HTTPAdapter(max_retries=3))
        self.network.mount('https://', HTTPAdapter(max_retries=3))

    def parse_city(self, locationDic: dict) -> str:
        city = "中国"
        if "province" in locationDic:
            city = locationDic["province"]
            if "district" in locationDic:
                city = city + " " + locationDic["district"]
        return city

    def parse_location(self, locationDic: dict) -> str:
        location = ""
        if "location" in locationDic:
            location = locationDic["location"]
        return location

    def load_location_dic(self) -> dict:
        locationDic = {}
        try:
            ip = self.qurey_ip_address()
            print(ip + " are ip v4  = " + self.are_ip_v4(ip).__str__())
            parameters = {
                "key": self.amapKey,
                "ip": ip,
                "type": 4 if self.are_ip_v4(ip) else 6,

            }
            r = self.network.get("https://restapi.amap.com/v5/ip", params=parameters, verify=False,timeout=10)
            locationDic = r.json()
            print("get_location_dic : " + r.text)
        except:
            print("get_location_dic : exception ")
            pass

        return locationDic

    def qurey_ip_address(self):
        ip = ""
        try:
            ip = self.network.get("http://ifconfig.me/ip", timeout=1).text.strip()
        except:
            ip = ""
            pass
        if not (self.are_ip_v4(ip) or self.are_ip_v6(ip)):
            try:
                ip = self.network.get("http://icanhazip.com", timeout=1).text.strip()
            except:
                ip = ""
                pass
        # 默认北京
        if not (self.are_ip_v4(ip) or self.are_ip_v6(ip)):
            ip = "222.129.0.11"
        print("get_ip_address : " + ip)
        return ip

    def are_ip_v4(self, ip: str) -> bool:
        try:
            return isinstance(ip_address(ip), IPv4Address)
        except ValueError:
            return False

    def are_ip_v6(self, ip: str) -> bool:
        try:
            return isinstance(ip_address(ip), IPv6Address)
        except ValueError:
            return False

    def load_weather_city_info(self, location: str) -> dict:
        data = {}
        try:
            parameters = {
                "key": self.qWeatherKey,
                "location": location
            }
            r = self.network.get("https://geoapi.qweather.com/v2/city/lookup", params=parameters, verify=False)
            data = r.json()
            print("get_weather_city_info : " + r.text)
        except:
            pass
        return data

    def parse_location_id(self, weatherCityDic) -> str:
        locationId = ""
        if "location" in weatherCityDic:
            location = weatherCityDic["location"]
            if len(location) > 0 and "id" in location[0]:
                locationId = location[0]["id"]
        return locationId

    def load_cur_weather(self, locationId) -> dict:
        data = {}
        try:
            parameters = {
                "key": self.qWeatherKey,
                "location": locationId
            }
            r = self.network.get("https://devapi.qweather.com/v7/weather/now", params=parameters, verify=False,timeout=10)
            data = r.json()
            print("get_cur_weather : " + r.text)
        except:
            pass
        return data

    def load_cur_indices(self, locationId) -> dict:
        data = {}
        try:
            parameters = {
                "key": self.qWeatherKey,
                "location": locationId,
                "type": "8"
            }
            r = self.network.get("https://devapi.qweather.com/v7/indices/1d", params=parameters, verify=False,timeout=10)
            data = r.json()
            print("load_cur_indices : " + r.text)
        except:
            pass
        return data

    # 获取当前的天气描述，有可能是失效
    def get_cur_desc(self, locationId) -> str:
        session = HTMLSession()
        response = session.get("https://www.qweather.com/weather/new-territories-" + locationId +".html")
        element = response.html.find('div.current-abstract', first=True)
        if element == None:
            return ""
        print("load_cur_desc : " + element.text)
        return element.text



    def parse_cur_temperature(self, weatherDic) -> str:
        temperature = None
        if "now" in weatherDic and "temp" in weatherDic["now"]:
            temperature = weatherDic["now"]["temp"] + "°"
        return temperature

    def parse_cur_weather_text(self, weatherDic) -> str:
        weatherText = None
        if "now" in weatherDic and "text" in weatherDic["now"]:
            weatherText = weatherDic["now"]["text"]
        return weatherText

    def parse_cur_weather_icon(self, weatherDic) -> Image:
        weather_ic = None
        if "now" in weatherDic and "icon" in weatherDic["now"]:
            weather_ic = weatherDic["now"]["icon"]
        print("parse_cur_weather_icon : " + weather_ic)
        return self.handle_weather_icon(weather_ic + ".png")

    def parse_cur_indices(self, weatherDic) -> str:
        if ("daily" not in weatherDic) or (len(weatherDic["daily"]) == 0):
            return ""
        todayWeatherDic = weatherDic["daily"][0]
        if "text" not in todayWeatherDic:
            return ""
        return todayWeatherDic["text"]

    def load_3d_weather(self, locationId) -> dict:
        data = {}
        try:
            parameters = {
                "key": self.qWeatherKey,
                "location": locationId
            }
            r = self.network.get("https://devapi.qweather.com/v7/weather/3d", params=parameters, verify=False,timeout=10)
            data = r.json()
            print("load_3d_weather : " + r.text)
        except:
            pass
        return data

    def parse_3d_temperatures(self, weatherDic) -> ():
        if ("daily" not in weatherDic) or (len(weatherDic["daily"]) <= 1):
            return None
        tomorrowWeatherDic = weatherDic["daily"][1]
        tempMax = tomorrowWeatherDic["tempMax"]
        tempMin = tomorrowWeatherDic["tempMin"]

        return (tempMin, tempMax)

    def parse_tomorrow_weather_icon(self, weatherDic) -> Image:
        if ("daily" not in weatherDic) or (len(weatherDic["daily"]) <= 1):
            return ""
        tomorrowWeatherDic = weatherDic["daily"][1]
        if "iconDay" not in tomorrowWeatherDic:
            return ""
        iconDay = tomorrowWeatherDic["iconDay"]
        return self.handle_weather_icon(iconDay+".png")

    def parse_tomorrow_date(self, weatherDic) -> str:
        if ("daily" not in weatherDic) or (len(weatherDic["daily"]) <= 1):
            return ""
        tomorrowWeatherDic = weatherDic["daily"][1]
        if "fxDate" not in tomorrowWeatherDic:
            return ""
        iconDay = tomorrowWeatherDic["fxDate"]
        return iconDay

    # 二值化
    def handle_weather_icon(self, icon_name):
        if icon_name == None:
            return None
        weather_ic = Image.open(os.path.join(icon_dir, icon_name))
        ic = weather_ic.load()
        for w in range(0, 65):
            for h in range(0, 65):
                r, g, b, a = ic[w, h]
                if a == 0:
                    r = g = b = 255
                ic[w, h] = (r, g, b, 255)
        return weather_ic
