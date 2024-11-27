
# -*- coding: utf-8 -*-
import traceback
from sanic import Sanic
from sanic.response import text, json as sj
import xml.etree.ElementTree as ET
from src.utils.config import get as get_config
from src.server.router import route_message
import json


app = Sanic(__name__)
    
    
@app.route("/handleMsg", methods=["POST"])
async def handle_msg(request):
    # print(request.body)
    req_data = json.loads(request.body.decode("utf-8"))
    # print(req_data)
    res = await route_message(req_data)
    if res:
        return sj({'code': 0, 'msg': '消息处理成功', 'data': res.to_dict()})
    else:
        return sj({'code': 10001, 'msg': '消息处理失败', 'data': {}})



def start(ser_port=1359):
    """服务端，负责处理消息。
    :param ser_port:
    :return:
    """
    try:
        app.run(port=ser_port, host='0.0.0.0', debug=False, access_log=False, workers=2)
    except Exception as e:
        traceback.print_stack(e)


if __name__ == '__main__':
    # start(int(get_config("server_port")))
    app.run(port=int(get_config("server_port")), host='0.0.0.0', debug=False, access_log=False, workers=2)