#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from openpyxl  import load_workbook
import requests
import pickle
import datetime 
import time

def date_count(time1,time2):   #计算当前时间与问政网页的时间差，给了3天的缓冲时间，说明文档有说明逻辑关系。
    time1_year = int(time1[0:4])
    time1_month = int(time1[5:7])
    time1_day = int(time1[8:10])

    time2_year = int(time2[0:4])
    time2_month = int(time2[5:7])
    time2_day = int(time2[8:10])

    d1 = datetime.datetime(time1_year,time1_month,time1_day)   # 第一个日期
    d2 = datetime.datetime(time2_year,time2_month,time2_day)   # 第二个日期
    interval = d2 - d1                   # 两日期差距
    
    return interval.days                 # 具体的天数 

def xget(url):     
    print(url)
    cc = 1
    while True:
        try:
            page = requests.get(url)
            page.encoding = 'utf-8'
            soup = BeautifulSoup(page.text, 'lxml')
            break
        except:
            cc += 2
            print(' get wait',end= '...' )
            time.sleep(cc)
    return soup

def geturls(num1=0,num2=0,urls0=[],now_time0=''):     #获取符合要求的网页
    for x  in  range(num1,num2):
        url = 'http://m.shiyan.gov.cn/zwhd/web/letter/detail.action?letterId={}'.format(x)
        soup0= xget(url)
        wz=soup0.find('div',class_='mess_list')
        if wz!=None:
            wz1=wz.find('table',class_='mess1')
            td = wz1.find_all('td')
            wztime=td[1].find('span',class_='mtp3').text[0:10]
            time_sub=date_count(wztime,now_time0)

            if time_sub >= 3 :
                if '办结回复' in wz.text:
                    urls0.append(url)
    return urls0



def getinfo(xxxurl):      #从问政网页中获得我们需要的信息
    xxx =xget(xxxurl)
    info = []
    tds=[]
    tds1=[]
    a=xxx.find('div',class_='mess_list')
    wh=xxx.find('div',class_='mess_con')
    wt=xxx.find('div',class_='mess')
    rt=a.find_all('div',class_='messp')
    if rt.__len__()==2:
        rt1=rt[1].find('table',class_='mess1')
        rt2=rt[1].find('table',class_='mess2')
        #context=rt.text
        tds=wt.find_all('td')
        tds1=rt2.find_all('td')
    if rt.__len__()==1:
        rt1=rt[0].find('table',class_='mess1')
        rt2=rt[0].find('table',class_='mess2')
        #context=rt.text
        tds=wt.find_all('td')
        tds1=rt2.find_all('td')
    if rt.__len__()!=0:
        info.append(xxxurl)
        info.append(tds[0].find('span').text)
        info.append(tds[1].find('span').text)
        info.append(wh.text)
        info.append(tds[2].find('span').text)
        info.append(tds[3].find('span',class_='mtp2').text)
        info.append(tds[4].find('span',class_='mtp3').text)
        info.append(tds[5].find('span').text)
        info.append(tds[6].find('span',class_='mtp3').text)
        info.append(tds1[0].find('span').text)
        info.append(tds1[1].find('span').text)
        info.append(tds1[2].find('span').text)
        info.append(rt1.text)
    return info