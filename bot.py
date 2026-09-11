# -*- coding: utf-8 -*-
"""
بوت قرآن كريم على تيليجرام
============================
المميزات:
- 📖 المصحف للقراءة (نص كامل لأي سورة، بأي لغة مختارة)
- 🎲 اختيار عشوائي لسورة
- 🌐 اختيار لغة (ترجمات متعددة عبر alquran.cloud)
- ⚙️ اختيارات متقدمة:
    - اختيار القارئ حسب القراءات العشر (بيانات القراء تُجلب مباشرة وبشكل حي
      من واجهة mp3quran.net API، وعددهم يفوق 60 قارئاً في مختلف الروايات)
    - أذكار الصباح (نص + رابط صوتي قابل للتعديل)
    - فضل قراءة القرآن (نص)
- 🔙 أزرار "رجوع" في كل قائمة فرعية
- 📢 زر ثابت للانتقال المباشر إلى قناة البوت @x7oly

المصادر المستخدمة:
- نصوص وترجمات القرآن: https://alquran.cloud/api  (مجاني، بدون مفتاح API)
- بيانات القراء والتلاوات: https://www.mp3quran.net/api/v3 (مجاني، بدون مفتاح API)

قبل التشغيل:
    pip install -r requirements.txt
    export BOT_TOKEN="ضع التوكن هنا"
    python bot.py
"""

import os
import random
import logging

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
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

PAGE_SIZE = 16          # عدد السور/القراء في كل صفحة
TELEGRAM_MSG_LIMIT = 3800  # هامش أمان أقل من حد تيليجرام (4096)

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

# رمز اللغة -> (الاسم المعروض، معرّف الإصدار في alquran.cloud)
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
    "• أهل القرآن هم أهل الله وخاصته.\n\n"
    "نسأل الله أن يجعلنا وإياكم من أهل القرآن، وأن يرزقنا تلاوته وتدبره "
    "آناء الليل وأطراف النهار."
)

MORNING_ATHKAR_TEXT = (
    "🌅 *أذكار الصباح*\n\n"
    "1. آية الكرسي.\n"
    "2. سورة الإخلاص، والفلق، والناس (ثلاث مرات).\n"
    "3. \"أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك "
    "له...\" إلى آخر الذكر.\n"
    "4. \"اللهم بك أصبحنا، وبك أمسينا، وبك نحيا، وبك نموت، وإليك النشور.\"\n"
    "5. سيد الاستغفار.\n"
    "6. \"اللهم عافني في بدني، اللهم عافني في سمعي، اللهم عافني في بصري...\"\n"
    "7. \"حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم\" (سبع مرات).\n"
    "8. التسبيح والتحميد والتهليل والتكبير.\n\n"
    "_يمكنك استبدال هذا النص بنص أذكار الصباح الكامل الذي تفضّله، وإرفاق "
    "ملف صوتي حقيقي في متغيّر MORNING_ATHKAR_AUDIO._"
)

# ضع هنا رابط ملف صوتي مباشر (mp3) لأذكار الصباح، أو مساراً محلياً لملف على
# الخادم. اتركه فارغاً إن لم يتوفر لديك ملف بعد.
MORNING_ATHKAR_AUDIO = ""  # مثال: "https://example.com/athkar_sabah.mp3"

# ------------------------------------------------------------------
# ذاكرة تخزين مؤقت لبيانات القراء (تُجلب مرة واحدة وتُعاد استخدامها)
# ------------------------------------------------------------------
_reciters_raw = None       # القائمة الخام كما تعود من mp3quran
_riwayat_names = None      # قائمة أسماء الروايات (بدون تكرار) بترتيب ثابت
_riwayat_groups = None     # dict: اسم الرواية -> [ (اسم_القارئ, moshaf_dict), ... ]


async def load_reciters():
    """تحميل بيانات القراء من mp3quran.net مرة واحدة وتخزينها مؤقتاً."""
    global _reciters_raw, _riwayat_names, _riwayat_groups
    if _reciters_raw is not None:
        return
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{MP3QURAN_API}/reciters", params={"language": "ar"})
        resp.raise_for_status()
        data = resp.json()
    _reciters_raw = data.get("reciters", [])

    groups = {}
    order = []
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


def get_riwayat_names():
    return _riwayat_names or []


def get_reciters_in_riwayah(riwayah_idx: int):
    if not _riwayat_names or riwayah_idx >= len(_riwayat_names):
        return []
    name = _riwayat_names[riwayah_idx]
    return _riwayat_groups.get(name, [])


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
# لوحات المفاتيح (القوائم)
# ------------------------------------------------------------------
def back_button(target: str):
    return InlineKeyboardButton("🔙 رجوع", callback_data=f"menu:{target}")


def main_menu_kb():
    kb = [
        [InlineKeyboardButton("📖 المصحف للقراءة", callback_data="menu:mushaf:0")],
        [InlineKeyboardButton("🎲 سورة عشوائية", callback_data="action:random")],
        [InlineKeyboardButton("🌐 اختيار اللغة", callback_data="menu:lang")],
        [InlineKeyboardButton("⚙️ اختيارات متقدمة", callback_data="menu:advanced")],
        [InlineKeyboardButton("📢 قناة البوت", url=CHANNEL_URL)],
    ]
    return InlineKeyboardMarkup(kb)


def advanced_menu_kb():
    kb = [
        [InlineKeyboardButton("🎙️ اختيار القارئ (القراءات العشر)", callback_data="menu:riwayat:0")],
        [InlineKeyboardButton("🌅 أذكار الصباح", callback_data="menu:athkar")],
        [InlineKeyboardButton("✨ فضل قراءة القرآن", callback_data="action:virtue")],
        [back_button("main")],
    ]
    return InlineKeyboardMarkup(kb)


def paginated_kb(items, page, prefix, back_target, columns=2, extra_data=""):
    """
    بناء قائمة مقسّمة على صفحات.
    items: قائمة نصوص العرض.
    prefix: بادئة callback_data لكل عنصر (سيُلحق بها الفهرس المطلق).
    extra_data: جزء إضافي يوضع بين prefix وفهرس الصفحة (مثلاً معرف الرواية).
    """
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = items[start:end]

    rows, row = [], []
    for offset, label in enumerate(chunk):
        idx = start + offset
        cb = f"{prefix}:{extra_data}:{idx}" if extra_data != "" else f"{prefix}:{idx}"
        row.append(InlineKeyboardButton(label, callback_data=cb))
        if len(row) == columns:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    nav = []
    page_prefix = f"page:{prefix}:{extra_data}" if extra_data != "" else f"page:{prefix}"
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"{page_prefix}:{page-1}"))
    if end < len(items):
        nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"{page_prefix}:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([back_button(back_target)])
    return InlineKeyboardMarkup(rows)


def mushaf_menu_kb(page):
    labels = [f"{i+1}. {name}" for i, name in enumerate(SURAHS)]
    return paginated_kb(labels, page, prefix="read", back_target="main")


def language_menu_kb():
    kb, row = [], []
    for code, (name, _) in LANGUAGES.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang:{code}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([back_button("main")])
    return InlineKeyboardMarkup(kb)


def riwayat_menu_kb(page):
    names = get_riwayat_names()
    return paginated_kb(names, page, prefix="riw", back_target="advanced")


def reciters_menu_kb(riwayah_idx, page):
    reciters = get_reciters_in_riwayah(riwayah_idx)
    labels = [name for name, _ in reciters]
    return paginated_kb(
        labels, page, prefix="rec", back_target="riwayat",
        extra_data=str(riwayah_idx),
    )


def reciter_surahs_kb(riwayah_idx, rec_idx, page):
    reciters = get_reciters_in_riwayah(riwayah_idx)
    if rec_idx >= len(reciters):
        return InlineKeyboardMarkup([[back_button("advanced")]])
    _, moshaf = reciters[rec_idx]
    nums = surah_numbers_for_moshaf(moshaf)
    labels = [f"{n}. {SURAHS[n-1]}" for n in nums if 1 <= n <= 114]

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    chunk = labels[start:end]
    chunk_nums = nums[start:end]

    rows, row = [], []
    for label, n in zip(chunk, chunk_nums):
        row.append(InlineKeyboardButton(label, callback_data=f"audio:{riwayah_idx}:{rec_idx}:{n}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"page:asur:{riwayah_idx}:{rec_idx}:{page-1}"))
    if end < len(labels):
        nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"page:asur:{riwayah_idx}:{rec_idx}:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([back_button(f"reclist:{riwayah_idx}")])
    return InlineKeyboardMarkup(rows)


# ------------------------------------------------------------------
# دوال مساعدة لجلب نص القرآن وإرساله
# ------------------------------------------------------------------
async def fetch_surah_text(surah_num: int, edition: str):
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{QURAN_API}/surah/{surah_num}/{edition}")
        resp.raise_for_status()
        data = resp.json()
    ayat = data.get("data", {}).get("ayahs", [])
    return ayat


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


async def send_surah(update: Update, context: ContextTypes.DEFAULT_TYPE, surah_num: int):
    lang_code = context.user_data.get("lang", "ar")
    _, edition = LANGUAGES.get(lang_code, LANGUAGES["ar"])

    query = update.callback_query
    chat_id = query.message.chat_id if query else update.effective_chat.id

    try:
        ayat = await fetch_surah_text(surah_num, edition)
    except Exception as e:
        log.exception("فشل جلب نص السورة")
        await context.bot.send_message(chat_id, f"⚠️ تعذّر جلب نص السورة حالياً: {e}")
        return

    header = f"📖 سورة {SURAHS[surah_num - 1]} ({surah_num})\n\n"
    body = "\n".join(f"{a['numberInSurah']}. {a['text']}" for a in ayat)
    full_text = header + body

    for chunk in chunk_text(full_text):
        await context.bot.send_message(chat_id, chunk)


# ------------------------------------------------------------------
# المعالجات (Handlers)
# ------------------------------------------------------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("lang", "ar")
    await update.message.reply_text(
        "🕌 أهلاً بك في بوت القرآن الكريم\n\nاختر من القائمة أدناه:",
        reply_markup=main_menu_kb(),
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split(":")
    action = parts[0]

    context.user_data.setdefault("lang", "ar")

    # ---------- القوائم الرئيسية ----------
    if action == "menu":
        target = parts[1]
        if target == "main":
            await query.edit_message_text("🕌 القائمة الرئيسية:", reply_markup=main_menu_kb())
        elif target == "mushaf":
            page = int(parts[2]) if len(parts) > 2 else 0
            await query.edit_message_text("📖 اختر سورة للقراءة:", reply_markup=mushaf_menu_kb(page))
        elif target == "lang":
            await query.edit_message_text("🌐 اختر لغة العرض:", reply_markup=language_menu_kb())
        elif target == "advanced":
            await query.edit_message_text("⚙️ اختيارات متقدمة:", reply_markup=advanced_menu_kb())
        elif target == "athkar":
            kb = [[back_button("advanced")]]
            if MORNING_ATHKAR_AUDIO:
                await query.edit_message_text(MORNING_ATHKAR_TEXT, parse_mode=ParseMode.MARKDOWN,
                                               reply_markup=InlineKeyboardMarkup(kb))
                await context.bot.send_audio(query.message.chat_id, MORNING_ATHKAR_AUDIO,
                                              caption="🎧 أذكار الصباح (صوتي)")
            else:
                await query.edit_message_text(MORNING_ATHKAR_TEXT, parse_mode=ParseMode.MARKDOWN,
                                               reply_markup=InlineKeyboardMarkup(kb))
        elif target == "riwayat":
            page = int(parts[2]) if len(parts) > 2 else 0
            if not get_riwayat_names():
                await query.edit_message_text("⏳ جاري تحميل قائمة الروايات، لحظات...")
                await load_reciters()
            await query.edit_message_text(
                "🎙️ اختر رواية من القراءات العشر:", reply_markup=riwayat_menu_kb(page)
            )
        elif target.startswith("reclist"):
            riwayah_idx = int(target.split("-")[1]) if "-" in target else int(parts[2])
            await query.edit_message_text(
                "🎙️ اختر القارئ:", reply_markup=reciters_menu_kb(riwayah_idx, 0)
            )
        return

    # ---------- أزرار الإجراءات المباشرة ----------
    if action == "action":
        sub = parts[1]
        if sub == "random":
            surah_num = random.randint(1, 114)
            await query.edit_message_text(f"🎲 السورة المختارة: {SURAHS[surah_num-1]}")
            await send_surah(update, context, surah_num)
        elif sub == "virtue":
            kb = InlineKeyboardMarkup([[back_button("advanced")]])
            await query.edit_message_text(VIRTUE_TEXT, parse_mode=ParseMode.MARKDOWN, reply_markup=kb)
        return

    # ---------- قراءة سورة من المصحف ----------
    if action == "read":
        surah_num = int(parts[1])
        await send_surah(update, context, surah_num)
        return

    # ---------- تغيير اللغة ----------
    if action == "lang":
        code = parts[1]
        context.user_data["lang"] = code
        name = LANGUAGES.get(code, ("?", ""))[0]
        await query.edit_message_text(
            f"✅ تم اختيار لغة العرض: {name}", reply_markup=main_menu_kb()
        )
        return

    # ---------- التنقل بين صفحات القوائم ----------
    if action == "page":
        sub = parts[1]
        if sub == "read":
            page = int(parts[2])
            await query.edit_message_text("📖 اختر سورة للقراءة:", reply_markup=mushaf_menu_kb(page))
        elif sub == "riw":
            page = int(parts[2])
            await query.edit_message_text("🎙️ اختر رواية:", reply_markup=riwayat_menu_kb(page))
        elif sub == "rec":
            riwayah_idx = int(parts[2])
            page = int(parts[3])
            await query.edit_message_text("🎙️ اختر القارئ:", reply_markup=reciters_menu_kb(riwayah_idx, page))
        elif sub == "asur":
            riwayah_idx, rec_idx, page = int(parts[2]), int(parts[3]), int(parts[4])
            await query.edit_message_text(
                "📜 اختر سورة للاستماع:", reply_markup=reciter_surahs_kb(riwayah_idx, rec_idx, page)
            )
        return

    # ---------- اختيار رواية ----------
    if action == "riw":
        riwayah_idx = int(parts[1])
        await query.edit_message_text("🎙️ اختر القارئ:", reply_markup=reciters_menu_kb(riwayah_idx, 0))
        return

    # ---------- اختيار قارئ ----------
    if action == "rec":
        riwayah_idx = int(parts[1])
        rec_idx = int(parts[2])
        await query.edit_message_text(
            "📜 اختر سورة للاستماع إليها:", reply_markup=reciter_surahs_kb(riwayah_idx, rec_idx, 0)
        )
        return

    # ---------- إرسال الصوت ----------
    if action == "audio":
        riwayah_idx, rec_idx, surah_num = int(parts[1]), int(parts[2]), int(parts[3])
        reciters = get_reciters_in_riwayah(riwayah_idx)
        if rec_idx >= len(reciters):
            await query.message.reply_text("⚠️ تعذّر إيجاد بيانات القارئ.")
            return
        rec_name, moshaf = reciters[rec_idx]
        url = build_audio_url(moshaf, surah_num)
        caption = f"🎧 {SURAHS[surah_num-1]} - القارئ: {rec_name}\nالرواية: {moshaf.get('name','')}"
        try:
            await context.bot.send_audio(query.message.chat_id, url, caption=caption)
        except Exception as e:
            log.exception("فشل إرسال الصوت")
            await query.message.reply_text(
                f"⚠️ تعذّر إرسال الملف الصوتي مباشرة، يمكنك الاستماع عبر الرابط:\n{url}"
            )
        return


async def on_error(update, context: ContextTypes.DEFAULT_TYPE):
    log.error("حدث خطأ: %s", context.error)


def main():
    if BOT_TOKEN in ("", "ضع_التوكن_هنا"):
        raise SystemExit(
            "❌ لم يتم ضبط توكن البوت. عرّف متغير البيئة BOT_TOKEN أو ضعه في الكود مباشرة."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(on_callback))
    app.add_error_handler(on_error)

    log.info("🚀 البوت يعمل الآن...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
