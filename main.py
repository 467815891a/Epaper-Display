#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
import psutil
import requests
import json
import textwrap
from w1thermsensor import W1ThermSensor
from Waveshare_Epaper_UART import EPaper
from Waveshare_Epaper_UART import Handshake
from Waveshare_Epaper_UART import SetStorageMode
from Waveshare_Epaper_UART import RefreshAndUpdate
from Waveshare_Epaper_UART import DrawLine
from Waveshare_Epaper_UART import DisplayText
from Waveshare_Epaper_UART import DisplayImage
from Waveshare_Epaper_UART import SetCurrentDisplayRotation
from Waveshare_Epaper_UART import SetPallet
from Waveshare_Epaper_UART import SetEnFontSize
from Waveshare_Epaper_UART import SetZhFontSize
from Waveshare_Epaper_UART import ClearScreen

city = '合肥'  #这里指定天气预报的城市
serial_port = '/dev/ttyS1'  #定义串口

paper=EPaper(serial_port)

def connected_to_internet(url):
    try:
        _ = requests.get(url, timeout=2)
        return True
    except:
        return False

class Weather:
    def __init__(self, query_city=city):
        __appid = '36145716'  # 修改为你的用户 ID
        __appsecret = 'p7JhIabx'  # 修改为你的用户 密钥
        self.url = f"https://www.tianqiapi.com/api/?version=v1&city={query_city}&appid={__appid}&appsecret={__appsecret}"

    def get_weather(self):
        __ret = requests.get(self.url)
        __ret.encoding = 'utf-8'
        self.weather_dict = json.loads(__ret.text)

    def display_weather(self):
        weather_x = 0
        weather_y = 170
        paper.send(DrawLine(weather_x + 4 * 120 , weather_y , weather_x + 4 * 120 , 397))
        paper.send(SetEnFontSize(SetZhFontSize.THIRTYTWO))
        paper.send(DisplayText(weather_x + 4 * 120 + 5 , weather_y , (u'户外空气：'+ str(self.weather_dict['data'][0]['air']) +'  ' + self.weather_dict['data'][0]['air_level']).encode("GB18030")))
        paper.send(DisplayText(weather_x + 4 * 120 + 5 , weather_y + 35 , (u'户外温度：'+ self.weather_dict['data'][0]['tem']).encode("GB18030")))
        for i in range(4):
            for key, val in self.weather_dict.items():
                paper.send(DisplayText(weather_x + 28 + i*120 ,weather_y, (str(self.weather_dict['data'][i]['date'])[-2:] + u'日').encode("GB18030")))
                weather = str(self.weather_dict['data'][i]['wea']).split(u'转',1)
                if weather[0].find('晴') != -1 :
                    w_bmp = 'SUNNY.BMP'
                elif weather[0].find('多云')  != -1 :
                    w_bmp = 'CLOUDY.BMP'
                elif weather[0].find('尘')  != -1 :
                    w_bmp = 'DUST.BMP'
                elif weather[0].find('雾')  != -1 :
                    w_bmp = 'FROG.BMP'
                elif weather[0].find('霾')  != -1 :
                    w_bmp = 'HAZE.BMP'
                elif weather[0].find('阴')  != -1 :
                    w_bmp = 'CAST.BMP'
                elif weather[0].find('沙')  != -1 :
                    w_bmp = 'SAND.BMP'
                elif weather[0].find('雨夹雪')  != -1 :
                    w_bmp = 'SLEET.BMP'
                elif weather[0].find('小雨')  != -1 :
                    w_bmp = 'RAINL.BMP'
                elif weather[0].find('中雨')  != -1 :
                    w_bmp = 'RAINM.BMP'
                elif weather[0].find('大雨')  != -1 :
                    w_bmp = 'RAINH.BMP'
                elif weather[0].find('阵雨')  != -1 :
                    w_bmp = 'SHOWR.BMP'
                elif weather[0].find('暴雨')  != -1 :
                    w_bmp = 'STROM.BMP'
                elif weather[0].find('小雪')  != -1 :
                    w_bmp = 'SNOWL.BMP'
                elif weather[0].find('中雪')  != -1 :
                    w_bmp = 'SNOWL.BMP'
                elif weather[0].find('大雪')  != -1 :
                    w_bmp = 'SNOWH.BMP'
                elif weather[0].find('暴雪')  != -1 :
                    w_bmp = 'SNOWHH.BMP'
                elif weather[0].find('雷')  != -1 :
                    w_bmp = 'THUN.BMP'
                else :
                    w_bmp = 'CAST.BMP'
                paper.send(DisplayImage(weather_x + 20 + i*120 ,weather_y+35, w_bmp.encode("GB18030")))
                paper.send(DisplayText(weather_x + 60 - round(len(weather[0])/2*32) + i*120 ,weather_y+115, weather[0].encode("GB18030")))
                if len(weather) > 1:
                    paper.send(DisplayText(weather_x + 60 - round(len(weather[1])/2*32) + i*120 ,weather_y+150, weather[1].encode("GB18030")))
                tempture = str(self.weather_dict['data'][i]['tem2'])[:-1] + u'~' + str(self.weather_dict['data'][i]['tem1'])
                paper.send(DisplayText(weather_x + 60 - round(len(tempture)/2*16) + i*120 ,weather_y+190, tempture.encode("GB18030")))     


def update_timedate():
    clock_x = 5
    clock_y = 5
    temp_x = 0
    time_now = datetime.datetime.now()
    time_str = time_now.strftime('%H:%M')
    date_str = time_now.strftime('%Y年%m月%d日')
    weekday_dict = {0 : '星期一',1 : '星期二',2 : '星期三',3 : '星期四',4 : '星期五',5 : '星期六',6 : '星期天',}
    weekday_str = weekday_dict[time_now.weekday()]
    paper.send(SetZhFontSize(SetEnFontSize.FOURTYEIGHT))
    for c in time_str:
        n_bmp = 'N{}.BMP'.format('UMS' if c == ':' else c)
        paper.send(DisplayImage(clock_x + temp_x, clock_y, n_bmp.encode("GB18030")))
        temp_x += 60 if c == ':' else 91
    paper.send(DisplayText(clock_x + 450 , clock_y , date_str.encode("GB18030")))
    paper.send(DisplayText(clock_x + 450 , clock_y + 50, weekday_str.encode("GB18030")))
    paper.send(DrawLine(0, clock_y + 159, 800, clock_y + 159))
    paper.send(DrawLine(0, clock_y + 160, 800, clock_y + 160))

    TheDay = datetime.date(2020,0o5,21)
    Today  = datetime.date.today()
    cntdown = (TheDay - Today).days
    paper.send(SetZhFontSize(SetEnFontSize.SIXTYFOUR))
    paper.send(DisplayText(clock_x + 450  + 200, clock_y + 90, str(cntdown).encode("GB18030")+u'天'.encode("GB18030")))
    paper.send(SetEnFontSize(SetZhFontSize.THIRTYTWO))
    paper.send(DisplayText(clock_x + 450  , clock_y + 110, u'距离生日还有'.encode("GB18030")))

def update_sysinfo():
    paper.send(DrawLine(0, 399, 800, 399))
    paper.send(DrawLine(0, 398, 800, 398))
    paper.send(DrawLine(245, 400, 245, 600))
    CPU_temp = round(int(os.popen('cat /sys/class/thermal/thermal_zone0/temp | head -1').readline().replace("\n", ''))/1000,1)
    CPU_usage = psutil.cpu_percent()
    DISK_total = round(psutil.disk_usage('/').total/1024/1024/1024, 1)
    DISK_used = round(psutil.disk_usage('/').used/1024/1024/1024, 1)
    RAM_total = int(psutil.virtual_memory().total/1024/1024)
    RAM_used = int(psutil.virtual_memory().used/1024/1024)
    RSSI= os.popen('iwconfig wlan0 | grep "Signal level"').readline().split('=')[-1].replace("\n", '')
    paper.send(SetEnFontSize(SetZhFontSize.THIRTYTWO))
    paper.send(DisplayText(5, 410, (u'CPU温度:' + str(CPU_temp)+ '℃').encode("GB18030")))
    paper.send(DisplayText(5, 460, (u'CPU占用:' + str(CPU_usage) + '%  ').encode("GB18030")))
    paper.send(DisplayImage(5, 510, (u'RAM.BMP').encode("GB18030")))
    paper.send(DisplayText(60, 510, (str(RAM_used) + 'MB' + '/' + str(RAM_total) + 'MB').encode("GB18030")))
    paper.send(DisplayImage(5, 560, (u'DISK.BMP').encode("GB18030")))
    paper.send(DisplayText(60, 560, (str(DISK_used) + 'GB'  + '/' + str(DISK_total) + 'GB').encode("GB18030")))
    paper.send(DisplayText( 4 * 120 + 5 , 275 , (u'WiFi强度：' + RSSI).encode("GB18030")))
    paper.send(DisplayText( 4 * 120 + 5 , 315 , (u'当前网络状态').encode("GB18030")))

class Quotes():
    def get_quotes(self):
        __url = "http://open.iciba.com/dsapi/"
        __r = requests.get(__url)
        __eng = __r.json()['content']
        __cn = __r.json()['note']
        self.__english = textwrap.wrap(__eng,width=43)
        if len(__eng) <= 129 and len(__cn) <= 34:
            self.__chinese = textwrap.wrap(__cn,width=17)
        else:
            self.__chinese = None

    def display_quotes(self):
        paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        for i in range(len(self.__english)):
            paper.send(DisplayText(255,410 + i*35, self.__english[i].encode("GB18030")))
        if self.__chinese is not None:
            for j in range(len(self.__chinese)):
                paper.send(DisplayText(250,455 + i*35 + j*35 , self.__chinese[j].encode("GB18030")))


def update_sensor():
    try:
        sensor = W1ThermSensor()
        temperature = sensor.get_temperature()
        InDoor_tempture = str(temperature) + u'℃'
        paper.send(DisplayText( 4 * 120 + 5 , 170 + 70 , ((u'室内温度：') + InDoor_tempture).encode("GB18030")))
    except:
        paper.send(DisplayText( 4 * 120 + 5 , 170 + 70 , ((u'室内温度：') + (u'暂无数据')).encode("GB18030")))

def Display_init():
    paper.send(Handshake())
    paper.send(ClearScreen())
    paper.send(SetStorageMode(SetStorageMode.TF_MODE))
    paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.NORMAL))
    paper.send(SetPallet(SetPallet.BLACK, SetPallet.WHITE))
    paper.read_responses()
    update_timedate()
    update_sysinfo()
    update_sensor()
    if connected_to_internet('http://connect.rom.miui.com/generate_204') == True :
        paper.send(DisplayImage(690, 310, (u'NETY.BMP').encode("GB18030")))
        weather.get_weather()
        weather.display_weather()
        quotes.get_quotes()
        quotes.display_quotes()
    else :
        paper.send(DisplayImage(690, 310, (u'NETN.BMP').encode("GB18030")))
    if connected_to_internet('http://clients3.google.com/generate_204') == True :
        paper.send(DisplayImage(745, 310, (u'WWWY.BMP').encode("GB18030")))
    else :
        paper.send(DisplayImage(745, 310, (u'WWWN.BMP').encode("GB18030")))
    paper.send(RefreshAndUpdate())
        
if __name__ == '__main__':
    weather=Weather(city)
    quotes=Quotes()
    Display_init()
    last_update_time = datetime.datetime.now()
    time.sleep(1)
    while True:
        while time.strftime("%S") != '00' :
            time.sleep(1)
        paper.send(ClearScreen())
        paper.send(DisplayText(4 * 120 + 5 , 360 , (u'最新更新于'+str((datetime.datetime.now()-last_update_time).seconds//60)+u'分钟前').encode("GB18030")))
        if connected_to_internet('http://connect.rom.miui.com/generate_204') == True :
            paper.send(DisplayImage(690, 310, (u'NETY.BMP').encode("GB18030")))
            if time.strftime("%M") == '00' :
                last_update_time = datetime.datetime.now()
                weather.get_weather()
                quotes.get_quotes()
        else :
             paper.send(DisplayImage(690, 310, (u'NETN.BMP').encode("GB18030")))
        if connected_to_internet('http://clients3.google.com/generate_204') == True :
            paper.send(DisplayImage(745, 310, (u'WWWY.BMP').encode("GB18030")))
        else :
             paper.send(DisplayImage(745, 310, (u'WWWN.BMP').encode("GB18030")))
        update_timedate()
        update_sysinfo()
        update_sensor()
        weather.display_weather()
        quotes.display_quotes()
        paper.send(RefreshAndUpdate())
        time.sleep(1)
