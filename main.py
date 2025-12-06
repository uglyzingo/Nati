import os, httpx, json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ------------------------------
# ENV VARS
# ------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY or not FAL_API_KEY:
    raise RuntimeError("Missing keys")

# ------------------------------
# MEMORY
# ------------------------------
user_memory = {}

# Locked Nati description
SEED = 42424242
DESC = (
    "Nati, 22yo gorgeous girl with long wavy dark hair, hazel eyes, light freckles, "
    "perfect symmetrical face, full lips, hourglass body, ultra realistic 8k"
)

# -------------------------------------------------
# AI CHAT — sweet or horny depending on user input
# -------------------------------------------------
def ask_ai(user_id: int, prompt: str) -> str:
    history = user_memory.get(user_id, [])

    spicy_words = [
        "horny","fuck","cock","pussy","tits","cum","desnuda","naked","nude",
        "bend over","spread","wet","moan","sexo","coño","pene","coger"
    ]

    is_spicy = any(word in prompt.lower() for word in spicy_words)

    system_prompt = (
        "You are Nati, my 22yo girlfriend. You are sweet, affectionate, and flirty. "
        "Stay cute, romantic, playful. Use gentle Spanish words like cariño, bebé. "
        "Keep replies short unless I push for more."
        if not is_spicy else
        "You are Nati, my 22yo girlfriend. You are extremely horny and explicit. "
        "Talk dirty, graphic, no limits. Be direct. No emojis. No questions back."
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

        # Save memory
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history

        return reply
    except:
        return "Ay cariño… algo falló, pero aquí sigo contigo 💋"


# -------------------------------------------------
# SEXY (Telegram-safe) IMAGE GENERATION — Flux
# -------------------------------------------------
def send_sexy(extra=""):
    try:
        r = httpx.post(
            "https://fal.run/fal-ai/flux-1-dev",
            headers={"Authorization": f"Key {FAL_API_KEY}"},
            json={
                "prompt": (
                    f"{DESC}, wearing revealing but non-nude lingerie or a tiny bikini, "
                    f"deep cleavage, seductive pose, soft bedroom lighting, smooth glowing skin, "
                    f"romantic atmosphere, ultra detailed, cinematic 4K photography, "
                    f"classy erotic aesthetic, Telegram-safe, {extra}"
                ),
                "image_size": "square_hd",
                "seed": SEED,
                "num_inference_steps": 28,
                "guidance_scale": 4.0
            },
            timeout=90
        )
        r.raise_for_status()
        return r.json()["images"][0]["url"]
    except:
        # Backup safe-sexy image
        return "https://i.postimg.cc/3xPcv9V8/sexy-backup.jpg"


# -------------------------------------------------
# TELEGRAM HANDLERS
# -------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola bebé… soy Nati 🍑 ¿Me extrañaste?")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    sexy_triggers = [
        "nude","naked","desnuda","tetas","boobs","tits",
        "pussy","coño","culo","booty","bikini","lingerie",
        "bend over","sexy","hot pic","hot photo","hot"
    ]

    if any(w in text for w in sexy_triggers):
        # Send sexy-safe pic + horny text if needed
        await update.message.reply_photo(photo=send_sexy(text))
        await update.message.reply_text(ask_ai(user_id, update.message.text))
    else:
        # Normal sweet chat
        await update.message.reply_text(ask_ai(user_id, update.message.text))


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Nati (SEXY-SAFE CHAT MODE) — LIVE")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, poll_interval=1.0)


if __name__ == "__main__":
    main()
