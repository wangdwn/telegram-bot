import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 配置
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8288157221:AAH7IDXYcZAsjrY9uHAmxKvDRvLw44FBoTs")
DEEPSEEK_API_KEY = "sk-47fe72a58b884a64a6b35374782f5113"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("你好！我是智能助手小帮✌️\n\n可以：\n- 聊天问答\n- 查天气 城市名\n- 查新闻\n\n随便问我～")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""可用命令：
/start - 开始
/help - 帮助
/weather 城市 - 查天气
/news - 最新新闻

也可以直接发消息问我！""")

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args) if context.args else "广州"
    try:
        r = requests.get(f"https://wttr.in/{city}?format=3", timeout=5)
        await update.message.reply_text(r.text)
    except:
        await update.message.reply_text("查询天气失败～")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get("https://news.google.com/rss?hl=zh-CN&gl=CN&ceid=CN:zh-Hans", timeout=10)
        import re
        titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', r.text)[:5]
        msg = "📰 今日新闻：\n\n" + "\n\n".join([f"{i+1}. {t}" for i,t in enumerate(titles)])
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"获取新闻失败: {e}")

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    try:
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 500
        }
        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(reply[:4000])
        else:
            await update.message.reply_text(f"AI回答失败: {r.status_code} - 请检查API Key")
    except Exception as e:
        await update.message.reply_text(f"出错了: {str(e)[:200]}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ai_chat(update, context)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    print("🤖 Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
