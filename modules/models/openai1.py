import json
import requests
import traceback
import tiktoken

from ..setting import init_prompt, no_api_msg, openai_completion_url

def construct_text(role, text):
    return {"role": role, "content": text}


def construct_user(text):
    return construct_text("user", text)


def construct_system(text):
    return construct_text("system", text)


def construct_assistant(text):
    return construct_text("assistant", text)

def count_token(input_str):
    encoding = tiktoken.get_encoding("cl100k_base")
    if type(input_str) == dict:
        input_str = f"role: {input_str['role']}, content: {input_str['content']}"
    length = len(encoding.encode(input_str))
    return length


class BaseModel1():
    def __init__(self, model_name, api_key='', prompt=init_prompt, temperature=1.0) -> None:
        self.model_name = model_name
        self.api_key = api_key
        self.prompt = prompt
        self.temperature = temperature
        self.history = []

    def get_answer_at_once(self):
        if not self.api_key:
            raise Exception(no_api_msg)
        response = self._get_response()
        response = json.loads(response.text)
        content = response["choices"][0]["message"]["content"]
        total_token_count = response["usage"]["total_tokens"]
        return content, total_token_count

    def predict(self, text, clear=False):
        if clear:
            self.history = []
        text = text[:4000]
        self.history.append(construct_user(text))
        content, token_count = self.get_answer_at_once()
        return content


class OpenAIClient1(BaseModel1):
    def __init__(
        self,
        api_key,
        prompt=init_prompt,
        temperature=1.0,
    ) -> None:
        super().__init__(model_name='gpt-3.5-turbo', api_key=api_key, prompt=prompt, temperature=temperature)
        self._refresh_header()

    def get_answer_stream_iter(self):
        if not self.api_key:
            raise Exception(no_api_msg)
        response = self._get_response(stream=True)
        if response is not None:
            iter = self._decode_chat_response(response)
            partial_text = ""
            for i in iter:
                partial_text += i
                yield partial_text
        else:
            yield '错误'


    def get_once_answer(self, text):
        if not self.api_key:
            raise Exception(no_api_msg)
        response = self._get_response(text=text)
        response = json.loads(response.text)
        content = response["choices"][0]["message"]["content"]
        total_token_count = response["usage"]["total_tokens"]
        return content, total_token_count

    def _get_response(self, stream=False, text=""):
        openai_api_key = self.api_key
        prompt = self.prompt
        history = [text] if text else self.history
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }

        if prompt is not None:
            history = [construct_system(prompt), *history]

        payload = {
            "model": self.model_name,
            "messages": history,
            "temperature": self.temperature,
            "top_p": 1.0,
            "n": 1,
            "stream": stream,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            'stop': []
        }
        try:
            response = requests.post(
                openai_completion_url,
                headers=headers,
                json=payload,
                stream=stream,
                timeout=60,
            )
        except:
            traceback.print_exc()
            return None
        return response

    def _refresh_header(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


    def _decode_chat_response(self, response):
        error_msg = ""
        for chunk in response.iter_lines():
            if chunk:
                chunk = chunk.decode()
                chunk_length = len(chunk)
                try:
                    chunk = json.loads(chunk[6:])
                except:
                    print("JSON解析错误,收到的内容: " + f"{chunk}")
                    error_msg += chunk
                    continue
                try:
                    if chunk_length > 6 and "delta" in chunk["choices"][0]:
                        if "finish_reason" in chunk["choices"][0]:
                            finish_reason = chunk["choices"][0]["finish_reason"]
                        else:
                            finish_reason = chunk["finish_reason"]
                        if finish_reason == "stop":
                            break
                        try:
                            yield chunk["choices"][0]["delta"]["content"]
                        except Exception as e:
                            # logging.error(f"Error: {e}")
                            continue
                except:
                    print(f"ERROR: {chunk}")
                    continue
        if error_msg and not error_msg=="data: [DONE]":
            raise Exception(error_msg)
