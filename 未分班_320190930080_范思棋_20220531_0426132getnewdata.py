import time  # 便于观察爬取耗时
import pandas as pd
from pachong import getAllUrl, getAllInfo
import os


def getnewdata(pastinfo):
    """
    1、从第一页开始爬取url
    2、判断url是否包括在历史数据中，即是否为新url
    3、新url获取完毕后，开是爬取问政数据
    4、结果存入newdata.xlsx中
    :param pastinfo:参数为导入的dataFrame类型的历史数据
    :return: info:返回更新的所有记录

    """

    flag = 1
    i = 1
    urls = []  # 存放新的url

    while flag:
        URLS = getAllUrl(i, i + 1)  # 获取第i页的所有url
        for url in URLS:  # 循环判断是否为新url
            c = pastinfo['编号'].astype(str).str.contains(url[63:])
            if not any(c):  # 如果c全为false，即旧文件不包含该url
                urls.append(url)
            else:  # 旧文件中包含该url->跳出循环结束更新
                flag = 0
        i = i + 1

    info = getAllInfo(urls)  # 爬取
    t = time.asctime()[4:].replace(':', '-')
    info.to_excel('newdata' + t + '.xlsx')
    print('增加了{0}条数据到newdata{1}.xlsx中'.format(len(urls), t))
    return info


def main():
    print('正在读取历史数据...')
    past_info = pd.read_excel('result.xlsx')  # past_info是dataframe类型的历史数据
    print('历史数据读取完毕')
    new_info = getnewdata(past_info)  # new_info是dataframe类型的新数据
    result = pd.concat([new_info, past_info])
    print('新旧数据合并完毕')
    os.remove("result.xlsx")  # 删除旧数据
    result.to_excel('result.xlsx')  # 将新旧合并好的重新写回result里面
    print('新数据追加到result中完毕')


if __name__ == "__main__":
    main()
