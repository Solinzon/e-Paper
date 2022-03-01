import datetime
import os
from datetime import date

import requests
from PIL import Image, ImageDraw, ImageFont
import logging
import time

from cn2an import cn2an, an2cn
from lunar_python import Lunar, Solar
from lunar_python.util import HolidayUtil

# pip install opencv-python
# pip3 install requests
# pip3 install cn2an
# pip3 install pillow
# matplotlib、pandas、tqdm
from main.utils.text_utils import WordWrap

logging.basicConfig(level=logging.DEBUG,
                    filemode='w', format='%(levelname)s:%(asctime)s:%(message)s', datefmt='%Y-%d-%m %H:%M:%S')

font_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/font')
image_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets/image')

font12_light = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Light.ttc"), 12)
font14 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 14)
font14_bold = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Bold.ttc"), 14)
font18 = ImageFont.truetype(os.path.join(font_dir, "微软雅黑.ttc"), 18)
font18_bold = ImageFont.truetype(os.path.join(font_dir, "微软雅黑Bold.ttc"), 18)
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

    def __init__(self):
        # 给个默认值
        self.canvas = Image.new('1', (800, 480), 255)
        self.draw = ImageDraw.Draw(self.canvas)

    def paint(self):
        self.init_canvas()
        self.draw_divider()
        self.draw_calendar()
        self.draw_weather()
        self.print()

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
        # 画日期、农历、节日
        weeks = ["周一", "周二", "周三", "周四", "周五", "周六", "周日", ]
        cur_weeks = weeks[time.localtime(time.time())[6]]
        date_str = time.strftime("%Y/%m/%d ", time.localtime()) + cur_weeks
        self.draw.text((self.padding, self.padding), date_str, font=font18_bold, fill=0)
        curDate = date.fromtimestamp(time.time())
        solar = Solar.fromYmd(curDate.year, curDate.month, curDate.day)
        lunar = solar.getLunar()
        lunar_date_str = lunar.getYearInGanZhi() + "(" + lunar.getYearShengXiao() + ")年 " + lunar.getMonthInChinese() + "月" + lunar.getDayInChinese() + "日"
        self.draw.text((self.padding, self.padding + 20 + self.line_h), lunar_date_str, font=font14, fill=0)
        if curDate.month == 3 and curDate.day == 23:
            self.draw.text((self.padding, self.padding + 20 + self.line_h + 14 + self.line_h),
                           an2cn((curDate.year - 2013).__str__()) + "年纪念日",
                           font=font14,
                           fill=0)
        else:
            holiday = HolidayUtil.getHoliday(curDate.year, curDate.month, curDate.day)
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
        days = (datetime.datetime(curDate.year, curDate.month, curDate.day) - datetime.datetime(2013, 3, 23)).days + 1
        self.draw.text((calendar_center_x + day_w / 2 + 20, calendar_center_y + 60), "在一起的第" + days.__str__() + "天",
                       font=font12_light,
                       fill=0)

    def draw_weather(self):
        logging.debug("draw_weather")
        zero_x = self.calendar_w
        zero_y = 0
        # 画城市
        self.draw.text((zero_x + self.padding, zero_y + self.padding), "澳门特别行政区", font=font18_bold, fill=0)
        # 今日温度
        weather_center_x = zero_x + self.weather_w / 2
        weather_center_y = zero_y + self.weather_h / 2
        weather_ic_w, weather_ic_h = 65, 65
        today_weather_ic = Image.open(os.path.join(image_dir, "test_weather_ic.png")).resize(
            (weather_ic_w, weather_ic_h)).convert(
            "1")
        today_weather = "11°"
        today_weather_h, today_weather_w = font24_bold.getsize(today_weather)
        offset = (today_weather_w + weather_ic_w) / 2
        self.canvas.paste(today_weather_ic,
                          ((weather_center_x - offset).__int__(), (weather_center_y - weather_ic_h).__int__()))
        self.draw.text((weather_center_x + offset - today_weather_w, weather_center_y - weather_ic_h),
                       today_weather, font=font24_bold, fill=0)
        self.draw.text((weather_center_x + offset - today_weather_w, weather_center_y - weather_ic_h/2), "晴", font=font14, fill=0)
        # 气温描述
        desc = "今晚晴。明天晴，比今天暖和一些（13°），有风, 空气不错。"
        desc_w, desc_h = font14.getsize(desc)
        if desc_w < self.weather_w - self.padding * 2:
            self.draw.text((weather_center_x - desc_w / 2, weather_center_y + today_weather_h), desc, font=font14,
                           fill=0)
        else:
            WordWrap().draw_text(xy=(zero_x + self.padding, weather_center_y + today_weather_h), text=desc, font=font14,
                                 draw=self.draw, width=self.weather_w - 2 * self.padding)
        # 明天预报
        self.draw.text((zero_x + self.padding, 310), "明天", font=font14_bold, fill=0)
        self.draw.text((zero_x + self.padding, 310 + 20), "2022/2/27", font=font14, fill=0)
        tomorrow_weather_w, tomorrow_weather_h = 40, 40
        today_weather_ic = Image.open(os.path.join(image_dir, "test_weather_ic.png")).resize((40, 40)).convert("1")
        self.canvas.paste(today_weather_ic, (weather_center_x.__int__() - (tomorrow_weather_w / 2).__int__(), 310))
        self.draw.text((zero_x + 180, 310 + 10), "1° ~  12°", font=font14, fill=0)

    # 输出最后的图片
    def print(self):
        self.canvas.save('blur.jpg', 'jpeg')


painter = CalendarPainter()
painter.paint()
