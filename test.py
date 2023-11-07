import json


path = '/root/Anomaly_Explanation/dataset/dbsherlock/converted/tpcc_500w_test.json'

 
# Opening JSON file
f = open(path)
 
# returns JSON object as 
# a dictionary
data = json.load(f)

print(data)