import requests
import json
from lxml import etree
import pandas as pd
import sys
import io
import pdfplumber
import fitz
import re
from cassandra.cluster import Cluster

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['52.76.70.227']
cluster = Cluster(server)
session = cluster.connect('scrapy')
result = pd.DataFrame(list(session.execute('select code from hangseng')))
codes = [code for code in result['code']]

for code in codes:
    print('current code:', code)
    r = requests.get(f'https://www1.hkexnews.hk/search/prefix.do?&callback=callback&lang=ZH&type=A&name={code}&market=SEHK&_=1569225522122')
    ids = r.text.strip().lstrip('callback(').rstrip(');')
    stockIds = json.loads(ids)
    stockId = [stockInfo for stockInfo in stockIds['stockInfo']][0]
    id = stockId['stockId']
    data = {
        'category': '0',
        'market': 'SEHK',
        'searchType': '1',
        't1code': '40000',
        't2Gcode': '-2',
        't2code': '-2',
        'stockId': '513',
        'from': '20100101',
        'to': '20190923',
        'MB-Daterange': '0'
    }
    data['stockId'] = str(id)
    header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Length': '155',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': 'JSESSIONID=4wXfFiY0u_v2FS3YKpQyQZneczkkzJVLiLRLlubZ; TS014a5f8b=015e7ee603dc36934551ce1e05f4083fb9275aa0f824b4fea033486c56ae1502de00cf1a5b8ab83987556452bd0422e51704899faa01b223b131d2ec773242bb905885addd; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1; sclang=en; WT_FPC=id=180.167.170.226-599130208.30764952:lv=1569221182925:ss=1569220814106; TS0168982d=015e7ee6034a044be320f26fdc44d29cbc99b17d0af940335fb6912f65956f924e49196d85d3b68193102a4ec98af700b15c1a5ffb',
                'Host': 'www1.hkexnews.hk',
                'Origin': 'https://www1.hkexnews.hk',
                'Referer': 'https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    response = requests.post(url='https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en',data = data,headers = header)
    s=etree.HTML(response.text)
    defalut_dates = s.xpath('//table/tbody/tr/td[1]/text()')
    dates = [f"{i.split('/')[2].split(' ')[0]}-{i.split('/')[1]}-{i.split('/')[0]}" for i in defalut_dates if i!=' ']
    codes = s.xpath('//table/tbody/tr/td[2]/text()')
    abbreviations = s.xpath('//table/tbody/tr/td[3]/text()')
    urls = s.xpath('//table/tbody/tr/td[4]/div[@class="doc-link"]/a/@href')

    for inx,url in enumerate(urls):
        link = f'https://www1.hkexnews.hk{url}'
        print(link)
        r = requests.get(link)
        fo = open(r"/home/ubuntu/edgar_scrapy/need.pdf",'wb')
        fo.write(r.content)
        fo.close()
        time.sleep(6)
        errorpdfs = []
        articles = ''
        try:
            with pdfplumber.open(r"/home/ubuntu/edgar_scrapy/need.pdf") as pdf:
                page_count = len(pdf.pages)
                print('total pages:', page_count)
                for page in pdf.pages:
                    spot = re.findall('(\n\w{1}\n)',page.extract_text())
                    body = f'---------- The {page.number} page ----------\n' + page.extract_text()
                    bodys = body.replace('\n','') if len(spot)>5 else body
                    articles += bodys
        except:
            try:
                doc = fitz.open(r"/home/ubuntu/edgar_scrapy/need.pdf")
                print('total pages:', doc.pageCount)
                for page in doc:
                    body = f'---------- The {page.number} page ----------\n' + page.getText()
                    articles += body
                doc.close()
            except:
                errorpdfs.append(link)
                print('error pdf urls list ===== :', errorpdfs)
        finally:
            session.execute("insert into hkexnews (url,date,code,abbreviation,body)values(%s ,%s ,%s, %s, %s)",
                         (link,dates[inx],str(codes[inx]),str(abbreviations[inx]),articles))
