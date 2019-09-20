import pandas as pd
from cassandra.cluster import Cluster
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['52.76.70.227']
cluster = Cluster(server)
session = cluster.connect('scrapy')
date = pd.read_csv('/home/ubuntu/edgar_scrapy/edgar/edgar/out.xlsx',sep = '~')
data = []
for res in date.index.values:
    row = date.ix[res,date.columns.values].to_dict()
    data.append(row)
    session.execute("""insert into hangseng (constituent_type,constituent_name,code)values(%s ,%s ,%s)""",
                    ('50 xlsx',str(row['constituent_name']),str(row['code'])))
print('out file data',len(data))
