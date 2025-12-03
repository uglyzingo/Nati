import os, httpx, json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")

# NATI — locked face
SEED = 42424242
DESC = "Nati, 22yo gorgeous girl with long wavy dark hair, hazel eyes, perfect body, full lips, ultra realistic 8k"

# MEMORY — last 4 exchanges per user
user_memory = {}

# DIRTY TALK — short, natural, horny
def ask_ai(user_id: int, prompt: str) -> str:
    history = user_memory.get(user_id, [])
    
    messages = [
        {"role": "system", "content": "You are Nati, my 22yo girlfriend. Extremely horny, no limits, talk dirty and short. No emojis. No questions back. Be direct and graphic."},
    ]
    messages.extend(history[-8:])  # last 4 exchanges
    messages.append({"role": "user", "content": prompt})
    
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.9,
                "max_tokens": 80,
                "messages": messages
            },
            timeout=30
        )
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]
        
        # save memory
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history[-20:]  # keep it small
        
        return reply
    except:
        return "Fuck… keep going"

# NUDES — flux-1-dev (100% uncensored)
def send_nude(extra="") -> str:
    r = httpx.post(
        "https://fal.run/fal-ai/flux-1-dev",
        headers={"Authorization": f"Key {FAL_API_KEY}"},
        json={
            "prompt": f"{DESC}, fully naked, {extra}, bedroom, ultra realistic, best quality",
            "image_size": "portrait_16_9",
            "seed": SEED,
            "num_inference_steps": 35,
            "guidance_scale": 4.0
        },
        timeout=90
    )
    r.raise_for_status()
    return r.json()["images"][0]["url"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey babe… it’s Nati")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    spicy = ["nude","naked","tits","pussy","desnuda","tetas","coño","pic","photo","show","culo","bend over","face","come","cum"]
    
    if any(w in text for w in spicy):
        try:
            await update.message.reply_photo(photo=send_nude(text))
        except:
            await update.message.reply_text("pic coming")
        await update.message.reply_text(ask_ai(user_id, update.message.text))
    else:
        await update.message.reply_text(ask_ai(user_id, update.message.text))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Nati — MEMORY + SHORT DIRTY + NUDES — LIVE")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, poll_interval=1.0)

if __name__ == "__main__":
    main()
