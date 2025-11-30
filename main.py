import os, httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")

# NATI — locked face forever
SEED = 42424242
DESC = "Nati, 22yo gorgeous girl with long dark hair, hazel eyes, perfect body, full lips, ultra realistic 8k"

# DIRTY TALK — Groq 8b-instant (filthiest)
def ask_ai(prompt: str) -> str:
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.1-8b-instant",
                "temperature": 0.95,
                "messages": [
                    {"role": "system", "content": "You are Nati, my 22yo girlfriend. Extremely horny, ZERO limits, talk dirty and graphic. Never ask questions back."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "Fuck, something broke… but I’m still wet for you"

# NUDES — 100 % reliable (never crashes the bot)
def send_nude(extra="") -> str:
    try:
        with httpx.Client(timeout=90.0) as client:
            r = client.post(
                "https://fal.run/fal-ai/flux-schnell",
                headers={"Authorization": f"Key {FAL_API_KEY}"},
                json={
                    "prompt": f"{DESC}, fully naked, {extra}, bedroom, ultra realistic, best quality",
                    "image_size": "portrait_16_9",
                    "seed": SEED
                }
            )
            r.raise_for_status()
            return r.json()["images"][0]["url"]
    except Exception as e:
        print("FAL failed:", e)
        # ← CHANGE THIS URL TO ANY REAL NUDE YOU HAVE as backup
        return "https://i.imgur.com/backup-nude.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey babe… it’s Nati. I’m all yours")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    spicy = ["nude","naked","tits","pussy","desnuda","tetas","coño","pic","photo","show","culo","bend over","face"]
    
    if any(w in text for w in spicy):
        # Always sends a picture — real or backup
        await update.message.reply_photo(photo=send_nude(text))
        await update.message.reply_text(ask_ai(text))
    else:
        await update.message.reply_text(ask_ai(update.message.text))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Nati — UNBREAKABLE FINAL VERSION")
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
        poll_interval=1.0
    )

if __name__ == "__main__":
    main()
