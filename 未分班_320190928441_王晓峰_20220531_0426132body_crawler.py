from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from openpyxl import load_workbook
import csv
import re

browser = webdriver.Chrome()
url = "http://njwlwz.gov.cn/Mail/Allemail.aspx?MailBox=%u6240%u6709%u4fe1%u7bb1&Manager=%25&ShowTitle=1&MailType=%25&Title=%25&Sender=%25&ID=%25&Mobile=%25&Open=1"

browser.get(url)

resp = browser.page_source  ##第一页的页面源代码

page_number = re.compile(
    r'<span id="ctl00_ContentPlaceHolder1_SmailSearch1_GridView1_ctl23_LabelPageCount">(?P<page_num>.*?)</span>', re.S)
page_number1 = page_number.finditer(resp)  ###页码数量

for it in page_number1:
    x_all = it.group("page_num")
print("the total page number is :",x_all)  ###页码数量


def get_href(resp):  ###获得超链接，跳转页面列表
    soup = BeautifulSoup(resp, 'html.parser')  # BeautifulSoup中的方法
    num = 1
    list_href = []
    list_1 = []
    for link in soup.find_all('a'):  # 遍历网页中所有的超链接（a标签）
        if (num % 2 != 0):
            list_href.append(link.get('href'))
        num = num + 1

    list_1 = ['http://njwlwz.gov.cn' + str(i) for i in list_href]  ##http://njwlwz.gov.cn   链接前缀
    list_2 = list_1

    number_number = len(list_1)-3

    ###删除字符串里的‘..’
    for i in range(0, number_number):
        if '..' in list_1[i]:
            list_2[i] = list_1[i].replace('..', '')
    return list_2


list_main = get_href(resp)
length = len(list_main) - 3  ##由于最后定位时有3 个会添加到列表当中 减去



l = 1

workbook = load_workbook(filename="body_crawler_data.xlsx")
sheet = workbook.active
header_title = ('ask_name','ask_time','ask_body','answer_name','answer_time','answer_body')  ##头部标题
str1 = 'A' + str(l)
str2 = 'B' + str(l)
str3 = 'C' + str(l)
str4 = 'D' + str(l)
str5 = 'E' + str(l)
str6 = 'F' + str(l)
sheet[str1].value = header_title[0]
sheet[str2].value = header_title[1]
sheet[str3].value = header_title[2]
sheet[str4].value = header_title[3]
sheet[str5].value = header_title[4]
sheet[str6].value = header_title[5]
workbook.save(filename="body_crawler_data.xlsx")





numm = 0
page_add = 1  ###用来计算页数爬取多少

while numm < length:
    js = 'window.open("' + str(list_main[numm]) + '");'
    numm += 1
    ##print(js)

    # 打开窗口
    browser.execute_script(js)
    # print(browser.page_source)

    # 得到所有的句柄，和主要的句柄
    handle_main = browser.current_window_handle
    handle_all = browser.window_handles
    # 在所有的句柄中找到需要的句柄
    for handle in handle_all:
        if handle != handle_main:
            handle_now = handle
    browser.switch_to.window(handle_now)

    # 在新的窗口中进行爬取
    # print(browser.page_source)

    content_title1 = 'I1'
    content1 = browser.find_element(By.ID, content_title1)
    browser.switch_to.frame(content1)

    try:##因为有两种不同的XPATH定位
        ask_name = browser.find_element(By.XPATH,
                                        '//*[@id="ctl00_ContentPlaceHolder1_ctl_MailView1_DetailsView1_Label_UserName"]').text
        ask_time = browser.find_element(By.XPATH,
                                        '//*[@id="ctl00_ContentPlaceHolder1_ctl_MailView1_DetailsView1_Label_AddDate"]').text
        ask_body = browser.find_element(By.XPATH,
                                        '//*[@id="ctl00_ContentPlaceHolder1_ctl_MailView1_DetailsView1_Label_Content"]').text
        answer_name = browser.find_element(By.XPATH,
                                           '//*[@id="ctl00_ContentPlaceHolder1_ctl_MailView1_GridView1_ctl02_Label_UserName"]').text
        answer_time = browser.find_element(By.XPATH,
                                           '//*[@id="ctl00_ContentPlaceHolder1_ctl_MailView1_GridView1_ctl02_Label3"]').text
        answer_body = browser.find_element(By.XPATH,
                                           '//*[@id="ctl00_ContentPlaceHolder1_ctl_MailView1_GridView1"]/tbody/tr[2]/td/table/tbody/tr[2]/td').text
    except:
        ask_name = browser.find_element(By.XPATH,
                                        '//*[@id="ctl00_ContentPlaceHolder1_MailShow1_DetailsView1_Label_UserName"]').text
        ask_time = browser.find_element(By.XPATH,
                                        '//*[@id="ctl00_ContentPlaceHolder1_MailShow1_DetailsView1_Label_AddDate"]').text
        ask_body = browser.find_element(By.XPATH,
                                        '//*[@id="ctl00_ContentPlaceHolder1_MailShow1_DetailsView1_Label_Content"]').text
        answer_name = browser.find_element(By.XPATH,
                                           '//*[@id="ctl00_ContentPlaceHolder1_MailShow1_GridView1_ctl02_Label_UserName"]').text
        answer_time = browser.find_element(By.XPATH,
                                           '//*[@id="ctl00_ContentPlaceHolder1_MailShow1_GridView1_ctl02_Label3"]').text
        answer_body = browser.find_element(By.XPATH,
                                           '//*[@id="ctl00_ContentPlaceHolder1_MailShow1_GridView1_ctl02_Label_AnswerContent"]').text



    # print(browser.page_source)

    # 内容获得



    dict_1 = {'ask_name': ask_name, 'ask_time': ask_time, 'ask_body': ask_body, 'answer_name': answer_name,
              'answer_time': answer_time, 'answer_body': answer_body}

    l += 1
    str1 = 'A' + str(l)
    str2 = 'B' + str(l)
    str3 = 'C' + str(l)
    str4 = 'D' + str(l)
    str5 = 'E' + str(l)
    str6 = 'F' + str(l)

    sheet[str1].value = dict_1.get('ask_name')
    sheet[str2].value = dict_1.get('ask_time')
    sheet[str3].value = dict_1.get('ask_body')
    sheet[str4].value = dict_1.get('answer_name')
    sheet[str5].value = dict_1.get('answer_time')
    sheet[str6].value = dict_1.get('answer_body')






    # csvwriter.writerow(dict_1.values())  ###写入文件里面
    # print(ask_name, ask_time)
    # print(ask_body)
    # print(answer_name, answer_time)
    # print(answer_body)

    ##关闭handle_now 窗口
    browser.close()
    ## 切换会handle_main 窗口
    browser.switch_to.window(handle_main)

    if numm == length:

        ##进行判断是否到截至页码数
        if page_add == 2:  ###截至爬取多少页
            workbook.save(filename="body_crawler_data.xlsx")

            print("the {} page is done".format(page_add))  ##输出当前完成页码
            break
        else:
            print("the {} page is done".format(page_add))  ##输出当前完成页码
            page_add += 1

        if page_add % 100 ==0:
            workbook.save(filename="body_crawler_data.xlsx")  ##每一百页保存一次

        numm = 0
        try:
            next_xpath = '//*[@id="ctl00_ContentPlaceHolder1_SmailSearch1_GridView1"]/tbody/tr[22]/td/table/tbody/tr/td[4]'
            next_page = browser.find_element(By.XPATH, next_xpath)
            next_page.click()
            list_main = get_href(browser.page_source)
            length = len(list_main) - 3
        except:
            workbook.save(filename="body_crawler_data.xlsx")



##关闭所有窗口
browser.close()
print("The crawler is  over!")
