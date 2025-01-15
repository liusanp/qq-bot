from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from src.client.tg_router import route_message


class TgClient():
    def __init__(self, token: str):
        self.token = token
        
    def run(self):
        application = ApplicationBuilder().token(self.token).build()
        message_handler = MessageHandler(filters.ALL, handle_message)
        application.add_handler(message_handler)
        application.run_polling()
        
        
async def handle_message(update: Update, context):
    res = await route_message(update.message)

    # 回复用户消息
    await update.message.reply_markdown_v2("test")