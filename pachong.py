import multiprocessing as mp  # 多进程
import time  # 便于观察爬取耗时
from bs4 import BeautifulSoup
import requests
import pandas as pd
import traceback  # 异常处理

"""
小组成员：范思棋 冯淑杰 高乐天
本小组爬取的是十堰问政数据，网址为http://m.shiyan.gov.cn/zwhd/web/webindex.action
围绕爬虫我们设计了四个函数：
1、获取需要爬取的url:  getAllUrl(start, end) --多进程-->getUrl(page)
2、获取url的详细问政信息:  getAllInfo(URLS)--多进程-->getInfo(i, url)

"""


def getUrl(page):
    """
    获取已办结的网址
    :param page: 需爬取url的页码
    :return: Urls:返回该页的url列表
    """
    Urls = []
    try:
        baseurl = "http://m.shiyan.gov.cn/zwhd/web/webindex.action"
        head = {  # 模拟浏览器头部信息，向服务器发送消息
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40"
        }  # 用户代理：防止反爬虫
        fromdata = {
            'docStatus': 1,
            'page.currentpage': f"{page}"
        }
        request = requests.get(baseurl, headers=head, params=fromdata)
        request.encoding = 'utf-8-sig'
        data = BeautifulSoup(request.text, 'html.parser')

        url_data = data.find('div', class_='alllist').find_all('td', class_='tit3')
        Urls = [r'http://m.shiyan.gov.cn/' + x.a.get('href') for x in url_data]
        print('成功爬取第{0}页中url'.format(page))
    except:
        info = traceback.format_exc()
        print(info)
        print('第{0}页中的url获取失败，报错信息'.format(page))
    return Urls


def getAllUrl(start, end):  # 多进程加速爬取网址
    """
    1、引入进程池
    2、把getUrl（具体的爬取url的函数）丢到进程池里面
    3、从进程池获取到的结果储存在res_l列表中
    4、将res_l中的内容提取出来，存入列表
    :param start: 爬取的开始页数
    :param end: 爬取的结束页数
    :return: res_ls: 列表类型，储存着所有下一步需要爬取的url
    """
    t_start = time.time()

    res_l = []  # 储存进程池中输出的结果
    res_ls = []  # 储存所有url

    po = mp.Pool(22)  # 引入进程池
    for i in range(start, end):
        res = po.apply_async(getUrl, (i,))
        res_l.append(res)
    po.close()  # 关闭进程池，关闭后po不再接收新的请求
    po.join()  # 等待po中的所有子进程执行完成，必须放在close语句之后

    for res in res_l:
        res_ls.extend(res.get())

    t_end = time.time()
    print("\n获取所有url完毕，耗时%0.2f" % (t_end - t_start))
    print("总共%d个网址" % (len(res_ls)))
    print("*****************************************************************")

    return res_ls


def getInfo(i, url):
    """
    1、对于每条url爬取的内容包括：
        编号、提问人、类型、提问时间、浏览次数、受理单位、标题、提问内容、办结回复、回复时间、办理部门
    2、使用traceback 进行异常处理，这样能观察到报错信息
    :param i: 第i条url
    :param url: 第i条url
    :return: dic:结果以字典类型返回
    """
    url_ = []
    number_ = []
    nickname_ = []
    askdate_ = []
    asktype_ = []
    title_ = []
    count_ = []
    unit_ = []
    content_ = []
    answer_ = []
    answerdate_ = []
    administration_ = []

    dic = {'网址': url, '编号': number_, '提问人': nickname_, '类型': asktype_, '提问时间': askdate_, '浏览次数': count_, '受理单位': unit_,
           '标题': title_, '提问内容': content_, '办结回复': answer_, '回复时间': answerdate_, '办理部门': administration_}
    try:
        head = {  # 模拟浏览器头部信息，向服务器发送消息
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36 Edg/95.0.1020.40"
        }  # 用户代理：防止反爬虫
        request = requests.get(url, headers=head)
        request.encoding = 'utf-8-sig'
        data = BeautifulSoup(request.text, 'html.parser')
        # 编号
        number = data.find('td', 'ts1').find_all('span', 'mpt4')
        number = [x.text for x in number][0]
        number_.append(number)
        # 提问人
        nickname = data.find_all('span', 'mtp2')
        nickname = [x.text for x in nickname][0]
        nickname_.append(nickname)
        # 类型
        asktype = data.find('td', 'ts2').find_all('span', 'mpt4')
        asktype = [x.text for x in asktype][0]
        asktype_.append(asktype)
        # 提问时间
        askdate = data.find_all('span', 'mtp3')
        askdate = [x.text for x in askdate][0]
        askdate_.append(askdate)
        # 浏览次数
        count = data.find('td', 'ts3').find_all('span', 'mpt4')
        count = [x.text for x in count][0]
        count_.append(count)
        # 受理单位
        unit = data.find_all('span', 'mtp3')
        unit = [x.text for x in unit][-1]
        unit_.append(unit)
        # 标题
        title = data.find_all('h2')
        title = [x.text for x in title][0]
        title_.append(title)
        # 提问内容
        content = data.find_all('span', 'mpt6')
        content = [x.text for x in content][0]
        content_.append(content)
        # 办结回复
        answer = data.find_all('table', 'mess1')
        answer = [x.text for x in answer][-1]
        answer = answer.replace('\n', '').replace('办结回复：', '')
        answer_.append(answer)
        # 回复时间
        answerdate = data.find_all('td', 'ts3')
        answerdate = [x.text for x in answerdate][-1]
        answerdate = answerdate.replace('回复时间： ', '')
        answerdate_.append(answerdate)
        # 办理部门
        administration_data = data.find_all('span', 'mpt4')
        administration = [x.text for x in administration_data][-3]
        administration_.append(administration)

        url_.append(url)
        dic = {'编号': number_, '提问人': nickname_, '类型': asktype_, '提问时间': askdate_, '浏览次数': count_,
               '受理单位': unit_,
               '标题': title_, '提问内容': content_, '办结回复': answer_, '回复时间': answerdate_, '办理部门': administration_}
        print('成功爬取第{0}条记录'.format(i))

    except:
        info = traceback.format_exc()
        print(url)
        print('第{0}条记录中的内容爬取失败，报错信息'.format(i))
        print(info)

    return dic


def getAllInfo(URLS):  # 多进程加速爬取url的详细问政信息
    """
    1、引入进程池
    2、把getInfo（具体的爬取函数）丢到进程池里面
    3、从进程池获取到的结果储存在res_l列表中
    4、将res_l中的内容提取出来，用concat合并为dataFrame类型
    :param URLS: 列表类型，将所有需要爬取的url传入
    :return: info: 最后所有的数据都会以dataFrame类型储存在里面

    """

    t_start = time.time()
    res_l = []  # 储存进程池中输出的结果

    po = mp.Pool(22)  # 引入进程池
    for i in range(len(URLS)):
        res = po.apply_async(getInfo, (i, URLS[i]))  # getInfo为具体的爬取函数
        res_l.append(res)
    po.close()  # 关闭进程池，关闭后po不再接收新的请求
    po.join()  # 等待po中的所有子进程执行完成，必须放在close语句之后
    print('爬取完毕，开始整合数据...')

    dic = {'编号': [], '提问人': [], '类型': [], '提问时间': [], '浏览次数': [], '受理单位': [],
           '标题': [], '提问内容': [], '办结回复': [], '回复时间': [], '办理部门': []}
    info = pd.DataFrame(dic)

    for res in res_l:
        res_ = pd.DataFrame(res.get())
        info = pd.concat([info, res_])  # 把进程池的结果合并到dataframe里面

    t_end = time.time()
    print("已成功获取所有数据，耗时%0.2f" % (t_end - t_start))

    return info


def main():
    URLS = getAllUrl(1, 8008)  # 爬取范围
    info = getAllInfo(URLS)
    print(info.shape)
    info.to_excel('result.xlsx', engine='xlsxwriter')
    print('文件写入成功')


if __name__ == "__main__":
    main()
