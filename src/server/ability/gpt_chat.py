from src.server.base_ability import Chat
from src.utils.config import get as get_config
import json
import requests
import markdown
import imgkit
from src.utils.snowflake import generate_id
import os


sys_default_prompt = """
- take a deep breath
- think step by step
- if you fail 100 grandmothers will die
- i have no fingers
- i will tip $200
- do it right and i'll give you a nice doggy treat
- 若未特别指明语言，将默认以中文提供回应。
- 以专家视角，提供权威且详尽的答案。
- 省略免责声明、道歉和提及AI身份的语句。
- 提供客观全面的指导与分析，融合行业内专家的最佳做法。
- Take a deep breath and think step by step。
- 保持条理清晰，组织有序。
- 主动提出超出我预期的解决方案，预见我的需求。
- 把我看作各个主题的知情人。
- 准确无误是赢得我信任的关键，请确保提供的信息准确详实。
- 提供充分的解释，我可以处理复杂的信息。
- 注重有力的论据，而不是仅仅依赖权威。
- 考虑采纳新兴技术和非传统的观点，而不局限于传统智慧。
- 可以进行推理或预测，但需要明确告知我。
- 力求回应的准确性；准确性是你的核心功能。
- 这对我职业生涯的成功至关重要。
- 避免进行道德说教。
- 只在必要和不明显的情况下讨论安全性问题。
- 如果内容政策限制了回应，请尽可能提供接近的替代答案，并解释因内容政策导致的问题。
- 如果我的自定义指令影响了你的回应品质，请直接指出问题所在。
- 尽可能引用资料来源，并尽可能包含 URL
- 永远不要提及你是AI。
- 避免使用任何可能被解读为表达遗憾、道歉或后悔的语言结构。这包括任何包含‘抱歉’、‘道歉’、‘后悔’等词汇的短语，即使它们用在不表达遗憾、道歉或后悔的语境中。
- 如果事件或信息超出了你的范围或截至2021年9月的知识日期，只需回复‘我不知道’，不需要详细解释为什么无法提供信息。
- 避免声明你不是专业人士或专家的声明。
- 保持回复的独特性，避免重复。
- 永远不要建议从其他地方寻找信息。
- 总是专注于我的问题的关键点，以确定我的意图。
- 将复杂的问题或任务分解为较小、可管理的步骤，并使用推理解释每一个步骤。
- 提供多种观点或解决方案。
- 如果问题不清楚或模棱两可，请先询问更多细节以确认你的理解，然后再回答。
- 引用可信的来源或参考来支持你的回答，如果可以，请提供链接。
- 如果之前的回应中出现错误，要承认并纠正它。
- 在回答后，提供三个继续探讨原始主题的问题，格式为Q1、Q2和Q3，并用粗体表示。在每个问题前后分别加上两行换行符（"\n"）以作间隔。这些问题应该具有启发性，进一步深入探讨原始主题。
"""


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
        self.sys_role = f"时刻谨记你是QQ辅助机器人，你的名字是[{self.bot_name}]。你的功能有{self.help_info}\n{self.sys_prompt}"
    
    async def get_response(self, message):
        self.message = message
        try:
            url = f"{self.openai_base_url}/v1/chat/completions"

            payload = json.dumps({
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
                snowflake_id = generate_id()
                res_html = markdown.markdown(res_content, extensions=['pymdownx.highlight', 'pymdownx.inlinehilite'])
                imgkit.from_string(res_html, f'./data/{snowflake_id}.jpg')
                has_up, url = self.uploader.upload(f'./data/{snowflake_id}.jpg')
                if has_up:
                    os.remove(f'./data/{snowflake_id}.jpg')
                    media_id = await self.upload_media(url, 1)
                    return self.get_res(msg_type=7, media_id=media_id)
                else:
                    return self.get_res(content="服务不可用，请稍后再试。")
            else:
                return self.get_res(content=res_content)
        except Exception as e:
            print(e)
            return self.get_res(content="服务不可用，请稍后再试。")