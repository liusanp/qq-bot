from src.server.base_ability import Chat
from src.utils.config import get as get_config
import json
import requests
import markdown
import imgkit
from src.utils.snowflake import generate_id
import os


sys_default_prompt = ""


class GptChat(Chat):
    
    def __init__(self) -> None:
        super().__init__()
        self.openai_base_url = get_config("openai_base_url")
        self.openai_api_key = get_config("openai_api_key")
        self.openai_model = get_config("openai_model")
        self.sys_prompt = get_config("system_prompt")
        if not self.sys_prompt:
            self.sys_prompt = sys_default_prompt
        self.bot_name = get_config("qqbot.name")
        self.help_info = get_config("help_info")
        self.sys_role = f"\n时刻谨记你是辅助机器人，你的名字是[{self.bot_name}]。你的功能有{self.help_info}\n{self.sys_prompt}"
    
    async def get_response(self, message):
        self.message = message
        try:
            snowflake_id = generate_id()
            url = f"{self.openai_base_url}/v1/chat/completions"

            payload = json.dumps({
                "chatId": snowflake_id,
                "model": self.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.sys_role
                    },
                    {
                    "role": "user",
                    "content": message['content']
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
            res_content = response.json()['choices'][0]['message']['content'].strip()
            if get_config("md_2_img"):
                res_html = markdown.markdown(res_content, extensions=['pymdownx.highlight', 'pymdownx.inlinehilite'])
                imgkit.from_string(res_html, f'./data/{snowflake_id}.jpg')
                has_up, url = self.uploader.upload(f'./data/{snowflake_id}.jpg')
                if has_up:
                    os.remove(f'./data/{snowflake_id}.jpg')
                    return self.get_res(msg_type=7, media_id=url, file_type=1)
                else:
                    return self.get_res(content="服务不可用，请稍后再试。")
            else:
                return self.get_res(content=res_content)
        except Exception as e:
            print(e)
            return self.get_res(content="服务不可用，请稍后再试。")