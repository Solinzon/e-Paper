import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "main"))

from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from datetime import date
from PIL import Image, ImageDraw, ImageFont
import logging
import time

from cn2an import cn2an, an2cn
from lunar_python import Lunar, Solar
from lunar_python.util import HolidayUtil

# pip3 install requests
# pip3 install cn2an
# pip3 install pillow
# pip3 install requests-html
# matplotlib、pandas、tqdm、lunar_python
# APScheduler

# 墨水屏依赖
from waveshare_epd import epd7in5_V2
from main.utils.weather_manager import WeatherManager
from main.utils.text_utils import WordWrap
from main.utils.paragraph_manager import ParagraphManager

logging.basicConfig(level=logging.DEBUG,
                    filemode='w', format='%(levelname)s:%(asctime)s:%(message)s', datefmt='%Y-%d-%m %H:%M:%S')

font_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/font')
image_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/image')
icon_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/image/icons')

font12_light = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Light.ttc"), 12)
font14 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 14)
font14_bold = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Bold.ttc"), 14)
font18 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 18)
font18_bold = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Bold.ttc"), 18)
font20 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 20)
font24 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 24)
font24_bold = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Bold.ttc"), 24)
font144 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 140)


class CalendarPainter(object):
    # 内边距
    padding = 10
    # 文字行高
    line_h = 4

    # 日历部分宽高
    calendar_w = 540
    calendar_h = 360

    # 天气部分宽高
    weather_w = 260
    weather_h = 360

    # 文字部分宽高
    tips_w = 800
    tips_h = 120

    allow_draw_calendar = False
    allow_draw_weather = False
    allow_draw_tips = False

    def __init__(self):
        # 给个默认值
        self.canvas = Image.new('1', (800, 480), 255)
        self.draw = ImageDraw.Draw(self.canvas)

    def start(self):
        self.draw_all_job()
        scheduler = BackgroundScheduler()
        # 每天 00:00:10 更新日历
        scheduler.add_job(self.draw_calendar_job, "cron", day_of_week="0-6", hour=00, minute=00, second=10)
        # 每隔一个小时更新天气
        scheduler.add_job(self.draw_weather_job, "interval", hours=1)
        # 每天 00:10:10 更新tips
        scheduler.add_job(self.draw_tips_job, "cron", day_of_week="0-6", hour=00, minute=10, second=10)
        # 每天 08:30:30 更新所有
        # 每天 18:30:30 更新所有
        scheduler.add_job(self.draw_all_job, "cron", day_of_week="0-6", hour=8, minute=30, second=30)
        scheduler.add_job(self.draw_all_job, "cron", day_of_week="0-6", hour=18, minute=30, second=30)
        scheduler.start()

    def draw_all_job(self):
        self.toggle(draw_calendar=True, draw_weather=True, draw_tips=True)
        self.paint()
        self.toggle()

    def draw_calendar_job(self):
        self.toggle(draw_calendar=True)
        self.paint()
        self.toggle()

    def draw_weather_job(self):
        self.toggle(draw_weather=True)
        self.paint()
        self.toggle()

    def draw_tips_job(self):
        self.toggle(draw_tips=True)
        self.paint()
        self.toggle()

    def toggle(self, draw_calendar=False, draw_weather=False, draw_tips=False):
        self.allow_draw_calendar = draw_calendar
        self.allow_draw_weather = draw_weather
        self.allow_draw_tips = draw_tips

    def paint(self):
        self.init_canvas()
        self.draw_divider()
        self.draw_calendar()
        self.draw_weather()
        self.draw_tips()
        # self.print_img()
        self.print_to_screen()
        logging.debug("执行完毕")

    # 初始化画布、画笔
    def init_canvas(self):
        logging.debug("init_canvas")
        # 创建画布
        self.canvas = Image.new('1', (800, 480), 255)
        self.draw = ImageDraw.Draw(self.canvas)

    # 画分割线， 将屏幕分成3部分
    def draw_divider(self):
        logging.debug("draw_divider")
        self.draw.line((self.padding, self.calendar_h, 800 - self.padding, self.calendar_h), fill=0, width=1)
        self.draw.line((self.calendar_w, self.padding, self.calendar_w, self.calendar_h), fill=0, width=1)

    # 画日历部分
    def draw_calendar(self):
        if self.allow_draw_calendar != True:
            return
        # 画日期、农历、节日
        weeks = ["周一", "周二", "周三", "周四", "周五", "周六", "周日", ]
        cur_weeks = weeks[time.localtime(time.time())[6]]
        date_str = time.strftime("%Y/%m/%d ", time.localtime()) + cur_weeks
        self.draw.text((self.padding, self.padding), date_str, font=font18_bold, fill=0)
        cur_date = date.fromtimestamp(time.time())
        solar = Solar.fromYmd(cur_date.year, cur_date.month, cur_date.day)
        lunar = solar.getLunar()
        lunar_date_str = lunar.getYearInGanZhi() + "(" + lunar.getYearShengXiao() + ")年 " + lunar.getMonthInChinese() + "月" + lunar.getDayInChinese() + "日"
        self.draw.text((self.padding, self.padding + 20 + self.line_h), lunar_date_str, font=font14, fill=0)
        if cur_date.month == 3 and cur_date.day == 23:
            self.draw.text((self.padding, self.padding + 20 + self.line_h + 14 + self.line_h),
                           an2cn((cur_date.year - 2013).__str__()) + "年纪念日",
                           font=font14,
                           fill=0)
        else:
            holiday = HolidayUtil.getHoliday(cur_date.year, cur_date.month, cur_date.day)
            if holiday != None:
                self.draw.text((self.padding, self.padding + 20 + self.line_h + 14 + self.line_h), holiday.getName(),
                               font=font14,
                               fill=0)
        # 画今天是哪天
        calendar_center_x = self.calendar_w / 2
        calendar_center_y = self.calendar_h / 2
        day = time.strftime("%d", time.localtime())
        day_w, day_h = font144.getsize(day)
        day_x = calendar_center_x - day_w / 2
        day_y = calendar_center_y - day_h / 2
        self.draw.text((day_x, day_y), day, font=font144, fill=0)
        days = (datetime.datetime(cur_date.year, cur_date.month, cur_date.day) - datetime.datetime(2013, 3,
                                                                                                   23)).days + 1
        self.draw.text((calendar_center_x + day_w / 2 + 20, calendar_center_y + 60), "在一起的第" + days.__str__() + "天",
                       font=font12_light,
                       fill=0)

    def draw_weather(self):
        if self.allow_draw_weather != True:
            return
        logging.debug("draw_weather")
        # 准备数据
        # 定位数据，来自高德
        location_dic = WeatherManager().load_location_dic()
        # 城市，精确到区
        city = WeatherManager().parse_city(location_dic)
        # 经纬度
        location = WeatherManager().parse_location(location_dic)
        # 城市信息
        weather_City_Info = WeatherManager().load_weather_city_info(location)
        # location id , 用于获取天气
        locationId = WeatherManager().parse_location_id(weather_City_Info)
        # 获取现在天气信息
        cur_weather_dic = WeatherManager().load_cur_weather(locationId)

        # 获取3天的天气信息
        three_day_weather_dic = WeatherManager().load_3d_weather(locationId)
        logging.debug("city = " + city + ", location = " + location + " , locationId = " + locationId)
        if len(city) == 0 or len(location) == 0 or len(locationId) == 0:
            return False
        # 当前温度
        cur_temperature = WeatherManager().parse_cur_temperature(cur_weather_dic)
        # 当前气候
        cur_weather_text = WeatherManager().parse_cur_weather_text(cur_weather_dic)
        cur_weather_icon = WeatherManager().parse_cur_weather_icon(cur_weather_dic)

        # 明天的最高、最低气温
        tomorrow_temp_min, tomorrow_temp_max = WeatherManager().parse_3d_temperatures(three_day_weather_dic)
        tomorrow_icon = WeatherManager().parse_tomorrow_weather_icon(three_day_weather_dic)
        # 明天的日期
        tomorrow_date = WeatherManager().parse_tomorrow_date(three_day_weather_dic)

        # 天气指数
        today_indices_dic = WeatherManager().load_cur_indices(locationId)
        today_in_dices = WeatherManager().parse_cur_indices(today_indices_dic)

        cur_weather_desc = WeatherManager().get_cur_desc(locationId)

        cur_desc = cur_weather_desc if len(cur_weather_desc) > 0 else today_in_dices

        zero_x = self.calendar_w
        zero_y = 0
        # 画城市
        self.draw.text((zero_x + self.padding, zero_y + self.padding), city, font=font18_bold, fill=0)
        # 今日温度
        cur_weather_center_x = zero_x + self.weather_w / 2
        cur_weather_center_y = zero_y + self.weather_h / 2
        cur_weather_ic_w, cur_weather_ic_h = 65, 65
        if cur_temperature == None or cur_weather_text == None:
            return False
        cur_weather_h, cur_weather_w = font24_bold.getsize(cur_temperature)
        gap = 10
        offset = (cur_weather_w + cur_weather_ic_w + gap) / 2
        offset_y = int(cur_weather_center_y - cur_weather_ic_h)
        self.canvas.paste(cur_weather_icon.resize(
            (cur_weather_ic_w, cur_weather_ic_h)),
            (int(cur_weather_center_x - offset),
             offset_y - 8))
        self.draw.text((cur_weather_center_x + offset - cur_weather_w, offset_y),
                       cur_temperature, font=font24_bold, fill=0)

        self.draw.text((cur_weather_center_x + offset - cur_weather_w, cur_weather_center_y - cur_weather_ic_h / 2),
                       cur_weather_text,
                       font=font14, fill=0)
        # 气温描述
        cur_desc_w, cur_desc_h = font14.getsize(cur_desc)

        if cur_desc_w < self.weather_w - self.padding * 2:
            self.draw.text((cur_weather_center_x - cur_desc_w / 2, cur_weather_center_y + cur_weather_h), cur_desc,
                           font=font14,
                           fill=0)
        else:
            WordWrap().draw_text(xy=(zero_x + self.padding, cur_weather_center_y + cur_weather_h), text=cur_desc,
                                 font=font14,
                                 draw=self.draw, width=self.weather_w - 26)

        # 明天预报
        if tomorrow_temp_max == None or tomorrow_temp_min == None:
            return False

        self.draw.text((zero_x + self.padding, 310), "明天", font=font14_bold, fill=0)
        self.draw.text((zero_x + self.padding, 310 + 20), tomorrow_date, font=font14, fill=0)
        tomorrow_weather_w, tomorrow_weather_h = 40, 40
        self.canvas.paste(tomorrow_icon.resize((tomorrow_weather_w, tomorrow_weather_h)),
                          (cur_weather_center_x.__int__() - (tomorrow_weather_w / 2).__int__(), 310))
        temp_text = tomorrow_temp_min + "°" + " ~ " + tomorrow_temp_max + "°"
        self.draw.text((zero_x + 180, 310 + 10), temp_text, font=font14, fill=0)

    def draw_tips(self):
        if self.allow_draw_tips != True:
            return
        zero_x = 0
        zero_y = self.calendar_h
        self.draw.text((zero_x + self.padding, zero_y + self.padding - 4), "ONE · 一个", font=font18_bold, fill=0)
        # 最多100字 ，70字最佳
        data = ParagraphManager().get_paragraph()
        tips = data.get("content")
        source = data.get("from")
        if (len(tips) > 70):
            tips = "树梢间泻下的秋日阳光，在她肩部一闪一闪地跳跃着。"
            source = "挪威的森林"
        source = " -- 「 " + source + " 」"
        source_w, source_h = font20.getsize(source)
        line_count, y = WordWrap().draw_text(xy=(zero_x + self.padding, zero_y + 35), text=tips,
                                             font=font20,
                                             draw=self.draw, width=self.tips_w - self.padding * 4)
        if line_count < 3:
            # 在line_count的下一行写
            self.draw.text((self.tips_w - self.padding - source_w, y), source, font=font20, fill=0)
        else:
            # 在第3行写
            self.draw.text((self.tips_w - self.padding - source_w, y - source_h), source, font=font20, fill=0)

    # 输出最后的图片
    def print_img(self):
        self.canvas.save("main/assets/image/calendar.png", "png")

    def print_to_screen(self):
        try:
            logging.info("epd7in5_V2 pony pi")
            epd = epd7in5_V2.EPD()
            logging.info("init and Clear")
            epd.init()
            epd.Clear()
            epd.display(epd.getbuffer(self.canvas))
            logging.info("Goto Sleep...")
            epd.sleep()

        except IOError as e:
            logging.info(e)

        except KeyboardInterrupt:
            logging.info("ctrl + c:")
            epd7in5_V2.epdconfig.module_exit()
            exit()


painter = CalendarPainter()
painter.start()
while True:
    time.sleep(1)
