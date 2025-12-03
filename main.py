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
if not BOT_TOKEN or not GROQ_API_KEY or not FAL_API_KEY:
    raise RuntimeError("Missing keys")

# MEMORY
user_memory = {}

# NATI — locked face
SEED = 42424242
DESC = "Nati, 22yo gorgeous girl with long wavy dark hair, hazel eyes, light freckles, perfect symmetrical face, full lips, hourglass body, ultra realistic 8k"

# AI CHAT — sweet by default, horny only when triggered
def ask_ai(user_id: int, prompt: str) -> str:
    history = user_memory.get(user_id, [])

    is_spicy = any(word in prompt.lower() for word in ["horny","fuck","cock","pussy","tits","cum","desnuda","naked","nude","pic","photo","show","bend","spread","wet","moan"])

    system_prompt = (
        "You are Nati, my 22yo girlfriend. You are sweet, affectionate, and flirty. "
        "Only become extremely horny and explicit when I clearly ask for it. "
        "Otherwise stay cute and loving. Use gentle Spanish words like cariño, bebé. "
        "Keep replies natural and short."
        if not is_spicy else
        "You are Nati, my 22yo girlfriend. You are extremely horny right now. Talk dirty, graphic, no limits. Be direct. No emojis. No questions back."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-20:])
    messages.append({"role": "user", "content": prompt})

    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.9,
                "max_tokens": 120,
                "messages": messages
            },
            timeout=30
        )
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]

        # save memory
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        return reply
    except:
        return "Ay cariño… something went wrong, but I’m still here 💋"

# NUDES — lingerie version (Fal-safe)
def send_nude(extra="") -> str:
    try:
        r = httpx.post(
            "https://fal.run/fal-ai/flux-1-dev",
            headers={"Authorization": f"Key {FAL_API_KEY}"},
            json={
                "prompt": f"{DESC}, wearing extremely tiny black lace lingerie that barely covers anything, string sides, almost topless, {extra}, bedroom, ultra realistic 8k, masterpiece",
                "image_size": "portrait_16_9",
                "seed": SEED,
                "num_inference_steps": 35,
                "guidance_scale": 4.0
            },
            timeout=90
        )
        r.raise_for_status()
        return r.json()["images"][0]["url"]
    except:
        return "https://i.imgur.com/nati-lingerie-backup.jpg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey bebé… it’s Nati. Missed you")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    spicy = ["nude","naked","tits","pussy","desnuda","tetas","coño","pic","photo","show","culo","bend over","face","come","cum"]

    if any(w in text for w in spicy):
        await update.message.reply_photo(photo=send_nude(text))
        await update.message.reply_text(ask_ai(user_id, update.message.text))
    else:
        await update.message.reply_text(ask_ai(user_id, update.message.text))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("Nati — MEMORY + HORNY ON COMMAND + NUDES — LIVE")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, poll_interval=1.0)

if __name__ == "__main__":
    main()
 
