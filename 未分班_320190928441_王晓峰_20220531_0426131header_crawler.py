

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from openpyxl import load_workbook
import time



browser = webdriver.Chrome()
url = "http://njwlwz.gov.cn/Mail/Allemail.aspx?MailBox=%u6240%u6709%u4fe1%u7bb1&Manager=%25&ShowTitle=1&MailType=%25&Title=%25&Sender=%25&ID=%25&Mobile=%25&Open=1"


browser.get(url)
resp = browser.page_source  ##网页源代码

##print (resp)

page_number= re.compile(r'<span id="ctl00_ContentPlaceHolder1_SmailSearch1_GridView1_ctl23_LabelPageCount">(?P<page_num>.*?)</span>',re.S)
page_number1=page_number.finditer(resp)    ###页码数量


for it in page_number1:
    x_all=it.group("page_num")  ##总的页数
print("the total page number is ",x_all)

l = 1
#f= open("header_crawler_data.xlsx",mode="w+",encoding="utf-8-sig",newline="")   ##打开文件,若没有文件则创建文件并且写入
#csvwriter = csv.writer(f)
workbook = load_workbook(filename="header_crawler_data.xlsx")
sheet = workbook.active
header_title = ('classification','time','title','send_name','receive_name','answer_name','state')  ##头部标题
str1 = 'A' + str(l)
str2 = 'B' + str(l)
str3 = 'C' + str(l)
str4 = 'D' + str(l)
str5 = 'E' + str(l)
str6 = 'F' + str(l)
str7 = 'G' + str(l)
sheet[str1].value = header_title[0]
sheet[str2].value = header_title[1]
sheet[str3].value = header_title[2]
sheet[str4].value = header_title[3]
sheet[str5].value = header_title[4]
sheet[str6].value = header_title[5]
sheet[str7].value = header_title[6]
workbook.save(filename="header_crawler_data.xlsx")
#csvwriter.writerow(header_title)

##解析数据


for i in range(0,int(x_all)):
        ###等待页面加载完成
        try:

            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_SmailSearch1_GridView1_ctl23_btnGo"]'))
            )

        except:
            time.sleep(2)

        obj = re.compile(
             r'<td style="width:35px;">(?P<classification>.*?)</td>.*?<td style="width:80px;">(?P<time>.*?)</td>.*?target="_parent">(?P<title>.*?)</a>.*?<td align="center">(?P<send_name>.*?)</td>.*?'
             r'target="_self">(?P<receive_name>.*?)</a>.*?<td align="center">(?P<answer_name>.*?)</td>.*?<td style="width:55px;">(?P<state>.*?)</td>',
             re.S)
      ##开始匹配
        result = obj.finditer(resp)



        for it in result:
            dict = it.groupdict()

            #dict["time"] = dict["time"].strip()
            #csvwriter.writerow(dict.values())
            l += 1
            str1 = 'A' + str(l)
            str2 = 'B' + str(l)
            str3 = 'C' + str(l)
            str4 = 'D' + str(l)
            str5 = 'E' + str(l)
            str6 = 'F' + str(l)
            str7 = 'G' + str(l)
            sheet[str1].value = dict.get('classification')
            sheet[str2].value = dict.get('time')
            sheet[str3].value = dict.get('title')
            sheet[str4].value = dict.get('send_name')
            sheet[str5].value = dict.get('receive_name')
            sheet[str6].value = dict.get('answer_name')
            sheet[str7].value = dict.get('state')
        if i%100 == 0:
            workbook.save(filename="header_crawler_data.xlsx")




        print("the {} page is done".format(i+1))  ##输出当前完成页码
         ###点击跳转下一页
        try:
            next_xpath = '//*[@id="ctl00_ContentPlaceHolder1_SmailSearch1_GridView1"]/tbody/tr[22]/td/table/tbody/tr/td[4]'
            next_page = browser.find_element(By.XPATH, next_xpath)

            next_page.click()  ##点击操作

            resp = browser.page_source
        except:
            workbook.save(filename="header_crawler_data.xlsx")



workbook.save(filename="header_crawler_data.xlsx")


print("The crawler is  over!")
browser.close()   ##关闭网页