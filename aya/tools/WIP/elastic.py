from elasticsearch import Elasticsearch
import aya

IP_ADDR = '10.10.10.10'

client = Elasticsearch(
  f"http://{IP_ADDR}:9200/",
  api_key=""
)

data = client.search(index="kismet_devices",
    body={
        "query": {
            "match_all": {}  # This gets all documents
        },
        "size": 3000  # This is your LIMIT
    }
)

devices = data['hits']['hits']
for dev in devices:
    source = dev['_source']
    k_dev = aya.KismetDevice.from_json(source)
    if k_dev.dot11:
      print(k_dev)