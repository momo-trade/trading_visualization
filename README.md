Kibana/Elasticsearchを使ってトレードbotの損益を可視化するためのツールです。  
dockerを使うことで環境構築を簡単にします。
pythonスクリプトを実行することでElasticsearchにデータをためていくことができます。
Kibanaダッシュボードの作り方、使い方については使う人がいればレクチャしますのでDMください。

## 事前準備
dockerおよびdocker-composeの導入は事前に済ませておきます。  
[dockerインストール]   
https://docs.docker.com/engine/install/ubuntu/

[docker-composeのインストール]  
https://docs.docker.jp/compose/install.html#linux


## 導入手順
1. githubからソースをクローン
```
git clone https://github.com/momo-trade/trading_visualization.git
```
2. Kibanaにログインするユーザのパスワードを設定するため.envファイルを編集
```
ELASTIC_PASSWORD="好きなパスワードを設定"
```
3. コンテナの立ち上げ
```
docker-compose -f elastic-non-tls.yaml

(TLSを有効にしたい場合)
docker-compose -f create-certs.yaml run --rm create_certs
docker-compose -f elastic-tls.yaml up -d
```
4. Kibanaにログインしてみる  
http://<環境のIP>:5601 または、https://<環境のIP>:5601 (TLS有効の場合)   
ログインパスワード: elastic  
パスワード: .envに記載のパスワード

5. python環境にログイン
```
docker-compose -f elastic-non-tls.yaml exec python_env bash
```

6. configファイルの編集(python_env内)
```
# Exchange Setting
url: "https://api.bybit.com"
api_key: "APIキー"
api_secret: "API Secret"

# Elasticsearch Setting
es_user: elastic
es_pass: ".envに記載したパスワードと同じものを指定"
index_name: wallet_fund

mappings:
  properties:
    bot_name:
      type: keyword
    wallet_id:
      type: keyword
    type:
      type: keyword
    amount:
      type: double
    adress:
      type: keyword
    wallet_balance:
      type: double

# Target Strategy
bot_name: "Botの名前などの識別子"
```

6. スクリプトの実行(python_env内)
以下を実行するとサンプルの場合、Bybitからデータをwallet fundデータを取得しElasticsearchに格納します。cronなどで定期実行するように設定しておく。  
configを複数作れば、複数botの損益管理ができます。
```
python bybit_fund.py config/bybit_bot1.yaml
```

## bybit_fund.pyの簡単な説明
- pybitモジュールを使ってHTTPリクエストを実行
- Elasticsearch内にindexがない場合は、configに指定したindex_name、mappingに従いindexを作成
- send_elasticsearchでは、重複データを登録しないようにElasticsearch内を検索し、新規レコードのみを登録する処理を入れている
- httpにするかhttpsにするかでソースコードを修正する必要あり(http/httpsの部分)。ダサいのでいつか改善


## 参考
Install Elasticsearch with Docker  
https://www.elastic.co/guide/en/elastic-stack-get-started/current/get-started-docker.html

Bybitの公式？APIクライアント  
https://github.com/verata-veritatis/pybit

## docker-compseの小ネタ(備忘録)

| やること | コマンド |
| ------ | ------ |
| コンテナの立ち上げ | docker-compose up -d |
| コンテナの状態チェック | docker-compose ps |
| 停止中のコンテナも含めて確認する場合 | docker-compose ps -a |
| 特定のコンテナだけ削除 | docker-compose rm -fsv コンテナ名 |
| 個別にコンテナを作り直す | docker-compose build --no-cache コンテナ名 |
| コンテナにログインする | docker-compose exec コンテナ名 bash |
| 全コンテナの停止 | docker-compose stop |
| 全コンテナの削除 | docker-compose down |
| 全コンテナの削除(イメージも削除する) | docker-compose down --rmi all |
| コンテナのログ確認 | docker-compose logs コンテナ名 |
