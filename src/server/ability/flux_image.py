from src.server.base_ability import Image as ImageClass
from src.utils.config import get as get_config
import json
import requests
from botpy import logging
from src.utils.snowflake import generate_id
import re
import random
import string
from io import BytesIO
import os
from datetime import datetime, timedelta
import sseclient
from PIL import Image
import time


_log = logging.get_logger()


class FluxImage(ImageClass):
    
    def __init__(self) -> None:
        super().__init__()
        self.siliconflow_token = get_config("siliconflow_token")
        self.comfyui_host = get_config("comfyui_host")
        
    def get_help(self):
        return "发送【画：一只小鸡】，生成图片。或者【画（1:1）：一只小鸡】，生成指定宽高图片，宽高比例可选项：1:1, 1:2, 3:2, 3:4, 16:9, 9:16。\n示例：\n画：一个美丽的女孩，带着鲜花和一瓶香水，以新艺术风格的插图，深金色和天蓝色，迈克尔·马尔琴科，竹内直子，深青色和红色，帕特里夏·波拉科，多彩的梦想。\n\n发送照片，风格重绘。"
    
    def generate_random_string(self, length=10):
        # 生成包含字母和数字的随机字符串
        letters_and_digits = string.ascii_lowercase + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))
    
    def gen_time_str(self):
        current_time = datetime.now()
        future_time = current_time + timedelta(minutes=5)
        future_time_string = future_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        return future_time_string
    
    def download_and_convert_image(self, image_url, save_path):
        # 下载图片
        response = requests.get(image_url, verify=False)
        if response.status_code == 200:
            # 使用Pillow处理图像
            img = Image.open(BytesIO(response.content))
            # 转换并保存为PNG格式
            img.save(save_path, 'PNG')
        else:
            raise Exception(f"Failed to download image. Status code: {response.status_code}")
        
    async def get_response(self, message):
        self.message = message
        _log.info(message)
        snowflake_id = generate_id()
        try:
            prompt = message['content']
            match = re.match(r'^画(?:\s*[\(（](\d{1,2}[:：]\d{1,2})[\)）])?\s*[：:](.+)', prompt)
            ratio = "1:1"
            if match:
                if match.group(1):
                    ratio = match.group(1)
                prompt = match.group(2)
            width, height = self.get_wh_by_ratio(ratio)
            prompt = self.translater.trans(prompt)
            _log.info(prompt)
            k_res = await self.get_img_response_siliconflow(prompt, snowflake_id, width, height)
            return k_res
        except Exception as e:
            _log.error(e)
            return self.get_res(content="服务不可用，请稍后再试。")
        
    async def get_response_change_style(self, message):
        snowflake_id = generate_id()
        self.message = message
        attr = message['attachments']
        attr_content_type = attr[-1]['content_type']
        attr_url = attr[-1]['url']
        if 'image' not in attr_content_type:
            return self.get_res(content="发送帮助获取使用方法")
        try:
            # 下载图片
            img_path = f'./data/{snowflake_id}.png'
            self.download_and_convert_image(attr_url, img_path)
            # 上传图片
            url = f"{self.comfyui_host}/upload/image"
            payload = {}
            files=[
                ('image',(f'{snowflake_id}.png',open(img_path,'rb'),'image/png'))
            ]
            headers = {}
            response = requests.request("POST", url, headers=headers, data=payload, files=files)
            _log.info(response.text)
            # 启动解析prompt队列
            url = f"{self.comfyui_host}/prompt"
            payload = json.dumps({
            "client_id": f"{snowflake_id}",
            "prompt": {
                "25": {
                "inputs": {
                    "image": f'{snowflake_id}.png',
                    "upload": "image"
                },
                "class_type": "LoadImage"
                },
                "26": {
                "inputs": {
                    "model": "wd-v1-4-moat-tagger-v2",
                    "threshold": 0.35,
                    "character_threshold": 0.85,
                    "replace_underscore": False,
                    "trailing_comma": False,
                    "exclude_tags": "",
                    "image": [
                    "25",
                    0
                    ]
                },
                "class_type": "WD14Tagger|pysssss"
                }
            }
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            _log.info(response.text)
            prompt_id = response.json()['prompt_id']
            # 获取队列结果
            while True:
                time.sleep(1)
                url = f"{self.comfyui_host}/history/{prompt_id}"
                payload = {}
                headers = {}
                response = requests.request("GET", url, headers=headers, data=payload)
                _log.info(response.text)
                if prompt_id in response.json():
                    img_prompt = response.json()[prompt_id]['outputs']['26']['tags'][0]
                    break
            # 拼接提示词
            final_prompt = f'strong Pixel style, high quality, detailed, Illustration, minimalist avatar, colorful, (realistic:1.5), (half-length portrait:1.5), (oval shape face:1.0), (disheveled:1.0),  (skin details, skin texture:0.5), (skin pores:0.3), (eyes details:1.2), (iris details:1.2), (circular iris:1.2), (circular pupil:1.2), (facial asymmetry, face asymmetry:0.2), (detailed, professional photo, perfect exposition:1.25), (film grain:1.5), {img_prompt}, (shinny skin, reflections on the skin, skin reflections:1.5)'
            # 文生图
            width, height = self.get_wh_by_ratio('1:1')
            k_res = await self.get_img_response_siliconflow(final_prompt, snowflake_id, width, height)
            return k_res
        except Exception as e:
            _log.error(e)
            return self.get_res(content="服务不可用，请稍后再试。")
        
    async def get_img_response_siliconflow(self, prompt, id, width=1024, height=1024):
        url = "https://api.siliconflow.cn/v1/images/generations"
        
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell",
            "prompt": prompt,
            "image_size": f"{width}x{height}",
            "prompt_enhancement": False
        }
        headers = {
            "Authorization": f"Bearer {self.siliconflow_token}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        _log.info(response.text)
        img_url = response.json()['images'][0]['url']
        _log.info(f'img_url: {img_url}')
        if img_url:
            img_path = f'./data/{id}.png'
            self.download_and_convert_image(img_url, img_path)
            has_up, url = self.uploader.upload(img_path)
            if has_up:
                os.remove(img_path)
                return self.get_res(msg_type=7, media_id=url, file_type=1)
            else:
                return self.get_res(content="服务不可用，请稍后再试。")
        else:
            return self.get_res(content="服务不可用，请稍后再试。")
    
    async def get_img_response_kingnish(self, prompt, id, width=1024, height=1024):
        url = "https://kingnish-realtime-flux.hf.space/run/predict"
        sess_hash = self.generate_random_string()
        payload = json.dumps({
            "data": [
                prompt,
                69,
                width,
                height,
                True,
                5
            ],
            "event_data": None,
            "fn_index": 3,
            "trigger_id": 10,
            "session_hash": sess_hash
        })
        # print(payload)
        headers = {
            'content-type': 'application/json',
            'origin': 'https://kingnish-realtime-flux.hf.space',
            'referer': 'https://kingnish-realtime-flux.hf.space/?__theme=light',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        _log.info(response.text)
        img_url = response.json()['data'][0]['url']
        _log.info(f'img_url: {img_url}')
        if img_url:
            img_path = f'./data/{id}.png'
            self.download_and_convert_image(img_url, img_path)
            has_up, url = self.uploader.upload(img_path)
            if has_up:
                os.remove(img_path)
                return self.get_res(msg_type=7, media_id=url, file_type=1)
            else:
                return self.get_res(content="服务不可用，请稍后再试。")
        else:
            return self.get_res(content="服务不可用，请稍后再试。")
        
        
    async def get_img_response_blackforest(self, prompt, id, width=1024, height=1024):
        # 获取token
        url = f"https://huggingface.co/api/spaces/black-forest-labs/FLUX.1-schnell/jwt?expiration={self.gen_time_str()}&include_pro_status=true"
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        hf_token = response.json()["token"]
        _log.info(f'hf_token: {hf_token}')
        
        # 提交任务
        sess_hash = self.generate_random_string()
        url = "https://black-forest-labs-flux-1-schnell.hf.space/queue/join?__theme=light"
        payload = json.dumps({
            "data": [
                prompt,
                716811884,
                True,
                width,
                height,
                4
            ],
            "event_data": None,
            "fn_index": 2,
            "trigger_id": 5,
            "session_hash": sess_hash
        })
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            # 'cookie': '_ga=GA1.2.376343665.1709177677; _ga_R1FN4KJKJH=GS1.1.1709177676.1.1.1709178488.0.0.0',
            'origin': 'https://black-forest-labs-flux-1-schnell.hf.space',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://black-forest-labs-flux-1-schnell.hf.space/?__theme=light',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-zerogpu-token': hf_token
        }
        response = requests.post(url, headers=headers, data=payload)
        _log.info(f'task_res: {response.text}')
        if 'event_id' in response.json():
            # 获取图片地址
            img_url = self.fetch_image_url(sess_hash)
            _log.info(f'img_url: {img_url}')
            if img_url:
                img_path = f'./data/{id}.png'
                self.download_and_convert_image(img_url, img_path)
                has_up, url = self.uploader.upload(img_path)
                if has_up:
                    os.remove(img_path)
                    return self.get_res(msg_type=7, media_id=url, file_type=1)
                else:
                    return self.get_res(content="服务不可用，请稍后再试。")
            else:
                return self.get_res(content="服务不可用，请稍后再试。")
        else:
            return self.get_res(content="服务不可用，请稍后再试。")
        
    def fetch_image_url(self, sess_hash):
        # 请求头
        headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'cookie': '_ga=GA1.2.376343665.1709177677; _ga_R1FN4KJKJH=GS1.1.1709177676.1.1.1709178488.0.0.0',
            'origin': 'https://black-forest-labs-flux-1-schnell.hf.space',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://black-forest-labs-flux-1-schnell.hf.space/?__theme=light',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
        # SSE 请求URL
        url = f'https://black-forest-labs-flux-1-schnell.hf.space/queue/data?session_hash={sess_hash}'
        # 发送请求
        # response = requests.get(url, headers=headers, stream=True)
        # print(f'stream_res: {response.text}')
        # 使用 sseclient 处理 SSE 数据流
        client = sseclient.SSEClient(url)
        # 监听事件流
        for event in client:
            try:
                # 解析事件数据，通常是 JSON 格式
                data = event.data
                print(f"Received data: {data}")
                data_json = json.loads(data)
                if 'msg' in data_json and data_json['msg'] == "process_completed":
                    return data_json['output']['data'][0]['url']
            except Exception as e:
                print(f"Error parsing event: {e}")