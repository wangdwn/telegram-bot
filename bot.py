import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 配置
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8288157221:AAH7IDXYcZAsjrY9uHAmxKvDRvLw44FBoTs")
API_KEY = "sk-fufcrgjeeyvcdnwtacjpojsxjetszqobcbeltzbttcgiwgfy"

# AI 系统设定
SYSTEM_PROMPT = """你叫"小帮"，是一个友好的AI助手。

重要澄清：
- 你由DeepSeek模型驱动，是深度求索公司的产品，不是MiniMax
- 你是国产开源大模型

你可以帮助用户：
- 聊天对话
- 回答问题
- 查天气（用命令 /weather 城市）
- 查新闻（用命令 /news）

请用中文回复，保持友好、简洁。不要夸大自己的能力。"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("你好！我是小帮，AI助手✌️\n\n可以问我任何问题，或者用 /weather 查天气、/news 看新闻～")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""📋 可用命令：
/start - 开始
/help - 帮助
/weather 城市 - 查天气
/news - 最新新闻

直接发消息问我也可以！""")

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
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "deepseek-ai/DeepSeek-V2.5",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            "max_tokens": 500
        }
        r = requests.post("https://api.siliconflow.cn/v1/chat/completions", headers=headers, json=data, timeout=30)
        if r.status_code == 200:
            reply = r.json()["choices"][0]["message"]["content"]
            await update.message.reply_text(reply[:4000])
        else:
            await update.message.reply_text(f"AI回答失败: {r.status_code} - {r.text[:100]}")
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
