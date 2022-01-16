from pybit import HTTP
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import sys
import yaml
import traceback


class DataCollect:
    def __init__(self, config):
        self.__load_config(config)
        self.es = None

        self.__init_elastic()

    def __del__(self):
        self.es.close()

    def __load_config(self, config):
        try:
            with open(config, 'r') as config_yaml:
                settings = yaml.safe_load(config_yaml)
                for key, val in settings.items():
                    setattr(self, key, val)
        except Exception:
            print(traceback.format_exc())

    def __init_elastic(self):
        url = 'https://{}:{}@elasticsearch:9200'.format(self.es_user, self.es_pass)
        self.es = Elasticsearch([url], verify_certs=False, ssl_show_warn=False)

        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, mappings=self.mappings)

    def get_fund(self):
        session = HTTP(self.url, api_key=self.api_key, api_secret=self.api_secret)
        wallet_fund = session.wallet_fund_records()
        result = []
        for fund in wallet_fund['result']['data']:
            row = {
                'bot_name': self.bot_name,
                'wallet_id': str(fund['wallet_id']),
                'type': fund['type'],
                'amount': float(fund['amount']),
                'address': fund['address'],
                'wallet_balance': float(fund['wallet_balance']),
                '@timestamp': fund['exec_time']
            }
            result.append(row)

        return result

    def send_elasticsearch(self, send_data):
        # すでに存在するデータは登録しないようにする
        result = []
        for data in send_data:
            query = {
                'bool': {
                    'filter': [
                        {'term': {'bot_name': data['bot_name']}},
                        {'term': {'@timestamp': data['@timestamp']}}
                    ]
                }
            }
            # Elasticsearchを検索してドキュメントが登録済みか確認する
            check = self.es.search(index=self.index_name, query=query)['hits']['total']['value']

            # 検索にヒットしなかった場合、登録用形式に変換する
            if check == 0:
                row = {
                    '_op_type': 'create',
                    '_index': self.index_name,
                    '_source': data
                }
                result.append(row)

        if len(result):
            print('{}件の新規データを登録'.format(len(result)))
            helpers.bulk(self.es, result)


if __name__ == '__main__':
    config_file = sys.argv[1]
    client = DataCollect(config_file)
    result = client.get_fund()
    client.send_elasticsearch(result)
