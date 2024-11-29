from src.server.base_ability import Audio
from src.utils.config import get as get_config
import requests
from fish_audio_sdk import Session, TTSRequest
from botpy import logging
import re
import os
from src.utils.snowflake import generate_id


_log = logging.get_logger()


class FishAudio(Audio):
    
    def __init__(self) -> None:
        super().__init__()
        self.fish_audio_key = get_config("fish_audio_key")
        self.session = Session(self.fish_audio_key)
        self.model_is_up = False
        self.audio_id = {}
        self.model_list = []
        self.get_models()
        
    def get_help(self):
        help_list = []
        for m in self.model_list:
            hm = f"说（{m}）：你好啊。"
            help_list.append(hm)
        return "发送【说（丁真）：你好啊】，生成语音。\n可用模型：\n" + '\n'.join(help_list)
    
    async def get_response(self, message):
        self.message = message
        snowflake_id = generate_id()
        try:
            match = re.match(r'^说[（\(](.*?)[）\)][：:](.*)', message['content'])
            ref_id = match.group(1)
            prompt = match.group(2)
            # print(f'ref_id: {ref_id}')
            # print(f'prompt: {prompt}')
            audio_file_path = f'./data/{snowflake_id}'
            self.gen_audio(prompt, f'{audio_file_path}.mp3', ref_id)
            self.convert_to_silk(audio_file_path)
            has_up, url = self.uploader.upload(f'{audio_file_path}.silk')
            if has_up:
                os.remove(f'{audio_file_path}.mp3')
                os.remove(f'{audio_file_path}.silk')
                return self.get_res(msg_type=7, media_id=url, file_type=3)
            else:
                return self.get_res(content="服务不可用，请稍后再试。")
        except Exception as e:
            _log.error(e)
            return self.get_res(content="服务不可用，请稍后再试。")
        
    def gen_audio(self, prompt, file_path, ref_id="丁真"):
        self.get_models()
        # Option 1: Using a reference_id
        with open(file_path, "wb") as f:
            for chunk in self.session.tts(TTSRequest(
                reference_id=self.audio_id[ref_id],
                text=prompt,
                format='mp3'
            )):
                f.write(chunk)
                
    def get_models(self):
        if self.model_is_up:
            return
        url = "https://api.fish.audio/model"
        querystring = {"page_size":"20","page_number":"1"}
        headers = {"Authorization": f"Bearer {self.fish_audio_key}"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        # print(response.text)
        try:
            items = response.json()["items"]
            if items and len(items) > 0:
                self.model_list = []
                for i in items:
                    if i["title"].strip() not in self.model_list:
                        self.model_list.append(i["title"].strip())
                        self.audio_id[i["title"].strip()] = i["_id"]
                self.model_is_up = True
        except Exception as e:
            _log.error(e)