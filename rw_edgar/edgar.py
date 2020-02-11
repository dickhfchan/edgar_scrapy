import pandas as pd
import sys
import io
from cassandra.cluster import Cluster

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['13.229.248.211']
cluster = Cluster(server)
session = cluster.connect('scrapy')
result = pd.DataFrame(list(session.execute("select * from bloomberg where year = '2019'")))
print(len(result))
for res in result.index.values:
    row_data = result.ix[res,result.columns.values].to_dict()
    print(row_data['body'])
