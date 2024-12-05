from src.server.base_ability import Translate
from src.utils.config import get as get_config
import requests
from hashlib import md5
import random


class BaiduTranslate(Translate):
    
    def __init__(self) -> None:
        super().__init__()
        self.bd_appid = get_config("bd_appid")
        self.bd_secret = get_config("bd_secret")
    
    def trans(self, src_text):
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = 'auto'
        to_lang =  'en'

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path

        # Generate salt and sign
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(self.bd_appid + src_text + str(salt) + self.bd_secret)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': self.bd_appid, 'q': src_text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        # Send request
        r = requests.post(url, params=payload, headers=headers)
        print(r.text)
        result = r.json()
        if 'error_code' in result:
            return src_text
        else:
            return result['trans_result'][0]['dst']