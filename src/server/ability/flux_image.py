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
from src.utils.hf_util import req_img2img, req_text2img


_log = logging.get_logger()


class FluxImage(ImageClass):
    
    def __init__(self) -> None:
        super().__init__()
        self.siliconflow_token = get_config("siliconflow_token")
        self.comfyui_host = get_config("comfyui_host")
        
    def get_help(self):
        return "1、发送【画：一只小鸡】，生成图片。或者【画（1:1）：一只小鸡】，生成指定宽高图片，宽高比例可选项：1:1, 1:2, 3:2, 3:4, 16:9, 9:16。\n示例：\n画：一个美丽的女孩，带着鲜花和一瓶香水，以新艺术风格的插图，深金色和天蓝色，迈克尔·马尔琴科，竹内直子，深青色和红色，帕特里夏·波拉科，多彩的梦想。\n\n2、发送照片和风格，重绘照片，指定风格生成时间较长，请耐心等待。可用风格：小鸡气人、蓝色简约、黄色卡通"
    
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
        _log.info(f"download url: {image_url}")
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
        prompt = message['content']
        img_style = get_config(f"img_style")
        if prompt and prompt in img_style:
            return await self.get_response_change_style_assign(message)
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
        
    async def get_response_change_style_assign(self, message):
        snowflake_id = generate_id()
        self.message = message
        img_style = get_config(f"img_style")
        hf_token = get_config("hf_token")
        style = message['content']
        attr = message['attachments']
        attr_content_type = attr[-1]['content_type']
        attr_url = attr[-1]['url']
        if 'image' not in attr_content_type:
            return self.get_res(content="发送帮助获取使用方法")
        try:
            # 上传原始图片
            src_img_path = f'./data/{snowflake_id}-source.png'
            self.download_and_convert_image(attr_url, src_img_path)
            has_up, src_img_url = self.uploader.upload(src_img_path)
            # 转换图片风格
            res = req_img2img(src_img_url, img_style[style], hf_token=hf_token)
            res_img = Image.open(res)
            img_path = f'./data/{snowflake_id}.png'
            # 下载图片
            res_img.save(img_path, 'PNG')
            has_up, url = self.uploader.upload(img_path)
            if has_up:
                os.remove(src_img_path)
                os.remove(img_path)
                return self.get_res(msg_type=7, media_id=url, file_type=1)
            else:
                return self.get_res(content="服务不可用，请稍后再试。")
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
        hf_token = get_config("hf_token")
        res = req_text2img("KingNish/Realtime-FLUX", prompt, width, height, id, hf_token)
        res_img = Image.open(res)
        img_path = f'./data/{id}.png'
        res_img.save(img_path, 'PNG')
        has_up, url = self.uploader.upload(img_path)
        if has_up:
            os.remove(img_path)
            return self.get_res(msg_type=7, media_id=url, file_type=1)
        else:
            return self.get_res(content="服务不可用，请稍后再试。")
        