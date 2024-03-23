import os
from contextlib import contextmanager


MYSQL = {
  'host': "rm-3ns274fbt2y7o7s8a.mysql.rds.aliyuncs.com",
  'port': 3306,
  'db': "resume",
  'user': "futu",
  'password': "Futu_com",
}

openai_api_key = 'sk-2OyCN2OOgrk8GA6hSASHaMeZBmbh5R0ZNPQ99x122bXWMhuU'
http_proxy = 'https://api.chatanywhere.tech'
https_proxy = 'https://api.chatanywhere.tech'
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
openai_base_url = 'https://api.chatanywhere.tech'
openai_completion_url = f"{openai_base_url}/v1/chat/completions"

init_prompt = '你是一个有用的助手'
no_api_msg = '缺少api key'