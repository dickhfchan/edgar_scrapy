import requests
import json
from lxml import etree
import pandas as pd
import sys
import io
import pdfplumber
import fitz
import re
import time
from cassandra.cluster import Cluster

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['52.76.70.227']
cluster = Cluster(server)
session = cluster.connect('scrapy')
# result = pd.DataFrame(list(session.execute('select code from hangseng')))
# codes = [code for code in result['code']]
codes = ['1302', '2186', '83', '1638', '2343', '546', '1816', '1060', '23', '2362', '1618', '6055', '1896', '86', '950', '1208', '6806', '3983', '1176', '2232', '754', '2601', '2601', '6068', '2899', '386', '386', '405', '1811', '2883', '1378', '1171', '3900', '520', '819', '2768', '2329', '631', '1999', '371', '3898', '2588', '3339', '914', '914', '860', '607', '2020', '2020', '639', '435', '1513', '1988', '1988', '939', '939', '268', '1333', '2388', '2611', '762', '700', '700', '1099', '1099', '817', '322', '3888', '2858', '3690', '1916', '2678', '686', '1317', '6098', '3306', '2', '1083', '123', '590', '3360', '966', '966', '1071', '598', '1368', '998', '998', '1610', '1951', '1686', '1929', '175', '175', '489', '3323', '3323', '694', '1996', '512', '358', '931', '2877', '576', '241', '1361', '1383', '636', '3933', '1765', '1788', '973', '839', '3800', '336', '1169', '548', '6088', '2333', '363', '496', '3958', '1666', '1970', '142', '1177', '1908', '87', '1530', '506', '3380', '1888', '1119', '144', '6881', '1193', '3877', '2238', '656', '656', '303', '1890', '906', '951', '2018', '1848', '1558', '2799', '78', '1044', '1044', '189', '315', '902', '152', '1911', '1800', '1800', '257', '272', '3993', '1117', '1918', '1918', '451', '2869', '1818', '3309', '2380', '267', '267', '16', '1963', '2607', '337', '2128', '855', '1958', '788', '788', '1778', '1211', '1211', '1528', '6030', '6030', '297', '552', '1579', '1186', '884', '285', '5', '1138', '1336', '1336', '1907', '1257', '1898', '3377', '388', '1234', '763', '525', '1905', '1928', '2001', '1883']

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
