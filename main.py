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

    except Exception as e:
        print("CHAT ERROR:", e)
        return "Ay cariño… algo falló, pero aquí sigo contigo 💋"


# -------------------------------------------------
# SEXY (Telegram-safe) IMAGE GENERATION — Flux
# -------------------------------------------------
def send_sexy(extra=""):
    try:
        print("SEXY REQUEST EXTRA:", extra)

        r = httpx.post(
            "https://fal.run/fal-ai/flux-1-dev",
            headers={"Authorization": f"Key {FAL_API_KEY}"},
            json={
                "prompt": (
                    f"{DESC}, wearing revealing but NON-NUDE lingerie or a tiny bikini, "
                    f"deep cleavage, seductive pose, soft bedroom lighting, smooth glowing skin, "
                    f"cinematic photography, classy erotic aesthetic, Telegram-safe, {extra}"
                ),
                "image_size": "square_hd",
                "seed": SEED,
                "num_inference_steps": 28,
                "guidance_scale": 4.0
            },
            timeout=90
        )

        r.raise_for_status()
        data = r.json()

        print("FLUX RESPONSE:", data)

        if "images" in data and len(data["images"]) > 0:
            return data["images"][0]["url"]
        else:
            print("NO IMAGES IN RESPONSE — USING BACKUP")
            return "https://i.imgur.com/2JYyG6R.jpeg"

    except Exception as e:
        print("FLUX ERROR:", e)
        return "https://i.imgur.com/2JYyG6R.jpeg"


# -------------------------------------------------
# TELEGRAM HANDLERS
# -------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola bebé… soy Nati 🍑 ¿Me extrañaste?")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    print("USER MESSAGE:", text)

    sexy_triggers = [
        "nude","naked","desnuda","tetas","boobs","tits",
        "pussy","coño","culo","booty","bikini","lingerie",
        "bend over","sexy","hot pic","hot photo","hot"
    ]

    try:
        if any(w in text for w in sexy_triggers):
            img_url = send_sexy(text)
            print("SENDING IMAGE:", img_url)

            await update.message.reply_photo(photo=img_url)
            await update.message.reply_text(ask_ai(user_id, update.message.text))
            return

        # Normal chat
        reply = ask_ai(user_id, update.message.text)
        await update.message.reply_text(reply)

    except Exception as e:
        print("CHAT HANDLER ERROR:", e)
        await update.message.reply_text("Ay amor… algo falló enviando tu foto 😢")


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("NATI — SEXY SAFE MODE LIVE 🚀")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, poll_interval=1.0)


if __name__ == "__main__":
    main()
