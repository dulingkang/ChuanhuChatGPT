import os

MYSQL = {
  'host': "",
  'port': 3306,
  'db': "",
  'user': "",
  'password': "",
}

openai_api_key = ''
http_proxy = ''
https_proxy = ''
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
openai_base_url = ''
openai_completion_url = f"{openai_base_url}/v1/chat/completions"

init_prompt = '你是一个有用的助手'
no_api_msg = '缺少api key'
