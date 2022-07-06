 
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import pickle
import sys
import logging

#日志配置
logging.basicConfig(filename='run.log',level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

"""

按照信件的时间先后顺序爬取内容
单纯获取页面底部框里面的所有内容，也是整个问政的全部内容

"""
#全局列表，记录已经爬取过的数据，用于数据更新
id_list=[]

def newpet(url):
    '''每条数据的结构'''
    pet = {
        'id':'',
        'title':'',
        'question':'',
        'q_time':'',
        'unit':'',
        'type':'',
        'a_time':'',
        'status':'',
        'answer':'',
        'url': url,
    }
    return pet

def write_to_excel(pet_list,file='./history_data.xlsx'):
    """将内容写入excel表中"""
    zh_CN = [#将列名转化为中文
        '编号',
        '信件标题',
        '询问内容',
        '发布时间',
        '回复部门',
        '类型',
        '回复时间',
        '受理情况',
        '官方回复',
        '链接',
    ]
    print('Writing to history_data.xlsx.')
    print('Waiting. . .')
    df=pd.DataFrame(pet_list)
    df.columns=zh_CN
    df.to_excel(file,index=False)
    print('Success')

def get_soup(url):
    '''请求网页，封装后返回BeautifulSoup对象'''
    cot=0
    while cot<3:
        try:
            page = requests.get(url,timeout=5)
            page.encoding = 'utf-8'
            soup = BeautifulSoup(page.text, 'lxml')
            return soup
        except requests.exceptions.Timeout:
            logging.warning("第"+str(cot+1)+"请求超时："+url)
            cot+=1

    logging.error("获取数据失败")
    print('TIME OUT')
    sys.exit(1)
    

def get_pet_obj(pg_url_list):
    '''获取一个页面的信件列表'''
    pet_list=[]
    cc=0
    for url in pg_url_list:
        cc+=1
        pet_list.extend(parse_url(url))
        print('{:3}{}{}'.format(cc,' /',len(pg_url_list)))
    return pet_list
    
def get_frame_pet_url():#第一步
    '''
    首页的信件展示块,里面包含一些分类里面没有的数据
    url：http://apps.ganzhou.gov.cn/szfwlwzweb/szfbmwz/indexList，
    需要单独处理一下，-> pet_list
    '''
    url='http://apps.ganzhou.gov.cn/szfwlwzweb/szfbmwz/indexList'
    b_url='http://apps.ganzhou.gov.cn/szfwlwzweb/szfbmwz/indexList?pg={}'
    html=requests.get(url)
    totalPage_match=re.search(r'var totalPage =(.*?);',html.text).group(1).strip()
    totalPage=int(totalPage_match)
    print('获取展示块的信件的url和部分内容...')
    pg_url_list=[b_url.format(i) for i in range(1,totalPage+1)]
    return pg_url_list
    


def parse_url(url):#被第二步调用
    '''
    获取信件的url和部分信息 被（get_pet_obj）调用, ->pet_list
    接收参数url形如：http://apps.ganzhou.gov.cn/szfwlwzweb/szfbmwz/renderDeptInfList?deptid=0001360000
    '''
    b_url='http://apps.ganzhou.gov.cn'
    li=get_soup(url).find_all('li')
    pet_list=[]
    for e in li:
        pet_url=b_url+e.a.get('href')
        pet=newpet(pet_url)
        id=e.a.find('span',class_='xinj-id').text
        id_list.append(id)#将ID号存入pet_id,方便数据更新
        pet['id']=id
        pet['title']=e.a.find('span',class_='xinj-con').text
        pet['unit']=e.a.find('span',class_='xinj-bumen').text
        pet['type']=e.a.find('span',class_='xinj-leix').text
        pet['q_time']=e.a.find('span',class_='xinj-time').text
        pet['status']=e.a.find('span',class_='xinj-qingk').text
        pet_list.append(pet)
    return  pet_list

def parse_one_page(url):#第三步
    '''从信件页面，获取问题内容，回复和回复时间'''
    soup=get_soup(url)
    question=soup.find('textarea').text
    comm=soup.find('div',class_='comm')
    fr=comm.find('span',class_='fr').text
    a_time=''
    time_p=re.search('(\d{4}-\d{2}-\d{2} [0-9:]+)$',fr)
    if time_p:
        a_time=time_p.group(1)
    comm.div.decompose()#去掉不必要的内容
    answer=comm.text.strip()
    return question,answer,a_time

def write_obj(id_list):
    with open('./idlist.dat','wb') as f:
        pickle.dump(id_list,f)#将id_list对象保存到idlsit.txt中


def start():
    base_url='http://apps.ganzhou.gov.cn/szfwlwzweb/szfbmwz'

    print('程序开始启动...')
    print('前期准备：获取url')
    t_pet_start=time.time()
    pg_url_list=get_frame_pet_url()#从展示框里面获取的信件
    pet_list=get_pet_obj(pg_url_list)
    write_obj(id_list)
    t_pet_end=time.time()
    total=len(pet_list)#数据条数
    cc=0
    print('开始爬取信件剩余内容！')
    print('爬取进度：')
    for pet in pet_list:
        cc+=1
        print('{:4}{}{}'.format(cc,' /',total))
        pet['question'],pet['answer'],pet['a_time']=parse_one_page(pet['url'])
    t_data_end=time.time()
    t_total=t_data_end-t_pet_start
    t_pet=t_pet_end-t_pet_start
    t_data=t_data_end-t_pet_end    
    #写入表格中
    write_to_excel(pet_list)
    logging.info("数据获取成功")
    
    print('内容已经全部爬取。')
    print("***************************")
    print('共爬取：{}条数据'.format(total))
    print("总耗时：{:.2f}分钟".format(t_total/60))
    print('\t获取信件URL：{:.2f}分钟'.format(t_pet/60))
    print('\t获取信件内容：{:.2f}分钟'.format(t_data/60))
    print("**************************")

if __name__=='__main__':
    start()