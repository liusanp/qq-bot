import requests
import json
from datetime import datetime
import os
from urllib.parse import quote
from src.utils.config import get as get_config
from src.client.base_ability import Upload
from src.utils.config import get as get_config
from botpy import logging


_log = logging.get_logger()


def get_today_str():
    today = datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    return date_str


class AlistUpload(Upload):
    
    def __init__(self) -> None:
        self.alist_url = get_config("alist_url")
        self.alist_username = get_config("alist_username")
        self.alist_password = get_config("alist_password")
        self.alist_token = get_config("alist_token")
        self.alist_token_date = get_config("alist_token_date")
        self.alist_show_url = get_config("alist_show_url")
        self.alist_bash_path = get_config("alist_bash_path")

    def get_token(self):
        today_str = get_today_str()
        if not self.alist_token or today_str != self.alist_token_date:
            uri = "/api/auth/login"
            payload = json.dumps({
                "username": self.alist_username,
                "password": self.alist_password
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("post", self.alist_url + uri, headers=headers, data=payload)
            res_json = response.json()
            if res_json['code'] == 200:
                data = res_json['data']
                self.alist_token = data['token']
                self.alist_token_date = today_str
        # print(alist_token_date)
        # print(alist_token)

    def get_dir_info(self, path, refresh=False):
        self.get_token()
        uri = "/api/fs/get"
        payload = json.dumps({
            "path": path,
            "password": "",
            "page": 1,
            "per_page": 0,
            "refresh": refresh
        })
        headers = {
            'Authorization': self.alist_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("post", self.alist_url + uri, headers=headers, data=payload)
        res_json = response.json()
        if res_json['code'] == 200:
            return True, res_json['data']
        else:
            return False, {}
    
    def get_dir_list(self, path, refresh=True):
        self.get_token()
        uri = "/api/fs/list"
        payload = json.dumps({
            "path": path,
            "password": "",
            "page": 1,
            "per_page": 10,
            "refresh": refresh
        })
        headers = {
            'Authorization': self.alist_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("post", self.alist_show_url + uri, headers=headers, data=payload)
        res_json = response.json()
        if res_json['code'] == 200:
            return True, res_json['data']
        else:
            return False, {}
    
    def create_dir(self, path):
        self.get_token()
        uri = "/api/fs/mkdir"
        payload = json.dumps({
            "path": path
        })
        headers = {
            'Authorization': self.alist_token,
            'Content-Type': 'application/json'
        }
        response = requests.request("post", self.alist_url + uri, headers=headers, data=payload)
        res_json = response.json()
        return res_json['code'] == 200

    def upload_file(self, file_path, upload_path):
        self.get_token()
        file_name = os.path.basename(file_path)
        up_file_path = quote(upload_path + '/' + file_name, 'utf-8')
        uri = "/api/fs/form"
        payload = {}
        files=[
            ('file',(file_name, open(file_path, 'rb'), 'application/octet-stream'))
        ]
        headers = {
            'Authorization': self.alist_token,
            # 'Content-Type': 'multipart/form-data',
            'File-Path': up_file_path
        }
        response = requests.request("put", self.alist_url + uri, headers=headers, data=payload, files=files)
        _log.info("upload res:" + response.text)
        res_json = response.json()
        return res_json['code'] == 200, self.alist_show_url + upload_path + '/' + file_name


    def upload(self, file_path):
        today_str = get_today_str()
        has_created, _ = self.get_dir_info(self.alist_bash_path + today_str)
        if not has_created:
            _log.info("创建当日文件夹：", today_str)
            has_created = self.create_dir(self.alist_bash_path + today_str)
        if has_created:
            _log.info("上传文件：", file_path)
            has_up, f_url = self.upload_file(file_path, self.alist_bash_path + today_str)
            _log.info("file_url:", f_url)
            self.get_dir_list(self.alist_bash_path + today_str)
            return has_up, f_url
        return False, ""
    
    
if __name__ == '__main__':
    # get_token()
    pass
