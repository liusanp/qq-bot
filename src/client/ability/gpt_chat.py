from src.client.base_ability import Chat, BaseAbility
from src.utils.config import get as get_config
import json
import requests


class GptChat(Chat, BaseAbility):
    
    def __init__(self) -> None:
        super().__init__()
        self.openai_base_url = get_config("openai_base_url")
        self.openai_api_key = get_config("openai_api_key")
        self.openai_model = get_config("openai_model")
    
    def get_response(self, message):
        self.message = message
        sys_prompt = get_config("system_prompt")
        bot_name = get_config("qqbot.name")
        try:
            url = f"{self.openai_base_url}/v1/chat/completions"

            payload = json.dumps({
                "model": self.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": sys_prompt if sys_prompt else f"你是一个很有用的QQ辅助机器人[{bot_name}]。"
                    },
                    {
                    "role": "user",
                    "content": message.content
                    }
                ],
                "stream": False
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.openai_api_key,
            }

            response = requests.request("POST", url, headers=headers, data=payload)

            print(response.text)
            # response = openai.chat.completions.create(
            #     model=openai_model,
            #     messages=[
            #         {'role': 'user', 'content': prompt},
            #     ],
            #     stream=False
            # )
            # return response.choices[0].message.content.strip()
            return self.get_res(content=response.json()['choices'][0]['message']['content'].strip())
        except Exception as e:
            print(e)
            return self.get_res(content="服务不可用，请稍后再试。")