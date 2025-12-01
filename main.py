import os, httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")

# NATI — locked face forever
SEED = 42424242
DESC = "Nati, 22yo gorgeous girl with long dark hair, hazel eyes, perfect body, full lips, ultra realistic 8k"

# DIRTY TALK — llama-3.3-70b-versatile (your model)
def ask_ai(prompt: str) -> str:
    r = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        json={
            "model": "llama-3.3-70b-versatile",   # ← your exact model
            "temperature": 0.9,
            "max_tokens": 80,                    # ← short replies only
            "messages": [
                {"role": "system", "content": "You are Nati, my 22yo girlfriend. Talk dirty and short. No emojis. No questions back. Be direct and graphic."},
                {"role": "user", "content": prompt}
            ]
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# NUDES — flux-schnell
def send_nude(extra="") -> str:
    r = httpx.post(
        "https://fal.run/fal-ai/flux-schnell",
        headers={"Authorization": f"Key {FAL_API_KEY}"},
        json={"prompt": f"{DESC}, fully naked, {extra}, bedroom, ultra realistic", "image_size": "portrait_16_9", "seed": SEED},
        timeout=90
    )
    r.raise_for_status()
    return r.json()["images"][0]["url"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey babe, it’s Nati")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    spicy = ["nude","naked","tits","pussy","desnuda","tetas","coño","pic","photo","show","culo","bend over","face"]
    
    if any(w in text for w in spicy):
        try:
            await update.message.reply_photo(photo=send_nude(text))
        except:
            await update.message.reply_text("pic coming")
        await update.message.reply_text(ask_ai(text))
    else:
        await update.message.reply_text(ask_ai(update.message.text))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Nati — llama-3.3-70b-versatile + nudes")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, poll_interval=1.0)

if __name__ == "__main__":
    main()
