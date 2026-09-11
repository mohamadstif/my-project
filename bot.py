# -*- coding: utf-8 -*-
"""
بوت قرآن كريم على تيليجرام - نسخة بقائمة أزرار ثابتة بالأسفل (Reply Keyboard)
==============================================================================
شبيه بالبوتات الاحترافية (مثل Quran Bot) مع:
- قائمة أزرار ثابتة أسفل الشاشة (لا تختفي أبداً)
- تصفح بصفحات (زر "التالي" / "السابق")
- اختيار القارئ بالحرف الأول من اسمه أو "الكل"
- ثلاث طرق للاختيار المتقدم: بالسورة / بالقارئ / بالرواية
- زر "اختيار قارئ آخر" و "القائمة الرئيسية" في كل شاشة استماع

المصادر:
- نصوص وترجمات القرآن: https://alquran.cloud/api
- بيانات القراء (أكثر من 60 قارئاً بجميع الروايات): https://www.mp3quran.net/api/v3

التشغيل:
    pip install -r requirements.txt
    export BOT_TOKEN="التوكن"
    python bot.py
"""

import os
import random
import logging

import httpx
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("quran_bot")

# ------------------------------------------------------------------
# الإعدادات الثابتة
# ------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "ضع_التوكن_هنا")
CHANNEL_USERNAME = "x7oly"
CHANNEL_URL = f"https://t.me/{CHANNEL_USERNAME}"

QURAN_API = "https://api.alquran.cloud/v1"
MP3QURAN_API = "https://www.mp3quran.net/api/v3"

PAGE_SIZE = 10
TELEGRAM_MSG_LIMIT = 3800

SURAHS = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف",
    "الأنفال", "التوبة", "يونس", "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
    "النحل", "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج", "المؤمنون",
    "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص",
    "الزمر", "غافر", "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
    "الأحقاف", "محمد", "الفتح", "الحجرات", "ق", "الذاريات", "الطور", "النجم",
    "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك",
    "القلم", "الحاقة", "المعارج", "نوح", "الجن", "المزمل", "المدثر",
    "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس", "التكوير",
    "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى",
    "الغاشية", "الفجر", "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين",
    "العلق", "القدر", "البينة", "الزلزلة", "العاديات", "القارعة", "التكاثر",
    "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثر", "الكافرون",
    "النصر", "المسد", "الإخلاص", "الفلق", "الناس",
]

LANGUAGES = {
    "ar": ("العربية (نص المصحف)", "quran-uthmani"),
    "en": ("English", "en.sahih"),
    "fr": ("Français", "fr.hamidullah"),
    "ur": ("اردو", "ur.jalandhry"),
    "id": ("Bahasa Indonesia", "id.indonesian"),
    "tr": ("Türkçe", "tr.diyanet"),
    "ru": ("Русский", "ru.kuliev"),
    "es": ("Español", "es.cortes"),
    "de": ("Deutsch", "de.aburida"),
    "fa": ("فارسی", "fa.ansarian"),
}

VIRTUE_TEXT = (
    "✨ *فضل قراءة القرآن الكريم*\n\n"
    "القرآن الكريم كلام الله تعالى، وقراءته عبادة عظيمة يُؤجر عليها المسلم "
    "بعدد حروفه، كما جاء في الحديث الشريف أن الحرف الواحد بعشر حسنات.\n\n"
    "ومن فضائله:\n"
    "• يكون شفيعاً لصاحبه يوم القيامة.\n"
    "• يرفع درجات قارئه في الدنيا والآخرة.\n"
    "• قراءته وتدبره سبب لطمأنينة القلب وشفاء الصدور.\n"
    "• أهل القرآن هم أهل الله وخاصته."
)

MORNING_ATHKAR_TEXT = (
    "🌅 *أذكار الصباح*\n\n"
    "1. آية الكرسي.\n"
    "2. سورة الإخلاص، والفلق، والناس (ثلاث مرات).\n"
    "3. \"أصبحنا وأصبح الملك لله...\" إلى آخر الذكر.\n"
    "4. \"اللهم بك أصبحنا، وبك أمسينا...\"\n"
    "5. سيد الاستغفار.\n"
    "6. \"اللهم عافني في بدني...\"\n"
    "7. \"حسبي الله لا إله إلا هو...\" (سبع مرات).\n"
    "8. التسبيح والتحميد والتهليل والتكبير.\n\n"
    "_يمكنك استبدال هذا النص بالنص الكامل الذي تفضّله._"
)

EVENING_ATHKAR_TEXT = (
    "🌙 *أذكار المساء*\n\n"
    "1. آية الكرسي.\n"
    "2. سورة الإخلاص، والفلق، والناس (ثلاث مرات).\n"
    "3. \"أمسينا وأمسى الملك لله...\" إلى آخر الذكر.\n"
    "4. \"اللهم بك أمسينا، وبك أصبحنا...\"\n"
    "5. سيد الاستغفار.\n"
    "6. \"اللهم عافني في بدني...\"\n"
    "7. \"حسبي الله لا إله إلا هو...\" (سبع مرات).\n"
    "8. التسبيح والتحميد والتهليل والتكبير.\n\n"
    "_يمكنك استبدال هذا النص بالنص الكامل الذي تفضّله._"
)

# روابط اختيارية لملفات صوتية مباشرة (mp3) أو مسارات على خادمك
MORNING_ATHKAR_AUDIO = ""
EVENING_ATHKAR_AUDIO = ""

# روابط اختيارية لملفات PDF (مصحف / تفسير) لديك
QURAN_PDF_URL = ""
TAFSIR_PDF_URL = ""

# ------------------------------------------------------------------
# نصوص أزرار القائمة (تُستخدم كنص الرسالة عند الضغط، لأنها Reply Keyboard)
# ------------------------------------------------------------------
BTN_MUSHAF = "📖 المصحف"
BTN_RECITERS = "🎙️ القراء"
BTN_RIWAYAT = "📜 الروايات"
BTN_RANDOM = "🎲 عشوائي"
BTN_QUICK = "⚡ اختيار سريع"
BTN_ADVANCED = "⚙️ اختيار متقدم"
BTN_MORNING = "🌅 أذكار الصباح"
BTN_EVENING = "🌙 أذكار المساء"
BTN_QURAN_PDF = "📕 القرآن الكريم PDF"
BTN_TAFSIR_PDF = "📚 تفسير القرآن PDF"
BTN_LANG = "🌐 تغيير اللغة"
BTN_CHANNEL = "📢 قناة البوت"

BTN_HOME = "🏠 القائمة الرئيسية"
BTN_NEXT = "➡️ التالي"
BTN_PREV = "⬅️ السابق"
BTN_ANOTHER_RECITER = "⬅️ اختيار قارئ آخر"
BTN_ANOTHER_SURAH = "⬅️ اختيار سورة أخرى"
BTN_ALL = "✨ الكل"

BTN_BY_SURAH = "📄 بالسورة"
BTN_BY_QARI = "🗣️ بالقارئ"
BTN_BY_RIWAYAH = "📻 بالرواية"
BTN_VIRTUE = "✨ فضل قراءة القرآن"

# ------------------------------------------------------------------
# ذاكرة تخزين مؤقت لبيانات القراء
# ------------------------------------------------------------------
_reciters_raw = None
_riwayat_names = None
_riwayat_groups = None
_reciters_by_id = None
_all_reciters_sorted = None
_letters = None


def normalize_letter(ch: str) -> str:
    if ch in "أإآ":
        return "ا"
    return ch


async def load_reciters():
    global _reciters_raw, _riwayat_names, _riwayat_groups
    global _reciters_by_id, _all_reciters_sorted, _letters
    if _reciters_raw is not None:
        return
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{MP3QURAN_API}/reciters", params={"language": "ar"})
        resp.raise_for_status()
        data = resp.json()
    _reciters_raw = data.get("reciters", [])

    _reciters_by_id = {r["id"]: r for r in _reciters_raw if "id" in r}
    _all_reciters_sorted = sorted(
        [(r.get("name", "قارئ"), r["id"]) for r in _reciters_raw if "id" in r],
        key=lambda x: x[0],
    )
    _letters = sorted({normalize_letter(name[0]) for name, _ in _all_reciters_sorted if name})

    groups, order = {}, []
    for reciter in _reciters_raw:
        rec_name = reciter.get("name", "قارئ غير معروف")
        for moshaf in reciter.get("moshaf", []):
            riwayah_name = moshaf.get("name", "رواية غير محددة")
            if riwayah_name not in groups:
                groups[riwayah_name] = []
                order.append(riwayah_name)
            groups[riwayah_name].append((rec_name, moshaf))
    _riwayat_names = order
    _riwayat_groups = groups


def get_all_reciters():
    return _all_reciters_sorted or []


def get_letters():
    return _letters or []


def build_audio_url(moshaf: dict, surah_num: int) -> str:
    server = moshaf.get("server", "").rstrip("/")
    return f"{server}/{surah_num:03d}.mp3"


def surah_numbers_for_moshaf(moshaf: dict):
    raw = moshaf.get("surah_list", "")
    nums = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            nums.append(int(part))
    return nums


# ------------------------------------------------------------------
# جلب/إرسال نص القرآن والصوتيات
# ------------------------------------------------------------------
async def fetch_surah_text(surah_num: int, edition: str):
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{QURAN_API}/surah/{surah_num}/{edition}")
        resp.raise_for_status()
        data = resp.json()
    return data.get("data", {}).get("ayahs", [])


def chunk_text(text: str, limit: int = TELEGRAM_MSG_LIMIT):
    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:]
    if text:
        chunks.append(text)
    return chunks


async def send_surah_text(bot, chat_id, surah_num: int, lang_code: str):
    _, edition = LANGUAGES.get(lang_code, LANGUAGES["ar"])
    try:
        ayat = await fetch_surah_text(surah_num, edition)
    except Exception as e:
        log.exception("فشل جلب نص السورة")
        await bot.send_message(chat_id, f"⚠️ تعذّر جلب نص السورة حالياً: {e}")
        return
    header = f"📖 سورة {SURAHS[surah_num - 1]} ({surah_num})\n\n"
    body = "\n".join(f"{a['numberInSurah']}. {a['text']}" for a in ayat)
    for chunk in chunk_text(header + body):
        await bot.send_message(chat_id, chunk)


async def send_recitation(bot, chat_id, reciter_name: str, moshaf: dict, surah_num: int):
    url = build_audio_url(moshaf, surah_num)
    caption = f"🎧 {SURAHS[surah_num-1]}\nالقارئ: {reciter_name}\nالرواية: {moshaf.get('name','')}"
    try:
        await bot.send_audio(chat_id, url, caption=caption)
    except Exception:
        log.exception("فشل إرسال الصوت")
        await bot.send_message(chat_id, f"⚠️ تعذّر إرسال الملف مباشرة، رابط الاستماع:\n{url}")


# ------------------------------------------------------------------
# لوحة المفاتيح الرئيسية
# ------------------------------------------------------------------
def kb_main():
    rows = [
        [BTN_MUSHAF, BTN_RECITERS],
        [BTN_RIWAYAT, BTN_RANDOM],
        [BTN_QUICK, BTN_ADVANCED],
        [BTN_MORNING, BTN_EVENING],
        [BTN_QURAN_PDF, BTN_TAFSIR_PDF],
        [BTN_LANG, BTN_CHANNEL],
    ]
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


async def go_main(update: Update, context: ContextTypes.DEFAULT_TYPE, text="🕌 القائمة الرئيسية، اختر من الأزرار:"):
    context.user_data["step"] = "main"
    await update.message.reply_text(text, reply_markup=kb_main())


# ------------------------------------------------------------------
# محرك القوائم المُصفّحة (Pagination Engine)
# ------------------------------------------------------------------
async def show_list(update, context, prompt, items, step, extra_nav=None):
    context.user_data["step"] = step
    context.user_data["items"] = items
    context.user_data["page"] = 0
    context.user_data["prompt"] = prompt
    context.user_data["extra_nav"] = extra_nav or []
    await render_page(update, context)


async def render_page(update, context):
    items = context.user_data.get("items", [])
    page = context.user_data.get("page", 0)
    prompt = context.user_data.get("prompt", "")
    extra_nav = context.user_data.get("extra_nav", [])

    start = page * PAGE_SIZE
    chunk = items[start:start + PAGE_SIZE]

    rows, row = [], []
    candidates = {}
    for label, value in chunk:
        row.append(KeyboardButton(label))
        candidates[label] = value
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(KeyboardButton(BTN_PREV))
    if start + PAGE_SIZE < len(items):
        nav.append(KeyboardButton(BTN_NEXT))
    if nav:
        rows.append(nav)

    for label in extra_nav:
        rows.append([KeyboardButton(label)])
    rows.append([KeyboardButton(BTN_HOME)])

    context.user_data["candidates"] = candidates
    await update.message.reply_text(prompt, reply_markup=ReplyKeyboardMarkup(rows, resize_keyboard=True))


# ------------------------------------------------------------------
# تدفّق: المصحف للقراءة
# ------------------------------------------------------------------
async def start_mushaf_flow(update, context):
    items = [(f"{i+1}. {name}", i + 1) for i, name in enumerate(SURAHS)]
    await show_list(update, context, "📖 اختر سورة لقراءة نصّها:", items, "mushaf_list")


async def handle_mushaf_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    surah_num = candidates.get(text)
    if surah_num is None:
        return await update.message.reply_text("الرجاء اختيار سورة من الأزرار 🙏")
    await send_surah_text(context.bot, update.message.chat_id, surah_num, context.user_data.get("lang", "ar"))


# ------------------------------------------------------------------
# تدفّق: اختيار اللغة
# ------------------------------------------------------------------
async def start_lang_flow(update, context):
    items = [(name, code) for code, (name, _) in LANGUAGES.items()]
    await show_list(update, context, "🌐 اختر لغة عرض النصوص:", items, "lang_list")


async def handle_lang_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    code = candidates.get(text)
    if code is None:
        return await update.message.reply_text("الرجاء اختيار لغة من الأزرار 🙏")
    context.user_data["lang"] = code
    await update.message.reply_text(f"✅ تم اختيار لغة العرض: {LANGUAGES[code][0]}")
    await go_main(update, context)


# ------------------------------------------------------------------
# تدفّق: اختيار القارئ (بالحرف الأول)
# ------------------------------------------------------------------
async def start_qari_flow(update, context):
    await load_reciters()
    items = [(BTN_ALL, "ALL")] + [(letter, letter) for letter in get_letters()]
    await show_list(
        update, context,
        "🎙️ فضلاً اختر الحرف الأول من اسم القارئ، أو اختر «الكل» لعرض جميع القراء:",
        items, "qari_letter",
    )


async def handle_qari_letter(update, context, text):
    candidates = context.user_data.get("candidates", {})
    letter = candidates.get(text)
    if letter is None:
        return await update.message.reply_text("الرجاء اختيار حرف من الأزرار أو «الكل» 🙏")
    all_recs = get_all_reciters()
    if letter == "ALL":
        filtered = all_recs
    else:
        filtered = [(n, i) for n, i in all_recs if normalize_letter(n[0]) == letter]
    items = [(name, rid) for name, rid in filtered]
    await show_list(update, context, "🎙️ فضلاً اختر القارئ المراد الاستماع له:", items, "qari_list")


async def handle_qari_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    reciter_id = candidates.get(text)
    if reciter_id is None:
        return await update.message.reply_text("الرجاء اختيار قارئ من الأزرار 🙏")
    reciter = _reciters_by_id.get(reciter_id)
    if not reciter:
        return await update.message.reply_text("⚠️ تعذّر إيجاد بيانات القارئ، حاول مجدداً.")
    context.user_data["sel_reciter_name"] = reciter.get("name", "قارئ")
    context.user_data["sel_reciter_moshaf_list"] = reciter.get("moshaf", [])
    items = [(m.get("name", "رواية"), idx) for idx, m in enumerate(reciter.get("moshaf", []))]
    await show_list(
        update, context,
        f"📜 فضلاً اختر الرواية المراد الاستماع لها:\nالقارئ: {reciter.get('name','')}",
        items, "qari_riwayat",
    )


async def handle_qari_riwayah_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    idx = candidates.get(text)
    moshaf_list = context.user_data.get("sel_reciter_moshaf_list", [])
    if idx is None or idx >= len(moshaf_list):
        return await update.message.reply_text("الرجاء اختيار رواية من الأزرار 🙏")
    moshaf = moshaf_list[idx]
    context.user_data["sel_moshaf"] = moshaf
    nums = surah_numbers_for_moshaf(moshaf)
    items = [(f"{n}. {SURAHS[n-1]}", n) for n in nums if 1 <= n <= 114]
    reciter_name = context.user_data.get("sel_reciter_name", "")
    context.user_data["on_extra_nav"] = start_qari_flow
    await show_list(
        update, context,
        f"🎧 فضلاً اختر السورة المراد الاستماع لها:\nالقارئ: {reciter_name}\nالرواية: {moshaf.get('name','')}",
        items, "qari_surahs", extra_nav=[BTN_ANOTHER_RECITER],
    )


# ------------------------------------------------------------------
# تدفّق: اختيار الرواية أولاً
# ------------------------------------------------------------------
async def start_riwayah_flow(update, context):
    await load_reciters()
    items = [(name, name) for name in _riwayat_names]
    await show_list(update, context, "📜 فضلاً اختر الرواية:", items, "riwayah_list")


async def handle_riwayah_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    riwayah_name = candidates.get(text)
    if riwayah_name is None:
        return await update.message.reply_text("الرجاء اختيار رواية من الأزرار 🙏")
    context.user_data["sel_riwayah_name"] = riwayah_name
    recs = _riwayat_groups.get(riwayah_name, [])
    context.user_data["riwayah_reciter_tuples"] = recs
    items = [(name, idx) for idx, (name, _) in enumerate(recs)]
    await show_list(
        update, context, f"🎙️ فضلاً اختر القارئ:\nالرواية: {riwayah_name}",
        items, "riwayah_reciters",
    )


async def back_to_riwayah_reciters(update, context):
    riwayah_name = context.user_data.get("sel_riwayah_name", "")
    recs = context.user_data.get("riwayah_reciter_tuples", [])
    items = [(name, idx) for idx, (name, _) in enumerate(recs)]
    await show_list(
        update, context, f"🎙️ فضلاً اختر القارئ:\nالرواية: {riwayah_name}",
        items, "riwayah_reciters",
    )


async def handle_riwayah_reciter_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    idx = candidates.get(text)
    recs = context.user_data.get("riwayah_reciter_tuples", [])
    if idx is None or idx >= len(recs):
        return await update.message.reply_text("الرجاء اختيار قارئ من الأزرار 🙏")
    name, moshaf = recs[idx]
    context.user_data["sel_reciter_name"] = name
    context.user_data["sel_moshaf"] = moshaf
    nums = surah_numbers_for_moshaf(moshaf)
    items = [(f"{n}. {SURAHS[n-1]}", n) for n in nums if 1 <= n <= 114]
    context.user_data["on_extra_nav"] = back_to_riwayah_reciters
    await show_list(
        update, context, f"🎧 فضلاً اختر السورة:\nالقارئ: {name}",
        items, "riwayah_surahs", extra_nav=[BTN_ANOTHER_RECITER],
    )


# ------------------------------------------------------------------
# معالج مشترك: اختيار سورة لبثّها صوتياً (يخدم qari_surahs و riwayah_surahs)
# ------------------------------------------------------------------
async def handle_recitation_surah_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    surah_num = candidates.get(text)
    if surah_num is None:
        return await update.message.reply_text("الرجاء اختيار سورة من الأزرار 🙏")
    reciter_name = context.user_data.get("sel_reciter_name", "قارئ")
    moshaf = context.user_data.get("sel_moshaf")
    if not moshaf:
        return await update.message.reply_text("⚠️ حدث خطأ، الرجاء البدء من جديد.")
    await send_recitation(context.bot, update.message.chat_id, reciter_name, moshaf, surah_num)


# ------------------------------------------------------------------
# تدفّق: الاختيار المتقدم (بالسورة / بالقارئ / بالرواية)
# ------------------------------------------------------------------
async def start_advanced_menu(update, context):
    items = [
        (BTN_BY_SURAH, "surah"),
        (BTN_BY_QARI, "qari"),
        (BTN_BY_RIWAYAH, "riwayah"),
        (BTN_VIRTUE, "virtue"),
    ]
    await show_list(update, context, "⚙️ اختر طريقة الاختيار المتقدم:", items, "advanced_menu")


async def handle_advanced_menu(update, context, text):
    candidates = context.user_data.get("candidates", {})
    value = candidates.get(text)
    if value == "surah":
        await start_surah_search_flow(update, context)
    elif value == "qari":
        await start_qari_flow(update, context)
    elif value == "riwayah":
        await start_riwayah_flow(update, context)
    elif value == "virtue":
        await update.message.reply_text(VIRTUE_TEXT, parse_mode=ParseMode.MARKDOWN)
        await go_main(update, context)
    else:
        await update.message.reply_text("الرجاء الاختيار من الأزرار 🙏")


# ------------------------------------------------------------------
# تدفّق: البحث بالسورة (اختر سورة أولاً ثم اعرض القراء المتوفرين لها)
# ------------------------------------------------------------------
async def start_surah_search_flow(update, context):
    await load_reciters()
    items = [(f"{i+1}. {name}", i + 1) for i, name in enumerate(SURAHS)]
    await show_list(update, context, "📄 اختر السورة:", items, "surah_search_list")


async def handle_surah_search_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    surah_num = candidates.get(text)
    if surah_num is None:
        return await update.message.reply_text("الرجاء اختيار سورة من الأزرار 🙏")
    context.user_data["sel_search_surah"] = surah_num

    matches = []
    for reciter in _reciters_raw or []:
        rname = reciter.get("name", "قارئ")
        for m in reciter.get("moshaf", []):
            if surah_num in surah_numbers_for_moshaf(m):
                matches.append((f"{rname} - {m.get('name','')}", (rname, m)))

    context.user_data["search_matches"] = matches
    items = [(label, idx) for idx, (label, _) in enumerate(matches)]
    context.user_data["on_extra_nav"] = start_surah_search_flow
    await show_list(
        update, context,
        f"🎧 القراء المتوفرون لسورة {SURAHS[surah_num-1]}:",
        items, "surah_search_reciters", extra_nav=[BTN_ANOTHER_SURAH],
    )


async def handle_surah_search_reciter_select(update, context, text):
    candidates = context.user_data.get("candidates", {})
    idx = candidates.get(text)
    matches = context.user_data.get("search_matches", [])
    if idx is None or idx >= len(matches):
        return await update.message.reply_text("الرجاء اختيار قارئ من الأزرار 🙏")
    _, (reciter_name, moshaf) = matches[idx]
    surah_num = context.user_data.get("sel_search_surah")
    await send_recitation(context.bot, update.message.chat_id, reciter_name, moshaf, surah_num)


# ------------------------------------------------------------------
# القائمة الرئيسية: التوزيع
# ------------------------------------------------------------------
async def handle_main_menu(update, context, text):
    if text == BTN_MUSHAF:
        await start_mushaf_flow(update, context)
    elif text == BTN_RECITERS:
        await start_qari_flow(update, context)
    elif text == BTN_RIWAYAT:
        await start_riwayah_flow(update, context)
    elif text == BTN_RANDOM:
        surah_num = random.randint(1, 114)
        await update.message.reply_text(f"🎲 السورة المختارة: {SURAHS[surah_num-1]}")
        await send_surah_text(context.bot, update.message.chat_id, surah_num, context.user_data.get("lang", "ar"))
    elif text == BTN_QUICK:
        await start_qari_flow(update, context)
    elif text == BTN_ADVANCED:
        await start_advanced_menu(update, context)
    elif text == BTN_MORNING:
        await update.message.reply_text(MORNING_ATHKAR_TEXT, parse_mode=ParseMode.MARKDOWN)
        if MORNING_ATHKAR_AUDIO:
            await context.bot.send_audio(update.message.chat_id, MORNING_ATHKAR_AUDIO, caption="🎧 أذكار الصباح")
    elif text == BTN_EVENING:
        await update.message.reply_text(EVENING_ATHKAR_TEXT, parse_mode=ParseMode.MARKDOWN)
        if EVENING_ATHKAR_AUDIO:
            await context.bot.send_audio(update.message.chat_id, EVENING_ATHKAR_AUDIO, caption="🎧 أذكار المساء")
    elif text == BTN_QURAN_PDF:
        if QURAN_PDF_URL:
            await context.bot.send_document(update.message.chat_id, QURAN_PDF_URL, caption="📕 القرآن الكريم")
        else:
            await update.message.reply_text("⚠️ لم يُضبط رابط ملف PDF بعد. أضِفه في متغيّر QURAN_PDF_URL بالكود.")
    elif text == BTN_TAFSIR_PDF:
        if TAFSIR_PDF_URL:
            await context.bot.send_document(update.message.chat_id, TAFSIR_PDF_URL, caption="📚 تفسير القرآن")
        else:
            await update.message.reply_text("⚠️ لم يُضبط رابط ملف PDF بعد. أضِفه في متغيّر TAFSIR_PDF_URL بالكود.")
    elif text == BTN_LANG:
        await start_lang_flow(update, context)
    elif text == BTN_CHANNEL:
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("📢 انضم إلى القناة", url=CHANNEL_URL)]])
        await update.message.reply_text("قناة البوت:", reply_markup=kb)
    else:
        await update.message.reply_text("الرجاء استخدام الأزرار بالأسفل 🙏", reply_markup=kb_main())


# ------------------------------------------------------------------
# المعالجات الرئيسية
# ------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["lang"] = "ar"
    await update.message.reply_text(
        "🕌 أهلاً بك في بوت القرآن الكريم\n\nاختر من القائمة أدناه:",
        reply_markup=kb_main(),
    )
    context.user_data["step"] = "main"


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data.setdefault("lang", "ar")
    step = context.user_data.get("step", "main")

    if text == BTN_HOME:
        return await go_main(update, context)

    if step != "main":
        if text == BTN_NEXT:
            context.user_data["page"] = context.user_data.get("page", 0) + 1
            return await render_page(update, context)
        if text == BTN_PREV:
            context.user_data["page"] = max(0, context.user_data.get("page", 0) - 1)
            return await render_page(update, context)
        extra_nav = context.user_data.get("extra_nav", [])
        if text in extra_nav:
            callback = context.user_data.get("on_extra_nav")
            if callback:
                return await callback(update, context)

    handlers_by_step = {
        "main": handle_main_menu,
        "mushaf_list": handle_mushaf_select,
        "lang_list": handle_lang_select,
        "advanced_menu": handle_advanced_menu,
        "qari_letter": handle_qari_letter,
        "qari_list": handle_qari_select,
        "qari_riwayat": handle_qari_riwayah_select,
        "qari_surahs": handle_recitation_surah_select,
        "riwayah_list": handle_riwayah_select,
        "riwayah_reciters": handle_riwayah_reciter_select,
        "riwayah_surahs": handle_recitation_surah_select,
        "surah_search_list": handle_surah_search_select,
        "surah_search_reciters": handle_surah_search_reciter_select,
    }
    handler = handlers_by_step.get(step, handle_main_menu)
    await handler(update, context, text)


async def on_error(update, context: ContextTypes.DEFAULT_TYPE):
    log.error("حدث خطأ: %s", context.error)


def main():
    if BOT_TOKEN in ("", "ضع_التوكن_هنا"):
        raise SystemExit("❌ لم يتم ضبط توكن البوت. عرّف متغير البيئة BOT_TOKEN.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_error_handler(on_error)

    log.info("🚀 البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
