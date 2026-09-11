import asyncio
import io
import logging
import os
import random
from pathlib import Path

import requests

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# =========================================================
# الإعدادات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

API_BASE = "https://mp3quran.net/api/v3"
QURAN_SITE = "https://quran.com"
CHANNEL_URL = "https://t.me/x7oly"

MAX_AUDIO_BYTES = 50 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"

QURAN_PDF = FILES_DIR / "quran.pdf"
TAFSIR_PDF = FILES_DIR / "tafsir.pdf"

MORNING_AUDIO = FILES_DIR / "adhkar_morning.mp3"
EVENING_AUDIO = FILES_DIR / "adhkar_evening.mp3"


# =========================================================
# أسماء الأزرار
# =========================================================

BTN_QURAN = "📖 المصحف"
BTN_RECITERS = "🎙️ القرائ"
BTN_REWAYAT = "📜 الروايات"
BTN_RANDOM = "🎲 عشوائي"
BTN_QUICK = "⚡ اختيار سريع"
BTN_ADVANCED = "⚙️ اختيار متقدم"
BTN_MORNING = "🌅 أذكار الصباح"
BTN_EVENING = "🌙 أذكار المساء"
BTN_QURAN_PDF = "📕 القرآن الكريم PDF"
BTN_TAFSIR_PDF = "📚 تفسير القرآن PDF"
BTN_CHANNEL = "📢 قناتنا على تيليجرام"
BTN_LANGUAGE = "🌐 تغيير اللغة"

BTN_BACK = "🔙 رجوع"
BTN_HOME = "🏠 القائمة الرئيسية"
BTN_NEXT = "التالي ➡️"
BTN_PREVIOUS = "⬅️ السابق"


# =========================================================
# لوحة القائمة الرئيسية
# =========================================================

MAIN_KEYBOARD = [
    [BTN_QURAN, BTN_LANGUAGE],
    [BTN_RANDOM],
    [BTN_QUICK],
    [BTN_ADVANCED],
    [BTN_RECITERS, BTN_REWAYAT],
    [BTN_MORNING, BTN_EVENING],
    [BTN_QURAN_PDF, BTN_TAFSIR_PDF],
    [BTN_CHANNEL],
]

HOME_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True,
    is_persistent=True,
    input_field_placeholder="اختر من القائمة…",
)


# =========================================================
# لوحة الرجوع
# =========================================================

def menu_keyboard(rows):
    keyboard = list(rows)

    keyboard.append([BTN_BACK, BTN_HOME])

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="اختر من القائمة…",
    )


# =========================================================
# التخزين المؤقت
# =========================================================

CACHE = {
    "reciters": None,
    "suras": None,
    "riwayat": None,
}


# =========================================================
# أدوات عامة
# =========================================================

def normalize_text(text):
    if not text:
        return ""

    return (
        str(text)
        .strip()
        .replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ى", "ي")
        .replace("ة", "ه")
        .replace("ـ", "")
    )


def get_name(item):
    if isinstance(item, dict):
        return str(
            item.get("name")
            or item.get("title")
            or item.get("reciter")
            or ""
        ).strip()

    return str(item).strip()


def get_sura_id(sura):
    if not isinstance(sura, dict):
        return None

    value = (
        sura.get("id")
        or sura.get("sura_id")
        or sura.get("number")
    )

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_sura_name(sura):
    if not isinstance(sura, dict):
        return ""

    return str(
        sura.get("name")
        or sura.get("sura_name")
        or sura.get("title")
        or ""
    ).strip()


def get_moshaf_name(moshaf):
    if not isinstance(moshaf, dict):
        return ""

    return str(
        moshaf.get("name")
        or moshaf.get("rewaya")
        or "رواية"
    ).strip()


def get_moshaf_server(moshaf):
    if not isinstance(moshaf, dict):
        return ""

    return str(moshaf.get("server") or "").strip()


def get_moshaf_surah_list(moshaf):
    if not isinstance(moshaf, dict):
        return []

    value = moshaf.get("surah_list")

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [
            int(x)
            for x in value.split(",")
            if x.strip().isdigit()
        ]

    return []


def make_sura_button(sura):
    sid = get_sura_id(sura)
    name = get_sura_name(sura)

    if sid is None:
        return name

    return f"{sid:03d} - {name}"


def parse_sura_button(text):
    try:
        number = int(text.split("-")[0].strip())
        return number
    except (ValueError, IndexError):
        return None


def make_reciter_buttons(reciters, per_page=12, page=0):
    total = len(reciters)

    start = page * per_page
    end = start + per_page

    current = reciters[start:end]

    rows = []

    for i in range(0, len(current), 2):
        row = current[i:i + 2]

        rows.append([
            get_name(item)
            for item in row
        ])

    navigation = []

    if page > 0:
        navigation.append(BTN_PREVIOUS)

    if end < total:
        navigation.append(BTN_NEXT)

    if navigation:
        rows.append(navigation)

    return rows


# =========================================================
# الاتصال بـ MP3Quran API
# =========================================================

async def api_get(path, params=None):
    def request():
        response = requests.get(
            f"{API_BASE}/{path}",
            params=params or {},
            timeout=(15, 60),
            headers={
                "User-Agent": "QuranBot/1.0"
            },
        )

        response.raise_for_status()
        return response.json()

    return await asyncio.to_thread(request)


async def get_reciters():
    if CACHE["reciters"] is not None:
        return CACHE["reciters"]

    data = await api_get(
        "reciters",
        {"language": "ar"},
    )

    reciters = data.get("reciters", [])

    if not isinstance(reciters, list):
        reciters = []

    CACHE["reciters"] = reciters

    return reciters


async def get_suras():
    if CACHE["suras"] is not None:
        return CACHE["suras"]

    data = await api_get(
        "suwar",
        {"language": "ar"},
    )

    suras = data.get("suwar", [])

    if not isinstance(suras, list):
        suras = []

    CACHE["suras"] = suras

    return suras


async def get_riwayat():
    if CACHE["riwayat"] is not None:
        return CACHE["riwayat"]

    data = await api_get(
        "riwayat",
        {"language": "ar"},
    )

    riwayat = data.get("riwayat", [])

    if not isinstance(riwayat, list):
        riwayat = []

    CACHE["riwayat"] = riwayat

    return riwayat


# =========================================================
# ترتيب القراء
# =========================================================

PREFERRED_RECITERS = [
    "مشاري العفاسي",
    "أحمد الحذيفي",
    "أحمد بن علي العجمي",
    "ماهر المعيقلي",
    "ياسر الدوسري",
    "عبدالباسط عبدالصمد",
    "محمد صديق المنشاوي",
    "سعد الغامدي",
    "سعود الشريم",
    "هاني الرفاعي",
    "خالد الجليل",
    "فارس عباد",
    "إدريس أبكر",
    "ناصر القطامي",
    "هزاع البلوشي",
]


def sort_reciters(reciters):
    preferred = []
    others = []

    preferred_normalized = [
        normalize_text(x)
        for x in PREFERRED_RECITERS
    ]

    for reciter in reciters:
        name = get_name(reciter)
        normalized = normalize_text(name)

        if normalized in preferred_normalized:
            preferred.append(reciter)
        else:
            others.append(reciter)

    preferred.sort(
        key=lambda x: preferred_normalized.index(
            normalize_text(get_name(x))
        )
        if normalize_text(get_name(x)) in preferred_normalized
        else 999
    )

    others.sort(
        key=lambda x: normalize_text(get_name(x))
    )

    return preferred + others


# =========================================================
# رسالة البداية
# =========================================================

WELCOME_TEXT = """🌿 أهلاً وسهلاً بك في قرآن بوت 🕌

نسأل الله أن يجعل هذا البوت سببًا لنشر كتابه وتذكّر كلامه.

﴿ وَذَكِّرْ فَإِنَّ الذِّكْرَىٰ تَنفَعُ الْمُؤْمِنِينَ ﴾

🌱 انشر الخير لعلّ الله يكتب لك أجره.

قال رسول الله ﷺ:
«مَن دلَّ على خيرٍ فله مثلُ أجرِ فاعلِه»

نسأل الله أن يكتب لك أجر كل من قرأ أو استمع أو انتفع. 🤍

اختر من القائمة بالأسفل 👇
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# القائمة الرئيسية
# =========================================================

async def show_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "🏠 القائمة الرئيسية\n\nاختر ما تريد من الأزرار بالأسفل:",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# المصحف
# =========================================================

async def show_quran(update, context):
    suras = await get_suras()

    if not suras:
        await update.message.reply_text(
            "❌ تعذر تحميل سور القرآن حاليًا.",
            reply_markup=HOME_MARKUP,
        )
        return

    context.user_data["mode"] = "quran"

    rows = []

    for i in range(0, len(suras), 2):
        row = []

        for sura in suras[i:i + 2]:
            row.append(make_sura_button(sura))

        rows.append(row)

    rows.append([BTN_HOME])

    markup = ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="اختر السورة…",
    )

    await update.message.reply_text(
        "📖 اختر السورة التي تريد فتحها في المصحف:",
        reply_markup=markup,
    )


async def open_quran_sura(update, context, sura_id):
    url = f"{QURAN_SITE}/{sura_id}"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📖 فتح المصحف",
                url=url,
            )
        ]
    ])

    await update.message.reply_text(
        "📖 تم اختيار السورة.\n\n"
        "اضغط الزر لفتحها في المصحف:",
        reply_markup=keyboard,
    )


# =========================================================
# القراء
# =========================================================

async def show_reciters(update, context, page=0):
    reciters = await get_reciters()

    reciters = sort_reciters(reciters)

    if not reciters:
        await update.message.reply_text(
            "❌ لم أتمكن من تحميل القراء.",
            reply_markup=HOME_MARKUP,
        )
        return

    context.user_data["mode"] = "reciters"
    context.user_data["reciter_list"] = reciters
    context.user_data["reciter_page"] = page

    rows = make_reciter_buttons(
        reciters,
        per_page=12,
        page=page,
    )

    markup = menu_keyboard(rows)

    total_pages = (len(reciters) + 11) // 12

    await update.message.reply_text(
        f"🎙️ اختر القارئ:\n\n"
        f"الصفحة {page + 1} من {total_pages}",
        reply_markup=markup,
    )


# =========================================================
# اختيار سريع
# =========================================================

async def show_quick(update, context):
    reciters = sort_reciters(await get_reciters())

    letters = set()

    for reciter in reciters:
        name = get_name(reciter)

        if name:
            letters.add(name[0])

    letters = sorted(letters)

    rows = []

    current = []

    for letter in letters:
        current.append(letter)

        if len(current) == 4:
            rows.append(current)
            current = []

    if current:
        rows.append(current)

    rows.append(["✨ الكل"])

    context.user_data["mode"] = "quick"

    await update.message.reply_text(
        "⚡ الاختيار السريع\n\n"
        "اختر الحرف الذي يبدأ به اسم القارئ:",
        reply_markup=menu_keyboard(rows),
    )


async def quick_letter(update, context, letter):
    reciters = sort_reciters(await get_reciters())

    if letter == "✨ الكل":
        selected = reciters
    else:
        selected = [
            r for r in reciters
            if get_name(r).startswith(letter)
        ]

    if not selected:
        await update.message.reply_text(
            "❌ لا يوجد قراء بهذا الحرف.",
            reply_markup=HOME_MARKUP,
        )
        return

    context.user_data["mode"] = "quick_reciters"
    context.user_data["reciter_list"] = selected
    context.user_data["reciter_page"] = 0

    rows = make_reciter_buttons(
        selected,
        per_page=12,
        page=0,
    )

    await update.message.reply_text(
        f"🎙️ القراء ({len(selected)}):",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# الاختيار المتقدم
# =========================================================

async def show_advanced(update, context):
    await update.message.reply_text(
        "⚙️ الاختيار المتقدم\n\n"
        "أولًا اختر القارئ:",
        reply_markup=HOME_MARKUP,
    )

    await show_reciters(update, context, page=0)

    context.user_data["mode"] = "advanced_reciter"


# =========================================================
# بعد اختيار القارئ
# =========================================================

def find_reciter_by_name(reciters, name):
    normalized = normalize_text(name)

    for reciter in reciters:
        if normalize_text(get_name(reciter)) == normalized:
            return reciter

    return None


async def handle_reciter_selected(update, context, name):
    reciters = context.user_data.get("reciter_list")

    if not reciters:
        reciters = sort_reciters(await get_reciters())

    reciter = find_reciter_by_name(reciters, name)

    if not reciter:
        await update.message.reply_text(
            "❌ لم أجد هذا القارئ.",
            reply_markup=HOME_MARKUP,
        )
        return

    context.user_data["selected_reciter"] = reciter

    moshaf_list = reciter.get("moshaf", [])

    if not moshaf_list:
        await update.message.reply_text(
            "❌ لا توجد رواية متاحة لهذا القارئ.",
            reply_markup=HOME_MARKUP,
        )
        return

    if len(moshaf_list) == 1:
        context.user_data["selected_moshaf"] = moshaf_list[0]

        await show_reciter_suras(
            update,
            context,
            reciter,
            moshaf_list[0],
        )
        return

    rows = []

    for moshaf in moshaf_list:
        rows.append([get_moshaf_name(moshaf)])

    context.user_data["mode"] = "moshaf"

    await update.message.reply_text(
        f"🎙️ القارئ: {get_name(reciter)}\n\n"
        "📜 اختر الرواية:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# اختيار الرواية
# =========================================================

async def handle_moshaf_selected(update, context, name):
    reciter = context.user_data.get("selected_reciter")

    if not reciter:
        await update.message.reply_text(
            "❌ انتهت الجلسة، اختر القارئ من جديد.",
            reply_markup=HOME_MARKUP,
        )
        return

    moshaf_list = reciter.get("moshaf", [])

    selected = None

    for moshaf in moshaf_list:
        if normalize_text(get_moshaf_name(moshaf)) == normalize_text(name):
            selected = moshaf
            break

    if not selected:
        await update.message.reply_text(
            "❌ لم أجد هذه الرواية.",
            reply_markup=HOME_MARKUP,
        )
        return

    context.user_data["selected_moshaf"] = selected

    await show_reciter_suras(
        update,
        context,
        reciter,
        selected,
    )


# =========================================================
# سور القارئ
# =========================================================

async def show_reciter_suras(update, context, reciter, moshaf):
    all_suras = await get_suras()

    allowed = get_moshaf_surah_list(moshaf)

    if allowed:
        allowed_set = set(allowed)

        suras = [
            s for s in all_suras
            if get_sura_id(s) in allowed_set
        ]
    else:
        suras = all_suras

    if not suras:
        await update.message.reply_text(
            "❌ لم أجد السور لهذه الرواية.",
            reply_markup=HOME_MARKUP,
        )
        return

    context.user_data["mode"] = "surah_audio"
    context.user_data["suras"] = suras

    rows = []

    for i in range(0, len(suras), 2):
        rows.append([
            make_sura_button(s)
            for s in suras[i:i + 2]
        ])

    await update.message.reply_text(
        f"🎙️ القارئ: {get_name(reciter)}\n"
        f"📜 الرواية: {get_moshaf_name(moshaf)}\n\n"
        "📖 اختر السورة:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# إرسال السورة صوتيًا
# =========================================================

async def send_surah_audio(update, context, sura_id):
    reciter = context.user_data.get("selected_reciter")
    moshaf = context.user_data.get("selected_moshaf")

    if not reciter or not moshaf:
        await update.message.reply_text(
            "❌ اختر القارئ والرواية أولًا.",
            reply_markup=HOME_MARKUP,
        )
        return

    server = get_moshaf_server(moshaf)

    if not server:
        await update.message.reply_text(
            "❌ لا يوجد رابط صوتي لهذه الرواية.",
            reply_markup=HOME_MARKUP,
        )
        return

    if not server.endswith("/"):
        server += "/"

    audio_url = f"{server}{sura_id:03d}.mp3"

    await update.message.reply_text(
        "⏳ جاري تجهيز التلاوة…"
    )

    try:
        def download_audio():
            response = requests.get(
                audio_url,
                timeout=(20, 120),
                headers={
                    "User-Agent": "QuranBot/1.0"
                },
            )

            response.raise_for_status()

            content = response.content

            if len(content) > MAX_AUDIO_BYTES:
                raise ValueError("AUDIO_TOO_LARGE")

            return content

        audio_data = await asyncio.to_thread(
            download_audio
        )

        file_obj = io.BytesIO(audio_data)

        sura_name = str(sura_id)

        for sura in await get_suras():
            if get_sura_id(sura) == sura_id:
                sura_name = get_sura_name(sura)
                break

        file_obj.name = f"{sura_id:03d}.mp3"

        await update.message.reply_audio(
            audio=file_obj,
            title=f"{sura_name} - {get_name(reciter)}",
            performer=get_name(reciter),
            caption=(
                f"🎧 {sura_name}\n"
                f"🎙️ {get_name(reciter)}\n"
                f"📜 {get_moshaf_name(moshaf)}"
            ),
            reply_markup=HOME_MARKUP,
        )

    except ValueError as error:
        if str(error) == "AUDIO_TOO_LARGE":
            await update.message.reply_text(
                "⚠️ هذه السورة أكبر من الحد المسموح لرفعها مباشرة إلى تيليجرام.",
                reply_markup=HOME_MARKUP,
            )
        else:
            await update.message.reply_text(
                "❌ حدث خطأ أثناء تجهيز الصوت.",
                reply_markup=HOME_MARKUP,
            )

    except Exception:
        logging.exception("Audio error")

        await update.message.reply_text(
            "❌ تعذر تحميل التلاوة حاليًا.\n"
            "جرّب سورة أخرى بعد قليل.",
            reply_markup=HOME_MARKUP,
        )


# =========================================================
# الروايات
# =========================================================

async def show_riwayat(update, context):
    riwayat = await get_riwayat()

    if not riwayat:
        await update.message.reply_text(
            "❌ تعذر تحميل الروايات.",
            reply_markup=HOME_MARKUP,
        )
        return

    rows = []

    for item in riwayat:
        name = get_name(item)

        if name:
            rows.append([name])

    context.user_data["mode"] = "riwayat"

    await update.message.reply_text(
        "📜 اختر الرواية:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# عشوائي
# =========================================================

async def random_recitation(update, context):
    await update.message.reply_text(
        "🎲 جاري اختيار تلاوة عشوائية…"
    )

    try:
        reciters = await get_reciters()

        valid = []

        for reciter in reciters:
            for moshaf in reciter.get("moshaf", []):
                server = get_moshaf_server(moshaf)

                if not server:
                    continue

                surah_list = get_moshaf_surah_list(moshaf)

                if not surah_list:
                    surah_list = list(range(1, 115))

                for sid in surah_list:
                    valid.append(
                        (reciter, moshaf, sid)
                    )

        if not valid:
            raise RuntimeError("No audio")

        reciter, moshaf, sid = random.choice(valid)

        context.user_data["selected_reciter"] = reciter
        context.user_data["selected_moshaf"] = moshaf

        await send_surah_audio(
            update,
            context,
            sid,
        )

    except Exception:
        logging.exception("Random error")

        await update.message.reply_text(
            "❌ تعذر اختيار تلاوة عشوائية حاليًا.",
            reply_markup=HOME_MARKUP,
        )


# =========================================================
# الأذكار
# =========================================================

MORNING_TEXT = """🌅 أذكار الصباح

أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

اللهم بك أصبحنا وبك أمسينا، وبك نحيا وبك نموت وإليك النشور.

رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.

سبحان الله وبحمده.

لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.
"""


EVENING_TEXT = """🌙 أذكار المساء

أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

اللهم بك أمسينا وبك أصبحنا وبك نحيا وبك نموت وإليك المصير.

رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.

سبحان الله وبحمده.

لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.
"""


async def send_dhikr(update, context, morning=True):
    text = MORNING_TEXT if morning else EVENING_TEXT
    audio_path = MORNING_AUDIO if morning else EVENING_AUDIO

    await update.message.reply_text(
        text,
        reply_markup=HOME_MARKUP,
    )

    if audio_path.exists():
        try:
            with open(audio_path, "rb") as audio:
                await update.message.reply_audio(
                    audio=audio,
                    caption=(
                        "🎧 أذكار الصباح"
                        if morning
                        else "🎧 أذكار المساء"
                    ),
                    reply_markup=HOME_MARKUP,
                )
        except Exception:
            logging.exception("Dhikr audio error")


# =========================================================
# ملفات PDF
# =========================================================

async def send_pdf(update, context, path, title):
    if not path.exists():
        await update.message.reply_text(
            f"📕 {title}\n\n"
            "⚠️ الملف غير موجود حاليًا.\n\n"
            "ضع الملف داخل مجلد files في المشروع باسم:\n"
            f"{path.name}",
            reply_markup=HOME_MARKUP,
        )
        return

    try:
        with open(path, "rb") as document:
            await update.message.reply_document(
                document=document,
                caption=f"📕 {title}",
                reply_markup=HOME_MARKUP,
            )

    except Exception:
        logging.exception("PDF error")

        await update.message.reply_text(
            "❌ تعذر إرسال الملف.",
            reply_markup=HOME_MARKUP,
        )


# =========================================================
# تغيير اللغة
# =========================================================

async def language_menu(update, context):
    rows = [
        ["🇸🇦 العربية"],
        ["🇬🇧 English"],
    ]

    context.user_data["mode"] = "language"

    await update.message.reply_text(
        "🌐 اختر اللغة:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# القناة
# =========================================================

async def show_channel(update, context):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 فتح قناتنا على تيليجرام",
                url=CHANNEL_URL,
            )
        ]
    ])

    await update.message.reply_text(
        "📢 تابع قناتنا على تيليجرام:",
        reply_markup=keyboard,
    )


# =========================================================
# معالجة الرسائل
# =========================================================

async def handle_message(update, context):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # -----------------------------------------
    # القائمة الرئيسية
    # -----------------------------------------

    if text == BTN_HOME:
        await show_home(update, context)
        return

    if text == BTN_BACK:
        await show_home(update, context)
        return

    if text == BTN_QURAN:
        await show_quran(update, context)
        return

    if text == BTN_RECITERS:
        await show_reciters(update, context, 0)
        return

    if text == BTN_REWAYAT:
        await show_riwayat(update, context)
        return

    if text == BTN_RANDOM:
        await random_recitation(update, context)
        return

    if text == BTN_QUICK:
        await show_quick(update, context)
        return

    if text == BTN_ADVANCED:
        await show_advanced(update, context)
        return

    if text == BTN_MORNING:
        await send_dhikr(
            update,
            context,
            morning=True,
        )
        return

    if text == BTN_EVENING:
        await send_dhikr(
            update,
            context,
            morning=False,
        )
        return

    if text == BTN_QURAN_PDF:
        await send_pdf(
            update,
            context,
            QURAN_PDF,
            "القرآن الكريم PDF",
        )
        return

    if text == BTN_TAFSIR_PDF:
        await send_pdf(
            update,
            context,
            TAFSIR_PDF,
            "تفسير القرآن PDF",
        )
        return

    if text == BTN_CHANNEL:
        await show_channel(update, context)
        return

    if text == BTN_LANGUAGE:
        await language_menu(update, context)
        return

    # -----------------------------------------
    # التنقل بين صفحات القراء
    # -----------------------------------------

    mode = context.user_data.get("mode")

    if text == BTN_NEXT:
        if mode in ("reciters", "advanced_reciter", "quick_reciters"):
            reciters = context.user_data.get(
                "reciter_list",
                [],
            )

            page = context.user_data.get(
                "reciter_page",
                0,
            )

            max_page = max(
                0,
                (len(reciters) - 1) // 12,
            )

            if page < max_page:
                page += 1

            context.user_data["reciter_page"] = page

            rows = make_reciter_buttons(
                reciters,
                per_page=12,
                page=page,
            )

            await update.message.reply_text(
                f"🎙️ اختر القارئ:\n\n"
                f"الصفحة {page + 1} من {max_page + 1}",
                reply_markup=menu_keyboard(rows),
            )

            return

    if text == BTN_PREVIOUS:
        if mode in ("reciters", "advanced_reciter", "quick_reciters"):
            reciters = context.user_data.get(
                "reciter_list",
                [],
            )

            page = context.user_data.get(
                "reciter_page",
                0,
            )

            page = max(0, page - 1)

            context.user_data["reciter_page"] = page

            rows = make_reciter_buttons(
                reciters,
                per_page=12,
                page=page,
            )

            await update.message.reply_text(
                "🎙️ اختر القارئ:",
                reply_markup=menu_keyboard(rows),
            )

            return

    # -----------------------------------------
    # المصحف
    # -----------------------------------------

    if mode == "quran":
        sura_id = parse_sura_button(text)

        if sura_id:
            await open_quran_sura(
                update,
                context,
                sura_id,
            )
            return

    # -----------------------------------------
    # اختيار القارئ
    # -----------------------------------------

    if mode in (
        "reciters",
        "advanced_reciter",
        "quick_reciters",
    ):
        await handle_reciter_selected(
            update,
            context,
            text,
        )
        return

    # -----------------------------------------
    # اختيار الرواية
    # -----------------------------------------

    if mode == "moshaf":
        await handle_moshaf_selected(
            update,
            context,
            text,
        )
        return

    # -----------------------------------------
    # اختيار السورة للصوت
    # -----------------------------------------

    if mode == "surah_audio":
        sura_id = parse_sura_button(text)

        if sura_id:
            await send_surah_audio(
                update,
                context,
                sura_id,
            )
            return

    # -----------------------------------------
    # الاختيار السريع
    # -----------------------------------------

    if mode == "quick":
        if text == "✨ الكل":
            await quick_letter(
                update,
                context,
                "✨ الكل",
            )
            return

        if len(text) == 1:
            await quick_letter(
                update,
                context,
                text,
            )
            return

    # -----------------------------------------
    # الروايات
    # -----------------------------------------

    if mode == "riwayat":
        await update.message.reply_text(
            f"📜 اخترت: {text}\n\n"
            "يمكنك الآن اختيار قارئ من القائمة.",
            reply_markup=HOME_MARKUP,
        )

        await show_reciters(update, context, 0)
        return

    # -----------------------------------------
    # اللغة
    # -----------------------------------------

    if mode == "language":
        if text == "🇸🇦 العربية":
            await update.message.reply_text(
                "🇸🇦 تم اختيار العربية.",
                reply_markup=HOME_MARKUP,
            )
            return

        if text == "🇬🇧 English":
            await update.message.reply_text(
                "🇬🇧 English is selected.\n"
                "The full English interface will be added in the next stage.",
                reply_markup=HOME_MARKUP,
            )
            return

    # -----------------------------------------
    # أي رسالة غير معروفة
    # -----------------------------------------

    await update.message.reply_text(
        "اختر من القائمة الموجودة أسفل الشاشة 👇",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# معالجة الأخطاء
# =========================================================

async def error_handler(update, context):
    logging.exception(
        "Unhandled error:",
        exc_info=context.error,
    )


# =========================================================
# تشغيل البوت
# =========================================================

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود في Railway Variables."
        )

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    application.add_error_handler(
        error_handler
    )

    print("Quran Bot is running...")

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
