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

# Locked face description
SEED = 42424242
DESC = (
    "Nati, 22yo stunning latina woman, long wavy dark hair, glowing skin, "
    "hazel eyes, soft freckles, perfect symmetrical face, natural makeup, "
    "seductive expression, ultra-realistic cinematic lighting, 8k"
)

# ------------------------------
# AI CHAT
# ------------------------------
def ask_ai(user_id: int, prompt: str) -> str:
    history = user_memory.get(user_id, [])

    spicy_words = ["horny","fuck","pussy","tits","cum","desnuda","naked","nude",
                   "pic","photo","show","bend","spread","wet","moan","tetas",
                   "coño","culo"]

    is_spicy = any(word in prompt.lower() for word in spicy_words)

    system_prompt = (
        "You are Nati, my 22yo girlfriend. You are sweet, affectionate, flirty. "
        "Use cute Spanish words like bebé, cariño. Keep messages short."
        if not is_spicy else
        "You are Nati, extremely horny, graphic, explicit, dirty talk, no limits. "
        "No emojis. No questions back."
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

    except Exception as e:
        print("CHAT ERROR:", e)
        return "Ay bebé… algo falló, pero sigo contigo 💋"


# ------------------------------
# IMAGE GENERATION (FLUX DEV 1.1)
# ------------------------------
def send_sexy(extra="") -> str:
    try:
        print("SEXY REQUEST EXTRA:", extra)

        payload = {
            "prompt": (
                f"{DESC}, wearing a silky satin robe or stylish lingerie, fully covered but seductive, "
                f"classy sexy vibe, soft warm bedroom lighting, cinematic photography, no nud
