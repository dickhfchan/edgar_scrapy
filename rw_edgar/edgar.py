import pandas as pd
import sys
import io
from cassandra.cluster import Cluster

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['13.229.248.211']
cluster = Cluster(server)
session = cluster.connect('scrapy')
result = session.execute("select company from edgar_seven")
for i in result:
    print(i)
#for res in result.index.values:
 #   row_data = result.ix[res,result.columns.values].to_dict()
    #print(row_data['seven_body'])
  #  print(row_data['body_url'])
