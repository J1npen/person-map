import logging
import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- 配置部分 ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_URL = 'http://localhost:8001/query'
# ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="你好！我是全能人物信息助手。\n\n你可以用自然语言对我下达指令，例如：\n"
             "1. '添加小明'\n"
             "2. '把小明的鞋码设为37'\n"
             "3. '小明喜欢什么？'\n"
             "4. '删掉小明'\n\n"
             "我会为您保存属于您的私有数据。"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    user_id = str(update.effective_user.id)  # 获取 Telegram 用户 ID 实现隔离
    
    try:
        # 调用本地 FastAPI 接口，传递 user_id
        response = requests.post(API_URL, json={"user_id": user_id, "query": user_text})
        if response.status_code == 200:
            answer = response.json().get("answer", "抱歉，处理时出现了点问题。")
        else:
            answer = f"服务响应错误: {response.status_code}"
    except Exception as e:
        answer = f"连接失败: {str(e)}"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("Telegram Bot 正在运行 (多用户隔离模式)...")
    application.run_polling()
