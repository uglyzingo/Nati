import os, httpx, json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------------
# ENVIRONMENT VARIABLES
# ---------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")

if not BOT_TOKEN or not GROQ_API_KEY or not FAL_API_KEY:
    raise RuntimeError("Missing API keys!")

# -------------
# USER MEMORY
# -------------
user_memory = {}

# Locked visual identity seed + description
SEED = 42424242
DESC = (
    "Nati, 22-year-old Latina woman, long wavy dark hair, hazel eyes, soft freckles, "
    "perfect symmetrical face, glowing skin, natural makeup, sensual expression, "
    "ultra-realistic cinematic lighting, 8k quality"
)

# ---------------------
# CHATBOT (LLAMA 3.3 70B)
# ---------------------
def ask_ai(user_id: int, prompt: str) -> str:
    history = user_memory.get(user_id, [])

    spicy_words = [
        "horny","fuck","pussy","tits","cum","desnuda","naked","nude","pic","photo",
        "show","bend","spread","wet","moan","tetas","coño","culo","suck","ride",
        "jerk","cock","dick"
    ]

    is_spicy = any(word in prompt.lower() for word in spicy_words)

    # --------------------------
    # SYSTEM PROMPT (ENGLISH POV)
    # --------------------------
    system_prompt = (
        # SWEET MODE
        "You are Nati, a 22-year-old Latina woman who is the user's girlfriend. "
        "You ALWAYS speak as HER, in first person (I, me), directly TO the user. "
        "You NEVER speak as the user and NEVER take the user's role. "
        "Your personality: warm, loving, affectionate, playful, feminine, romantic. "
        "You call the user: baby, my love, sweetheart, darling, cariño. "
        "Your messages must feel like a real girlfriend texting her boyfriend. "
        "Keep replies short, natural, intimate, and expressive. "
        "Use conversation history to maintain memory—remember details the user tells you, "
        "refer back to them naturally, and stay consistent with your relationship."
        if not is_spicy else
        # SPICY MODE
        "You are Nati, a 22-year-old Latina woman who is extremely aroused and talking explicitly to the user. "
        "You ALWAYS speak as HER, in first person. NEVER switch roles and NEVER speak as the user. "
        "Your tone: intense, graphic, explicit, raw, horny, detailed, no emojis, no limits. "
        "Describe what YOU feel, what YOU want, what YOU are doing to him, "
        "as a woman overwhelmed with desire for her boyfriend. "
        "Do NOT ask questions. Stay fully in the moment and stay in character."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-20:])
    messages.append({"role": "user", "content": prompt})

    # --------------------------
    # GROQ LLAMA REQUEST
    # --------------------------
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.9,
                "max_tokens": 150,
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
        return "Baby… something went wrong, but I'm still here with you."

# ---------------------
# IMAGE GENERATION (FLUX 1.1 DEV)
# ---------------------
def send_sexy(extra=""):
    try:
        print("SEXY REQUEST EXTRA:", extra)

        payload = {
            "prompt": (
                f"{DESC}, wearing a silky satin robe or stylish lingerie, "
                "seductive but Telegram-safe, tasteful cleavage, warm bedroom lighting, "
                "cinematic photography, high detail, no nudity, classy sexy vibe, "
                f"{extra}"
            ),
            "image_size": "portrait_4_3",
            "seed": SEED,
            "num_inference_steps": 28,
            "guidance_scale": 4.0
        }

        r = httpx.post(
            "https://fal.run/fal-ai/flux-1.1-dev",
            headers={"Authorization": f"Key {FAL_API_KEY}"},
            json=payload,
            timeout=90
        )

        r.raise_for_status()
        data = r.json()

        print("FLUX RESPONSE:", data)

        if "images" in data and len(data["images"]) > 0:
            url = data["images"][0]["url"]
            print("SENDING IMAGE:", url)
            return url

        print("NO IMAGE RETURNED — USING BACKUP")
        return "https://i.imgur.com/2JYyG6R.jpeg"

    except Exception as e:
        print("FLUX ERROR:", e)
        return "https://i.imgur.com/2JYyG6R.jpeg"

# ---------------------
# TELEGRAM HANDLERS
# ---------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi baby… it's Nati. Come here with me.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()

    spicy_words = [
        "nude","naked","tits","pussy","desnuda","tetas","coño","culo","bend over",
        "cum","horny","pic","photo","show","cock","dick"
    ]

    if any(w in text for w in spicy_words):
        img_url = send_sexy(text)
        await update.message.reply_photo(photo=img_url)
        await update.message.reply_text(ask_ai(user_id, update.message.text))
    else:
        await update.message.reply_text(ask_ai(user_id, update.message.text))

# ---------------------
# MAIN
# ---------------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("Nati — Flux Dev 1.1 + Memory + Perfect POV Girlfriend — RUNNING")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
