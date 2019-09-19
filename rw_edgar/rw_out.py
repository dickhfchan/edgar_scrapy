import pandas as pd
from cassandra.cluster import Cluster
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['52.76.70.227']
cluster = Cluster(server)
session = cluster.connect('scrapy')
date = pd.read_csv('/home/ubuntu/edgar_scrapy/edgar/edgar/output.csv',sep = '~')
data = []
for res in date.index.values:
    row = date.ix[res,date.columns.values].to_dict()
    data.append(row)
    session.execute("""insert into edgar (company,date,type,clk,clk_url,ten_year_url,body_url,body)values(%s ,%s ,%s, %s, %s ,%s ,%s, %s)""",
                    (str(row['company']),str(row['date']),str(row['type']),str(row['clk']), str(row['clk_url']),str(row['ten_year_url']),
                     str(row['body_url']),str(row['body'])))
print('output file data',len(data))
