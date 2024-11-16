from src.client.base_ability import Audio, BaseAbility
from src.utils.config import get as get_config
import requests
from fish_audio_sdk import Session, TTSRequest
from botpy import logging
import re


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
        
    
    def get_response(self, message):
        self.message = message
        try:
            match = re.match(r'^说[（\(](.*?)[）\)][：:](.*)', message.content)
            ref_id = match.group(1)
            prompt = match.group(2)
            # print(f'ref_id: {ref_id}')
            # print(f'prompt: {prompt}')
            self.gen_audio(prompt, self.message.id, ref_id)
            has_up, url = self.uploader.upload(f'./data/{message.id}.mp3')
            if has_up:
                media_id = self.upload_media(url)
                return self.get_res(media_id)
            else:
                return self.get_res("服务不可用，请稍后再试。")
        except Exception as e:
            _log.error(e)
            return self.get_res("服务不可用，请稍后再试。")
        
    def gen_audio(self, prompt, id, ref_id="丁真"):
        self.get_models()
        # Option 1: Using a reference_id
        with open(f'./data/{id}.mp3', "wb") as f:
            for chunk in self.session.tts(TTSRequest(
                reference_id=self.audio_id[ref_id],
                text=prompt
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
                    if i["title"] not in self.model_list:
                        self.model_list.append(i["title"])
                        self.audio_id[i["title"]] = i["_id"]
                self.model_is_up = True
        except Exception as e:
            _log.error(e)