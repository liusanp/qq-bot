# qq-bot
qq-bot

## 前置配置

### FFMPEG

```shell
apt install ffmpeg
```

### wkhtmltopdf

```shell
apt install wkhtmltopdf
```

## 服务

### 消息端

```shell
# 消息端，负责接收和发送消息。需要固定IP启动。
python qq-bot.py
```

### 服务端

```shell
# 服务端，负责处理消息。可以和消息端部署在不同服务器。配置
python bot-backend.py
```