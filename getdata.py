import requests
import sys
import pandas as pd
from bs4 import BeautifulSoup  
from datetime import datetime 

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    "Refer":"http://wz.yongzhou.gov.cn/",
    'Connection': 'close'  #防止反复爬取报错
}

MAX_C = 10    #最大爬取次数，反复爬取次数过多，容易触发反爬机制
ROOT = 'http://wz.yongzhou.gov.cn/'  #根网址
WEB_PAGE = '?page={0}'   #换页

def main():
    print(datetime.now().strftime("%H:%M:%S"),'start')
    filename = 'output.xlsx'
    print(datetime.now().strftime("%H:%M:%S"),"正在爬取网址")
    urls = get_urls()  #爬取网址 
    print(datetime.now().strftime("%H:%M:%S"),'正在爬取网页内容')
    data_all = parserpage(urls)  #爬取网址内容
    outdata( data_all,filename )   #保存所爬取的数据至excel表格
    print('数据已经全部存入"{0}"中'.format(filename))
    print(datetime.now().strftime("%H:%M:%S"),'end')
    
    
    
def get_urls():    #得到的不止是网址，每个元素是网址加一个空格加状态的形式
    urls_one = get_urls_one()   #爬取第一层网址
    urls_two = get_urls_two( urls_one )   #爬取第二层网址
    return urls_two
    


def get_urls_one():
    urls = []   
    cc = MAX_C   
    while True:  #网站不稳定，多次进行爬取  爬取主页面
        soup = BeautifulSoup( requests.get(ROOT,headers = headers).content,'lxml')\
                .find('div','wz_area_l')   #解析网址
        if soup != None:
            break
        if cc < 0:   #多次爬取都未成功
            print('not achieve')
            sys.exit()
        cc -= 1     
    #爬取第一层网址
    urls += [ ( ROOT + a.get('href') ) for nob in soup.find_all('div','cls') 
             for tr in nob.find('div','text').find_all('tr') for a in tr.find_all('a') ]
    return urls
    


def get_urls_two(root_urls):  #爬取二层网址
    urls = []
    for root in root_urls:  
        #得到页数
        Total = int( str( BeautifulSoup( requests.get(root,headers = headers).content,"lxml")\
            .find('script',language = 'JavaScript') )\
            .split(';')[1].split('=')[1].strip() )   #页数如果是1，则Total得到的数是0
        TotalPage = 1 if Total == 0 else Total
        for c,page in enumerate( range( 1,TotalPage + 1 ) ):  #c为迭代次数-1，即从0开始
            url_page = root if c == 0 else root + WEB_PAGE.format( page )  #第一页不需换页
            #加上网址页码后缀字符串，实现换页
            #爬取第二层网址
            soup = BeautifulSoup( requests.get(url_page).content,'html.parser')\
                .find('div','wz_area_l').find_all('div','text')[1]
            #顺便把状态加上
            urls += [ ( ROOT + tr.a.get('href') ) + ' ' + tr.font.text.strip('[]')
                        for tr in soup.find_all('tr')[1:] 
                        if tr.font.text.strip('[]') != '处理中']
    return urls


    
def parserpage(root_urls):  #爬取网页内容
    data_all = {} #爬取的数据存入字典，字典中的每一个元素都是一个列表
    #问题编号，单位，点击数，提问日期，提问时间分别被赋值成0，1，2，3，4，方便查找
    qstion_ord,unit,click,qstion_day,qstion_time = range(5) 
    for root_url in root_urls:   
        url,status = root_url.split()  #得到网址和状态
        soup = BeautifulSoup( requests.get(url,headers=headers).text,'lxml')\
            .find_all('div','text') 
        #问题信息有四个元素 与qstion_ord,unit,click,qstion_day,qustion_time对应
        qstion_msg = soup[0].find('div','pro').text.split()[:-1]  
        #setfault方法 如果没有该键，则以该值为键在字典中生成一个元素，该元素的值是一个空列表
        data_all.setdefault('网址',[]).append( url )  
        data_all.setdefault('状态',[]).append( status.strip() )  
        data_all.setdefault('问题编号',[]).append( qstion_msg[ qstion_ord ].split('：')[1] )
        data_all.setdefault('问题标题',[]).append( soup[0].find('div','c_title').h1.text )
        data_all.setdefault('单位',[]).append( qstion_msg[ unit ].split('：')[1] )
        data_all.setdefault('点击数',[]).append( qstion_msg[ click ].split('：')[1] )
        data_all.setdefault('提问时间',[]).append( qstion_msg[ qstion_day ]\
                                              .split('：')[1] + ' ' + qstion_msg[ qstion_time ] )
        #爬取提问正文
        qstion_text = soup[0].find('div','content').text
        if qstion_text.split() == '':   #正文是图片
            data_all.setdefault('提问正文',[]).append('图片')
        else:data_all.setdefault('提问正文',[]).append( qstion_text )
        #爬取回复正文
        react_text = ''.join( soup[1].text.rsplit('您认为',1)[:-1] )
        if react_text.split() == []:  #回复在评论区或者回复正文只有图片
            data_all.setdefault('回复正文',[]).append('回复在评论区或者回复正文只有图片')
        else:data_all.setdefault('回复正文',[]).append( react_text )
        #爬取评论
        #爬取评论页数,进行换页爬取评论
        Total = int( str( soup[2].find('script') )\
                            .split(';')[1].split('=')[1] )
        TotalPage = 1 if Total == 0 else Total  #如果页数为1，则Total得到的数为0
        for c,page in enumerate( range( 1,TotalPage + 1 ) ):  #c为迭代次数-1
            comments_url = url if c == 0 else url + WEB_PAGE.format( page ) #第一页不需换页
            comments = BeautifulSoup( requests.get(comments_url,headers = headers).content,'lxml')\
                        .find_all('div','cls nob')[2].find('div',id = 'comment')\
                        .find_all('div','pl_content')
        if comments != []:
            com = ''
            for c,comment in enumerate(comments,1):
                com += ( str(c) + '楼: ' + comment.text + '\n' )
            data_all.setdefault('评论',[]).append( com )
        else :  #没有评论
            data_all.setdefault('评论',[]).append( '暂无评论' )
    return data_all



def outdata(data_all,filename):  #输出数据
    writer = pd.ExcelWriter(filename)
    pd.DataFrame(data_all).to_excel(writer)
    writer.save()
    


if __name__ == '__main__':   #作为脚本
    main()

