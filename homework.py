import requests
import asyncio
import aiohttp
from lxml import etree
import re
import sqlite3
import time


# 获取总页数
def get_page(url):
    requests.packages.urllib3.disable_warnings()
    res = requests.get(url,verify=False)
    tree = etree.HTML(res.text)

    p = tree.xpath('/html/body/div/div/ul/li[6]/text()')[0]
    page = re.search(r'共(?P<num>.*?)页',p).group('num')
    return page


# 每次处理100页
async def get_url(page,url,number):
    tasks = []
    async with aiohttp.ClientSession() as session:
        # 每一个url都需要创建一个异步任务
        if number == num + 1:
            for i in range(100 * (number - 1) + 1, int(page)+1):
                s = url+f'&pageNo={i}'
                tasks.append(asyncio.create_task(get_single_url(s,session)))
            await asyncio.wait(tasks)
        else:
            for i in range(100 * (number - 1) + 1, 100 * number):
                s = url+f'&pageNo={i}'
                tasks.append(asyncio.create_task(get_single_url(s,session)))
            await asyncio.wait(tasks)


# 获取一页中的所有数据所在地址
async def get_single_url(url,session):
    async with session.get(url,verify_ssl=False) as res:
        tree = etree.HTML(await res.text())
        try:
            l = tree.xpath('/html/body/div/table')
        except:
            pass
        for i in l:
                data_url.append(i.xpath('./tr/td[1]/a/@href')[0])


# 准备100页中的所有网站
async def get_data(url,conn,name):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for u in data_url:
            s = url.split('zjzw/')[0]+u
            tasks.append(asyncio.create_task((get_single_data(s,session,conn,name))))
        await asyncio.wait(tasks)

# 获取每一页中的数据
async def get_single_data(url,session,conn,name):
    t = 0
    try:
        async with session.get(url,verify_ssl=False) as res:
            tree = etree.HTML(await res.text())
            # xptah路径要去掉tbody
            if (tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[2]/tr/td/text()')==[]): ajmc = ''
            else:ajmc = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[2]/tr/td/text()')[0].strip() # 案件名称

            if (tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[1]/td[3]/text()') == []): return 0
            else:jdswh = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[1]/td[3]/text()')[0].strip() # 决定书文号

            if (tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[2]/td[3]/text()')==[]): bcfr = ''
            else:bcfr = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[2]/td[3]/text()')[0].strip()# 被处罚人

            if (tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[2]/td[3]/text()[2]') == []): dbr = ''
            else:dbr = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[2]/td[3]/text()[2]')[0].strip()# 法定代表人

            if (tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[3]/td[3]/text()')==[]): bm = ''
            else:bm = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[3]/td[3]/text()')[0].strip() # 执法部门

            if (tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[4]/td[3]/text()')==[]): rq = ''
            else:rq = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[3]/tr[4]/td[3]/text()')[0].strip() # 日期


            jds = '' # 决定书
            jds_list = tree.xpath('/html/body/table[2]/tr/td/table/tr/td/table[5]/tr/td/p')
            for j in jds_list:
                if j.xpath('./text()')==[]:continue
                else:
                    jds += j.xpath('./text()')[0]
            jds.strip()

            try:
                conn.execute(f"INSERT INTO message "
                             f"VALUES ('{ajmc}','{jdswh}','{bcfr}','{dbr}','{bm}',"
                             f"'{rq}','{jds}','{name}')")
                conn.commit()
                t+=1
            except sqlite3.IntegrityError :
                pass
            print(jdswh+f'已写入数据库！')
    except:pass
    data = [(ajmc,jdswh,bcfr,dbr,bm,rq,jds,name)]
    return t,data

# 连接数据库
def sqlite():
    conn = sqlite3.connect('data.db')
    print("已成功连接数据库！")

    conn.execute(f'''CREATE TABLE if not exists message
           (案件名称               TEXT,
           行政处罚决定书文号        TEXT primary key, 
           被处罚人                TEXT,
           法定代表人               TEXT,
           执法部门                TEXT,
           作出行政处罚的日期        TEXT,
           行政处罚决定书           TEXT,
           部门                   TEXT);''')
    conn.commit()
    return conn


# 部门名称
name = [
    '市交通运输局', '市经信局', '市建委', '市文广旅游局', '市公安局', '市司法局', '市财政局', '市人力社保局', '市规划和自然资源局', '市住保房管局', '市园文局'
    ,'市农业农村局', '市文广新局', '市卫生健康委员会', '市统计局', '市生态环境局', '市市场监督管理局', '市质监局', '市城管局', '市应急管理局', '市物价局'
    ,'市税务局', '市道路运输管理局', '市港航管理局', '市公路管理局', '市机动车服务管理局', '市消防救援支队', '市交警支队', '市民政局']
# 部门链接
urls = [
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026037&webid=2&xzcf_code=&realid=0.8255545789755162&_=1636633125932',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026007&webid=2&xzcf_code=&realid=0.3577404082916318&_=1636633371491',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026032&webid=2&xzcf_code=&realid=0.5065803488060151&_=1636633382651',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026010&webid=2&xzcf_code=&realid=0.15657670693858605&_=1636633394627',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026015&webid=2&xzcf_code=&realid=0.6185234701709782&_=1636633407139',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026020&webid=2&xzcf_code=&realid=0.4223402780378366&_=1636633417563',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026022&webid=2&xzcf_code=&realid=0.8693176752949735&_=1636633426348',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026026&webid=2&xzcf_code=&realid=0.7107591702867397&_=1636633436420',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026028&webid=2&xzcf_code=&realid=0.49635016837997836&_=1636633446146',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026034&webid=2&xzcf_code=&realid=0.21427752866515404&_=1636633454747',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026035&webid=2&xzcf_code=&realid=0.8073276911858409&_=1636633469131',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026039&webid=2&xzcf_code=&realid=0.29855954315202227&_=1636633484363',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026012&webid=2&xzcf_code=&realid=0.4027931822541688&_=1636633493212',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026017&webid=2&xzcf_code=&realid=0.09595081805069294&_=1636633526875',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026021&webid=2&xzcf_code=&realid=0.044981864014328576&_=1636633537683',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026023&webid=2&xzcf_code=&realid=0.04945371660696052&_=1636633546732',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026025&webid=2&xzcf_code=&realid=0.1980911237181897&_=1636633556547',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026027&webid=2&xzcf_code=&realid=0.42593154879836836&_=1636633570123',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026031&webid=2&xzcf_code=&realid=0.40710264770498994&_=1636633579627',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026033&webid=2&xzcf_code=&realid=0.14351515844515572&_=1636633590083',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026049&webid=2&xzcf_code=&realid=0.8149654088683267&_=1636633604699',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026061&webid=2&xzcf_code=&realid=0.6893757169172627&_=1636633614891',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026092&webid=2&xzcf_code=&realid=0.07588628083660753&_=1636633624651',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026093&webid=2&xzcf_code=&realid=0.28879587207168256&_=1636633634827',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026094&webid=2&xzcf_code=&realid=0.03173935241274983&_=1636633648643',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026095&webid=2&xzcf_code=&realid=0.5681049127488342&_=1636633681299',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026117&webid=2&xzcf_code=&realid=0.1492125717399978&_=1636633690138',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026253&webid=2&xzcf_code=&realid=0.44478763588888837&_=1636633699636',
        'https://www.zjzwfw.gov.cn/zjzw/punish/frontpunish/punish_list.do?deptId=001008001026018&webid=2&xzcf_code=&realid=0.27784264220514854&_=1636633714810']

if __name__ == '__main__':
    for url in urls:
        # 主站网址
        # 获取总页数
        n = name[urls.index(url)]
        print(f'准备爬取市{n}的数据...')
        page = get_page(url)
        print('得到总页数:', page)
        num = int(int(page) / 100)
        conn = sqlite()
        for i in range(1, num + 2):
            data_url = []
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_url(page, url, i))
            print('准备完毕！')
            if (data_url == []):
                break
            loop = asyncio.get_event_loop()
            loop.run_until_complete(get_data(url, conn, n))
            time.sleep(5)
        conn.close()
    print("完成数据爬取")
    # print(f'一共爬取了{total}条数据！')