import json
# requires Python SDK version 1.3 or higher
from algosdk.v2client import indexer

headers = {
    "X-API-Key": "K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4",
}
# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="K7DgVll3W19DdHA3FTduX4XZTuCvTFf32HXUP5E4", indexer_address="https://testnet-algorand.api.purestake.io/idx2", headers=headers)
# /indexer/python/search_transactions_min_amount.py

response = myindexer.account_info(
    address="IH5Z5UZCZKNAH5OICUGHFEYM2JDMJRUSIUV4TZEQYHRNS3T2ROOV32CDIA")

print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))


