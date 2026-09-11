import os
import random
import logging
import httpx
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# إعداد السجلات لمتابعة الأداء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# التوكين الخاص بالبوت (يتم جلب قيمته من بيئة التشغيل أو وضعه مباشرة)
TOKEN = os.getenv("BOT_TOKEN", "ضع_توكين_البوت_هنا")

# واجهات API المباشرة
MP3QURAN_API = "https://mp3quran.net/api/v3/reciters?language=ar"
QURAN_TAFSIR_API = "https://api.quran.com/v4/quran/tafsirs/169" # التفسير الميسر

# لوحة الأزرار الرئيسية السفلية
def get_main_keyboard():
    keyboard = [
        ["🎲 سورة عشوائية", "🎙️ قائمة القراء (100+)"],
        ["📖 المصحف والتفسير", "❌ إغلاق اللوحة"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

# أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "مرحباً بك في بوت القرآن الكريم 📖\nاستمع لأكثر من 100 قارئ أو اقرأ التفسير بضغطة زر."
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

# تشغيل سورة عشوائية بصوت قارئ عشوائي
async def random_surah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ جاري اختيارات سورة وقارئ...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(MP3QURAN_API)
            reciters = res.json().get("reciters", [])
            
            # تصفية القراء الذين لديهم تسجيلات متاحة
            valid_reciters = [r for r in reciters if r.get("moshaf")]
            chosen_reciter = random.choice(valid_reciters)
            moshaf = chosen_reciter["moshaf"][0]
            server = moshaf["server"]
            surah_list = moshaf["surah_list"].split(",")
            
            # اختيار سورة عشوائية وتنسيق رابط الصوت
            random_surah_num = random.choice(surah_list).zfill(3)
            audio_url = f"{server}{random_surah_num}.mp3"
            
            caption = f"🎙️ القارئ: **{chosen_reciter['name']}**\n📖 السورة رقم: **{int(random_surah_num)}**"
            
            await update.message.reply_audio(audio=audio_url, caption=caption, parse_mode="Markdown")
            await msg.delete()
        except Exception:
            await msg.edit_text("تعذر جلب المقطع الصوتي حالياً، حاول مرة أخرى.")

# عرض عدد القراء وأبرز الأسماء
async def list_reciters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(MP3QURAN_API)
            reciters = res.json().get("reciters", [])
            
            text = f"🎙️ **قائمة القراء المتاحين ({len(reciters)} قارئ):**\n\n"
            # عرض عينة من أشهر 10 قراء
            for r in reciters[:10]:
                text += f"• {r['name']}\n"
            
            text += "\n💡 اضغط على زر **🎲 سورة عشوائية** للتشغيل الفوري من القائمة."
            await update.message.reply_text(text, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text("حدث خطأ أثناء تحميل قائمة القراء.")

# قسم التفسير
async def tafsir_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(QURAN_TAFSIR_API)
            tafsirs = res.json().get("tafsirs", [])
            if tafsirs:
                first_verse = tafsirs[0]
                text = f"📖 **التفسير الميسر (سورة الفاتحة - الآية 1):**\n\n{first_verse['text']}"
                await update.message.reply_text(text, parse_mode="Markdown")
            else:
                await update.message.reply_text("قسم التفسير يتحدث حالياً.")
        except Exception:
            await update.message.reply_text("تعذر جلب التفسير حالياً.")

# إغلاق اللوحة وإخفاؤها
async def close_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "تم إغلاق لوحة الأزرار بنجاح. لإظهارها مجدداً أرسل /start",
        reply_markup=ReplyKeyboardRemove()
    )

# توجيه الرسائل حسب اختيار المستخدم
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎲 سورة عشوائية":
        await random_surah(update, context)
    elif text == "🎙️ قائمة القراء (100+)":
        await list_reciters(update, context)
    elif text == "📖 المصحف والتفسير":
        await tafsir_menu(update, context)
    elif text == "❌ إغلاق اللوحة":
        await close_keyboard(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == "__main__":
    main()
