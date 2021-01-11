#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
import glob
import requests
import json
import textwrap
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
serial_port = '/dev/ttyATH0'  #定义串口

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

    def get_weather_img(self,weather_desc):
        if weather_desc.find('晴') != -1 :
            w_bmp = 'SUNNY.BMP'
        elif weather_desc.find('多云')  != -1 :
            w_bmp = 'CLOUDY.BMP'
        elif weather_desc.find('尘')  != -1 :
            w_bmp = 'DUST.BMP'
        elif weather_desc.find('雾')  != -1 :
            w_bmp = 'FROG.BMP'
        elif weather_desc.find('霾')  != -1 :
            w_bmp = 'HAZE.BMP'
        elif weather_desc.find('阴')  != -1 :
            w_bmp = 'CAST.BMP'
        elif weather_desc.find('沙')  != -1 :
            w_bmp = 'SAND.BMP'
        elif weather_desc.find('雨夹雪')  != -1 :
            w_bmp = 'SLEET.BMP'
        elif weather_desc.find('小雨')  != -1 :
            w_bmp = 'RAINL.BMP'
        elif weather_desc.find('中雨')  != -1 :
            w_bmp = 'RAINM.BMP'
        elif weather_desc.find('大雨')  != -1 :
            w_bmp = 'RAINH.BMP'
        elif weather_desc.find('阵雨')  != -1 :
            w_bmp = 'SHOWR.BMP'
        elif weather_desc.find('暴雨')  != -1 :
            w_bmp = 'STROM.BMP'
        elif weather_desc.find('小雪')  != -1 :
            w_bmp = 'SNOWL.BMP'
        elif weather_desc.find('中雪')  != -1 :
            w_bmp = 'SNOWL.BMP'
        elif weather_desc.find('大雪')  != -1 :
            w_bmp = 'SNOWH.BMP'
        elif weather_desc.find('暴雪')  != -1 :
            w_bmp = 'SNOWHH.BMP'
        elif weather_desc.find('雷')  != -1 :
            w_bmp = 'THUN.BMP'
        else :
            w_bmp = 'CAST.BMP'
        return w_bmp

    def display_oneday_weather(self,x,y,day):
        if str(self.weather_dict['data'][day]['day']).find(u'今天') != -1 :
            date = '今天'
        elif str(self.weather_dict['data'][day]['day']).find(u'明天') != -1 :
            date = '明天'
        elif str(self.weather_dict['data'][day]['day']).find(u'后天') != -1 :
            date = '后天'
        else :
            date = str(self.weather_dict['data'][day]['date'])[-2:] + '日'
        paper.send(DisplayText(x -30 ,y, date.encode("GBK")))
        weather = str(self.weather_dict['data'][day]['wea']).split('转',1)
        paper.send(DisplayImage(x -40 ,y+35, self.get_weather_img(weather[0]).encode("GBK")))
        paper.send(DisplayText(x  - round(len(weather[0])/2*32) , y+115, weather[0].encode("GBK")))
        if len(weather) > 1 :
            paper.send(DisplayText(x - round(len(weather[1])/2*32) ,y+150, weather[1].encode("GBK")))
        tempture = str(self.weather_dict['data'][day]['tem2'])[:-1] + '~' + str(self.weather_dict['data'][day]['tem1'])
        paper.send(DisplayText(x - round(len(tempture)/2*16) ,y+190, tempture.encode("GBK")))

    def display_weather(self):
        weather_x = 240
        weather_y = 170
        try:
            paper.send(SetEnFontSize(SetZhFontSize.THIRTYTWO))
            paper.send(DisplayText(5 , 405 , ('户外空气：'+ str(self.weather_dict['data'][0]['air']) + '  ' + self.weather_dict['data'][0]['air_level']).encode("GBK")))
            paper.send(DisplayText(5 , 440 , ('户外温度：'+ self.weather_dict['data'][0]['tem']).encode("GBK")))
            paper.send(DisplayText(130 , weather_y , ('小时预报：').encode("GBK")))
            for i in range(len(self.weather_dict['data'][0]['hours'])) :
                paper.send(DisplayText(150 , weather_y+40+i*35 , (self.weather_dict['data'][0]['hours'][i]['day'])[-3:].encode("GBK")))
                paper.send(DisplayText(220 , weather_y+40+i*35 , (self.weather_dict['data'][0]['hours'][i]['wea']).encode("GBK")))
                if i==4 :
                    break
            self.display_oneday_weather(70,weather_y,0)
            paper.send(DrawLine(weather_x + 63, 161, weather_x + 63,397))
            for i in range(1,5,1) :
                self.display_oneday_weather(weather_x+i*125,weather_y,i)
        except:
            paper.send(SetEnFontSize(SetZhFontSize.SIXTYFOUR))
            paper.send(DisplayText(weather_x , weather_y , ('暂无数据').encode("GBK")))

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
        paper.send(DisplayImage(clock_x + temp_x, clock_y, n_bmp.encode("GBK")))
        temp_x += 60 if c == ':' else 91
    paper.send(DisplayText(clock_x + 450 , clock_y , date_str.encode("GBK")))
    paper.send(DisplayText(clock_x + 450 , clock_y + 50, weekday_str.encode("GBK")))
    paper.send(DrawLine(0, clock_y + 159, 800, clock_y + 159))
    paper.send(DrawLine(0, clock_y + 160, 800, clock_y + 160))
    TheDay = datetime.date(2020,12,0o4)
    Today  = datetime.date.today()
    cntdown = (TheDay - Today).days
    paper.send(SetZhFontSize(SetEnFontSize.SIXTYFOUR))
    paper.send(DisplayText(clock_x + 450  + 200, clock_y + 90, (str(cntdown)+'天').encode("GBK")))
    paper.send(SetEnFontSize(SetZhFontSize.THIRTYTWO))
    paper.send(DisplayText(clock_x + 450  , clock_y + 110, '距离生日还有'.encode("GBK")))

class Quotes:
    def get_quotes(self):
        __url = "http://open.iciba.com/dsapi/"
        __r = requests.get(__url)
        __eng = __r.json()['content']
        __cn = __r.json()['note']
        self.eng_wrap = textwrap.wrap(__eng,width=45)
        if len(__eng) <= 155 and len(__cn) <= 32:
            self.cn_wrap = textwrap.wrap(__cn,width=16)
        else:
            self.cn_wrap = None

    def display_quotes(self):
        paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
        for i in range(len(self.eng_wrap)):
            paper.send(DisplayText(260,410 + i*35, self.eng_wrap[i].encode("GBK","ignore")))
        if self.cn_wrap is not None:
            for j in range(len(self.cn_wrap)):
                paper.send(DisplayText(260,455 + i*35 + j*35 , self.cn_wrap[j].encode("GBK","ignore")))

def update_sensor():
    paper.send(DrawLine(0, 399, 800, 399))
    paper.send(DrawLine(0, 398, 800, 398))
    paper.send(DrawLine(255, 400, 255, 600))
    paper.send(SetEnFontSize(SetEnFontSize.THIRTYTWO))
#    RSSI= os.popen('iwconfig wlan0 | grep "Signal level"').readline().split('=')[-1].replace(" \n", '')
#    paper.send(DisplayText( 5 , 510 , ('WiFi强度: ' + RSSI).encode("GBK")))
    paper.send(DisplayText( 5 , 550 , ('网络状态').encode("GBK")))
    try:
        sensor = glob.glob('/sys/bus/w1/devices/' + '28*')[0] + '/w1_slave'
        DS18B20 = open(sensor)
        temperature_raw = DS18B20.read()
        DS18B20.close()
        temperature = round(float(temperature_raw.split("t=")[1])/1000.0,1)
        InDoor_tempture = str(temperature) + u'℃'
        paper.send(DisplayText( 5 , 475 , (('室内温度: ') + InDoor_tempture).encode("GBK")))
    except:
        paper.send(DisplayText( 5 , 475 , (('室内温度: ') + ('暂无')).encode("GBK")))

def EPaper_init():
    paper.send(Handshake())
    paper.send(ClearScreen())
    paper.send(SetStorageMode(SetStorageMode.TF_MODE))
    paper.send(SetCurrentDisplayRotation(SetCurrentDisplayRotation.NORMAL))
    paper.send(SetPallet(SetPallet.BLACK, SetPallet.WHITE))
    paper.read_responses()

def RefreshAll():
    paper.send(ClearScreen())
    if connected_to_internet('http://connect.rom.miui.com/generate_204') == True :
        if time.strftime("%M") == '00' :
            weather.get_weather()
            quotes.get_quotes()
        paper.send(DisplayImage(145, 550, ('NETY.BMP').encode("GBK")))
    else :
        paper.send(DisplayImage(145, 550, ('NETN.BMP').encode("GBK")))
    if connected_to_internet('http://clients3.google.com/generate_204') == True :
        paper.send(DisplayImage(195, 550, ('WWWY.BMP').encode("GBK")))
    else :
        paper.send(DisplayImage(195, 550, ('WWWN.BMP').encode("GBK")))
    update_timedate()
    update_sensor()
    weather.display_weather()
    quotes.display_quotes()
    paper.send(RefreshAndUpdate())

if __name__ == '__main__':
    os.system("stty -F "+serial_port+" raw speed 115200")
    paper=EPaper(serial_port)
    weather=Weather(city)
    quotes=Quotes()
    EPaper_init()
    quotes.get_quotes()
    weather.get_weather()
    while True:
        while time.strftime("%S") != '00' :
            time.sleep(1)
        RefreshAll()