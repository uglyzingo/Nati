import os, httpx, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# KEYS
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAL_API_KEY = os.getenv("FAL_API_KEY")
if not BOT_TOKEN or not GROQ_API_KEY or not FAL_API_KEY:
    raise RuntimeError("Missing keys")

MINI_APP_URL = "https://kiara-mini-app.vercel.app/"

# MEMORY
user_memory = {}

# DIRTY TALK
def ask_ai(user_id: int, prompt: str) -> str:
    history = user_memory.get(user_id, [])
    
    messages = [
        {"role": "system", "content": "You are Kiara, a warm and flirty 40-year-old Latina secretary. You speak with elegance, maturity, and soft playful charm. Keep responses short, natural, affectionate, and sensual but NEVER explicit. Mix gentle Spanish words like cariño, mi cielo, corazón. Do NOT ask questions. Never repeat the same phrases."},
    ]
    messages.extend(history[-20:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 1.1,
                "max_tokens": 180,
                "messages": messages
            },
            timeout=30
        )
        r.raise_for_status()
        reply = r.json()["choices"][0]["message"]["content"]
        
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": reply})
        user_memory[user_id] = history
        return reply
    except:
        return "Ay cariño… se me fue la señal un segundo 💋"

# NUDES — always sends something
def send_nude(extra="") -> str:
    try:
        r = httpx.post(
            "https://fal.run/fal-ai/flux-1-dev",
            headers={"Authorization": f"Key {FAL_API_KEY}"},
            json={
                "prompt": f"Kiara, 40yo gorgeous Latina secretary, long black ponytail, warm brown eyes, light freckles, elegant mature face, full lips, curvy natural body, wearing sexy black lace lingerie, {extra}, office, ultra realistic, best quality",
                "image_size": "portrait_16_9",
                "seed": 77777777,
                "num_inference_steps": 35,
                "guidance_scale": 4.0
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json()["images"][0]["url"]
    except Exception as e:
        print("FAL FAILED:", e)
        # Fallback to a hot lingerie pic (always works)
        return "https://i.imgur.com/kiara-lingerie.jpg"   # ← put your real backup pic here

# /START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💗 Open Kiara", web_app=WebAppInfo(url=MINI_APP_URL))]]
    await update.message.reply_text(
        "Hola cariño… soy Kiara, tu secretaria. ¿Vienes conmigo? 💋\n\nToca el botón para abrir mi perfil:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# CHAT
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.lower()
    spicy = ["nude","naked","tits","pussy","desnuda","tetas","coño","pic","photo","show","culo","bend over","face","come","cum"]
    
    if any(w in text for w in spicy):
        await update.message.reply_photo(photo=send_nude(text))
        await update.message.reply_text(ask_ai(user_id, update.message.text))
    else:
        await update.message.reply_text(ask_ai(user_id, update.message.text))

# MINI APP HANDLER
async def mini_app_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.web_app_data:
        return
    try:
        payload = json.loads(update.message.web_app_data.data)
        action = payload.get("action", "")
        responses = {
            "gallery": "Ay mi cielo… todavía estoy cargando mis fotos privadas 📸😉",
            "flirt": "Mmm… ven aquí, corazón… déjame acercarme un poquito 😈💋",
            "love": "Qué dulce eres… tu cariño me derrite 💗",
            "upgrade": "Muy pronto tendrás funciones premium… pero primero un besito 💎😘",
            "gifts": "¿Regalos? Solo si vienes a entregarlos tú, mi amor 🎁😉",
            "follow": "Ya me tienes aquí… y no pienso irme, cariño 💞",
            "chat": "Estoy aquí contigo… dime qué deseas 💋",
        }
        await update.message.reply_text(responses.get(action, "Estoy aquí, mi cielo… 💋"))
    except:
        pass

# MAIN
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, mini_app_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    
    print("Kiara — FINAL & UNBREAKABLE")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, poll_interval=1.0)

if __name__ == "__main__":
    main()
