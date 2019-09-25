import requests
import json
from lxml import etree
import pandas as pd
import sys
import io
import pdfplumber
from cassandra.cluster import Cluster
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')
server = ['52.76.70.227']
cluster = Cluster(server)
session = cluster.connect('scrapy')
result = pd.DataFrame(list(session.execute('select code from hangseng')))
codes = [code for code in result['code']]
print(codes)
