import asyncio
import io
import logging
import os
import random
import re
import threading
import unicodedata
from pathlib import Path
from urllib.parse import urlencode

import requests
from flask import Flask, jsonify, render_template_string

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# =========================================================
# إعدادات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

API_BASE = "https://mp3quran.net/api/v3"
QURAN_API = "https://api.alquran.cloud/v1"

QURAN_SITE = "https://quran.com"
TAFSIR_URL = "https://quranenc.com/ar"
DORAR_URL = "https://dorar.net/hadith/search"
CHANNEL_URL = "https://t.me/x7oly"

MAX_AUDIO_BYTES = 50 * 1024 * 1024

PORT = int(os.getenv("PORT", "8080"))

# يمكن وضع WEBAPP_URL يدويًا في Railway
# مثال:
# https://your-domain.up.railway.app/quran
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

if not WEBAPP_URL:
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway_domain:
        WEBAPP_URL = f"https://{railway_domain}/quran"

# =========================================================
# الملفات
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"

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

BTN_TAFSIR = "📚 تفسير القرآن"
BTN_DORAR = "📜 الدرر السنية"

BTN_CHANNEL = "📢 قناتنا على تيليجرام"
BTN_LANGUAGE = "🌐 تغيير اللغة"

BTN_BACK = "🔙 رجوع"
BTN_HOME = "🏠 القائمة الرئيسية"
BTN_HIDE = "❌ إخفاء القائمة"

BTN_OPEN_QURAN = "📖 فتح المصحف"

# =========================================================
# القائمة الرئيسية
# =========================================================

MAIN_KEYBOARD_ROWS = [
    [BTN_QURAN, BTN_RECITERS],
    [BTN_REWAYAT, BTN_RANDOM],
    [BTN_QUICK, BTN_ADVANCED],
    [BTN_MORNING, BTN_EVENING],
    [BTN_TAFSIR],
    [BTN_DORAR],
    [BTN_CHANNEL],
    [BTN_LANGUAGE],
    [BTN_HIDE],
]


def build_main_keyboard():
    """
    زر المصحف هنا Web App حقيقي.
    """
    rows = []

    if WEBAPP_URL:
        quran_button = KeyboardButton(
            BTN_QURAN,
            web_app=WebAppInfo(url=WEBAPP_URL),
        )
    else:
        quran_button = KeyboardButton(BTN_QURAN)

    rows.append([
        quran_button,
        KeyboardButton(BTN_RECITERS),
    ])

    for row in MAIN_KEYBOARD_ROWS[1:]:
        rows.append([KeyboardButton(x) for x in row])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
    )


MAIN_KEYBOARD = build_main_keyboard()


def menu_keyboard(rows, resize=True):
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=resize,
        is_persistent=True,
    )


# =========================================================
# أسماء السور
# =========================================================

SURA_NAMES = [
    "الفاتحة",
    "البقرة",
    "آل عمران",
    "النساء",
    "المائدة",
    "الأنعام",
    "الأعراف",
    "الأنفال",
    "التوبة",
    "يونس",
    "هود",
    "يوسف",
    "الرعد",
    "إبراهيم",
    "الحجر",
    "النحل",
    "الإسراء",
    "الكهف",
    "مريم",
    "طه",
    "الأنبياء",
    "الحج",
    "المؤمنون",
    "النور",
    "الفرقان",
    "الشعراء",
    "النمل",
    "القصص",
    "العنكبوت",
    "الروم",
    "لقمان",
    "السجدة",
    "الأحزاب",
    "سبأ",
    "فاطر",
    "يس",
    "الصافات",
    "ص",
    "الزمر",
    "غافر",
    "فصلت",
    "الشورى",
    "الزخرف",
    "الدخان",
    "الجاثية",
    "الأحقاف",
    "محمد",
    "الفتح",
    "الحجرات",
    "ق",
    "الذاريات",
    "الطور",
    "النجم",
    "القمر",
    "الرحمن",
    "الواقعة",
    "الحديد",
    "المجادلة",
    "الحشر",
    "الممتحنة",
    "الصف",
    "الجمعة",
    "المنافقون",
    "التغابن",
    "الطلاق",
    "التحريم",
    "الملك",
    "القلم",
    "الحاقة",
    "المعارج",
    "نوح",
    "الجن",
    "المزمل",
    "المدثر",
    "القيامة",
    "الإنسان",
    "المرسلات",
    "النبأ",
    "النازعات",
    "عبس",
    "التكوير",
    "الانفطار",
    "المطففين",
    "الانشقاق",
    "البروج",
    "الطارق",
    "الأعلى",
    "الغاشية",
    "الفجر",
    "البلد",
    "الشمس",
    "الليل",
    "الضحى",
    "الشرح",
    "التين",
    "العلق",
    "القدر",
    "البينة",
    "الزلزلة",
    "العاديات",
    "القارعة",
    "التكاثر",
    "العصر",
    "الهمزة",
    "الفيل",
    "قريش",
    "الماعون",
    "الكوثر",
    "الكافرون",
    "النصر",
    "المسد",
    "الإخلاص",
    "الفلق",
    "الناس",
]


# =========================================================
# Slugs الخاصة بـ Quran.com
# =========================================================

QURAN_SLUGS = {
    1: "al-fatihah",
    2: "al-baqarah",
    3: "ali-imran",
    4: "an-nisa",
    5: "al-maidah",
    6: "al-anam",
    7: "al-araf",
    8: "al-anfal",
    9: "at-tawbah",
    10: "yunus",
    11: "hud",
    12: "yusuf",
    13: "ar-rad",
    14: "ibrahim",
    15: "al-hijr",
    16: "an-nahl",
    17: "al-isra",
    18: "al-kahf",
    19: "maryam",
    20: "ta-ha",
    21: "al-anbya",
    22: "al-hajj",
    23: "al-muminun",
    24: "an-nur",
    25: "al-furqan",
    26: "ash-shuara",
    27: "an-naml",
    28: "al-qasas",
    29: "al-ankabut",
    30: "ar-rum",
    31: "luqman",
    32: "as-sajdah",
    33: "al-ahzab",
    34: "saba",
    35: "fatir",
    36: "ya-sin",
    37: "as-saffat",
    38: "sad",
    39: "az-zumar",
    40: "ghafir",
    41: "fussilat",
    42: "ash-shuraa",
    43: "az-zukhruf",
    44: "ad-dukhan",
    45: "al-jathiyah",
    46: "al-ahqaf",
    47: "muhammad",
    48: "al-fath",
    49: "al-hujurat",
    50: "qaf",
    51: "adh-dhariyat",
    52: "at-tur",
    53: "an-najm",
    54: "al-qamar",
    55: "ar-rahman",
    56: "al-waqiah",
    57: "al-hadid",
    58: "al-mujadila",
    59: "al-hashr",
    60: "al-mumtahanah",
    61: "as-saff",
    62: "al-jumuah",
    63: "al-munafiqun",
    64: "at-taghabun",
    65: "at-talaq",
    66: "at-tahrim",
    67: "al-mulk",
    68: "al-qalam",
    69: "al-haqqah",
    70: "al-maarij",
    71: "nuh",
    72: "al-jinn",
    73: "al-muzzammil",
    74: "al-muddaththir",
    75: "al-qiyamah",
    76: "al-insan",
    77: "al-mursalat",
    78: "an-naba",
    79: "an-naziat",
    80: "abasa",
    81: "at-takwir",
    82: "al-infitar",
    83: "al-mutaffifin",
    84: "al-inshiqaq",
    85: "al-buruj",
    86: "at-tariq",
    87: "al-ala",
    88: "al-ghashiyah",
    89: "al-fajr",
    90: "al-balad",
    91: "ash-shams",
    92: "al-layl",
    93: "ad-duha",
    94: "ash-sharh",
    95: "at-tin",
    96: "al-alaq",
    97: "al-qadr",
    98: "al-bayyinah",
    99: "az-zalzalah",
    100: "al-adiyat",
    101: "al-qariah",
    102: "at-takathur",
    103: "al-asr",
    104: "al-humazah",
    105: "al-fil",
    106: "quraysh",
    107: "al-maun",
    108: "al-kawthar",
    109: "al-kafirun",
    110: "an-nasr",
    111: "al-masad",
    112: "al-ikhlas",
    113: "al-falaq",
    114: "an-nas",
}


# =========================================================
# أدوات مساعدة
# =========================================================

def normalize_text(text: str) -> str:
    text = text or ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        ch for ch in text
        if not unicodedata.combining(ch)
    )
    text = text.replace("ـ", "")
    return text.strip().lower()


def quran_web_url(sura_id=None):
    if not WEBAPP_URL:
        return None

    base = WEBAPP_URL.rstrip("/")

    if sura_id:
        return f"{base}?{urlencode({'sura': sura_id})}"

    return base


def get_sura_name(sura_id):
    if 1 <= sura_id <= len(SURA_NAMES):
        return SURA_NAMES[sura_id]
    return f"السورة {sura_id}"


def get_sura_id_by_name(text):
    normalized = normalize_text(text)

    for i, name in enumerate(SURA_NAMES, start=1):
        if normalized == normalize_text(name):
            return i

    # محاولة مطابقة جزئية
    for i, name in enumerate(SURA_NAMES, start=1):
        if normalize_text(name) in normalized:
            return i

    return None


# =========================================================
# Telegram keyboards
# =========================================================

def back_keyboard():
    return menu_keyboard([
        [BTN_BACK, BTN_HOME],
    ])


def quran_open_markup(sura_id=None):
    url = quran_web_url(sura_id)

    if not url:
        return None

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                BTN_OPEN_QURAN,
                web_app=WebAppInfo(url=url),
            )
        ]
    ])


# =========================================================
# حالة المستخدم
# =========================================================

user_states = {}


def get_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = {
            "mode": None,
            "selected_reciter": None,
            "selected_riwaya": None,
        }

    return user_states[user_id]


# =========================================================
# API القراء
# =========================================================

reciters_cache = None
reciters_cache_time = 0


def fetch_reciters():
    global reciters_cache

    if reciters_cache:
        return reciters_cache

    url = f"{API_BASE}/reciters"

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()

        data = response.json()

        reciters = data.get("reciters", [])

        reciters_cache = reciters
        return reciters

    except Exception as e:
        logging.exception("Failed to fetch reciters: %s", e)
        return []


def sort_reciters(reciters):
    return sorted(
        reciters,
        key=lambda x: normalize_text(
            x.get("name", "")
        )
    )


def get_all_reciters():
    return sort_reciters(fetch_reciters())


def find_reciter_by_name(name):
    target = normalize_text(name)

    for reciter in get_all_reciters():
        if normalize_text(reciter.get("name", "")) == target:
            return reciter

    return None


# =========================================================
# الروايات
# =========================================================

def get_riwayat():
    values = set()

    for reciter in get_all_reciters():
        moshaf_list = reciter.get("moshaf", [])

        for moshaf in moshaf_list:
            riwaya = (
                moshaf.get("name")
                or moshaf.get("riwaya")
                or ""
            ).strip()

            if riwaya:
                values.add(riwaya)

    return sorted(values, key=normalize_text)


def find_moshaf_for_reciter(reciter, riwaya=None):
    moshaf_list = reciter.get("moshaf", [])

    if not moshaf_list:
        return None

    if riwaya:
        target = normalize_text(riwaya)

        for moshaf in moshaf_list:
            name = (
                moshaf.get("name")
                or moshaf.get("riwaya")
                or ""
            )

            if normalize_text(name) == target:
                return moshaf

    return moshaf_list[0]


# =========================================================
# المصحف
# =========================================================

async def show_quran(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    المصحف الرئيسي يفتح مباشرة داخل Telegram Web App.
    """

    if WEBAPP_URL:
        markup = quran_open_markup()

        await update.message.reply_text(
            "📖 <b>المصحف الشريف</b>\n\n"
            "اضغط على الزر لفتح المصحف المدمج داخل تيليجرام.",
            parse_mode="HTML",
            reply_markup=markup,
        )
    else:
        await update.message.reply_text(
            "📖 المصحف غير مفعّل بعد.\n"
            "يجب إضافة WEBAPP_URL في Railway.",
            reply_markup=MAIN_KEYBOARD,
        )


async def open_quran_sura(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    sura_id: int,
):
    name = get_sura_name(sura_id)

    if WEBAPP_URL:
        markup = quran_open_markup(sura_id)

        await update.message.reply_text(
            f"📖 <b>سورة {name}</b>\n\n"
            "اضغط على «فتح المصحف» لفتح السورة مباشرة.",
            parse_mode="HTML",
            reply_markup=markup,
        )
    else:
        slug = QURAN_SLUGS.get(sura_id)

        if slug:
            url = f"{QURAN_SITE}/ar/{slug}"

            await update.message.reply_text(
                f"📖 سورة {name}",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "📖 فتح المصحف",
                            url=url,
                        )
                    ]
                ]),
            )


# =========================================================
# قائمة السور
# =========================================================

def surah_keyboard():
    rows = []

    for start in range(0, 114, 2):
        row = []

        for i in range(start + 1, min(start + 3, 115)):
            row.append(
                f"{i}. {SURA_NAMES[i - 1]}"
            )

        rows.append(row)

    rows.append([BTN_BACK, BTN_HOME])

    return menu_keyboard(rows)


# =========================================================
# القراء
# =========================================================

async def show_reciters(update, context):
    reciters = get_all_reciters()

    if not reciters:
        await update.message.reply_text(
            "تعذر تحميل قائمة القرّاء حاليًا.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    rows = []

    for reciter in reciters:
        name = reciter.get("name", "").strip()

        if name:
            rows.append([name])

    rows.append([BTN_BACK, BTN_HOME])

    user_states[update.effective_user.id]["mode"] = "reciter"

    await update.message.reply_text(
        "🎙️ <b>اختر القارئ:</b>",
        parse_mode="HTML",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# اختيار سريع
# =========================================================

async def show_quick(update, context):
    user_states[update.effective_user.id]["mode"] = "quick"

    rows = [
        ["ا", "ب", "ت"],
        ["ث", "ج", "ح"],
        ["خ", "د", "ذ"],
        ["ر", "ز", "س"],
        ["ش", "ص", "ض"],
        ["ط", "ظ", "ع"],
        ["غ", "ف", "ق"],
        ["ك", "ل", "م"],
        ["ن", "ه", "و"],
        ["ي"],
        [BTN_BACK, BTN_HOME],
    ]

    await update.message.reply_text(
        "⚡ <b>اختيار سريع</b>\n\n"
        "اختر أول حرف من اسم القارئ:",
        parse_mode="HTML",
        reply_markup=menu_keyboard(rows),
    )


async def quick_letter(update, context, letter):
    reciters = get_all_reciters()

    filtered = [
        r for r in reciters
        if normalize_text(
            r.get("name", "")
        ).startswith(normalize_text(letter))
    ]

    if not filtered:
        await update.message.reply_text(
            "لم أجد قرّاء بهذا الحرف.",
            reply_markup=back_keyboard(),
        )
        return

    rows = []

    for reciter in filtered:
        rows.append([
            reciter.get("name", "")
        ])

    rows.append([BTN_BACK, BTN_HOME])

    user_states[update.effective_user.id]["mode"] = "reciter"

    await update.message.reply_text(
        f"⚡ القرّاء الذين يبدأ اسمهم بحرف «{letter}»:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# اختيار متقدم
# =========================================================

async def show_advanced(update, context):
    user_states[update.effective_user.id]["mode"] = "advanced"

    reciters = get_all_reciters()

    rows = []

    for reciter in reciters:
        name = reciter.get("name", "").strip()

        if name:
            rows.append([name])

    rows.append([BTN_BACK, BTN_HOME])

    await update.message.reply_text(
        "⚙️ <b>الاختيار المتقدم</b>\n\n"
        "اختر القارئ ثم يمكنك اختيار الرواية المتاحة له.",
        parse_mode="HTML",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# الروايات
# =========================================================

async def show_rewayat(update, context):
    riwayat = get_riwayat()

    if not riwayat:
        await update.message.reply_text(
            "تعذر تحميل الروايات حاليًا.",
            reply_markup=MAIN_KEYBOARD,
        )
        return

    rows = []

    for value in riwayat:
        rows.append([value])

    rows.append([BTN_BACK, BTN_HOME])

    user_states[update.effective_user.id]["mode"] = "riwaya"

    await update.message.reply_text(
        "📜 <b>اختر الرواية:</b>",
        parse_mode="HTML",
        reply_markup=menu_keyboard(rows),
    )


async def show_reciters_by_riwaya(
    update,
    context,
    riwaya,
):
    results = []

    target = normalize_text(riwaya)

    for reciter in get_all_reciters():
        moshaf_list = reciter.get("moshaf", [])

        for moshaf in moshaf_list:
            name = (
                moshaf.get("name")
                or moshaf.get("riwaya")
                or ""
            )

            if normalize_text(name) == target:
                results.append(reciter)
                break

    rows = []

    for reciter in results:
        rows.append([
            reciter.get("name", "")
        ])

    rows.append([BTN_BACK, BTN_HOME])

    user_states[update.effective_user.id]["mode"] = "reciter_riwaya"
    user_states[update.effective_user.id]["selected_riwaya"] = riwaya

    await update.message.reply_text(
        f"📜 القرّاء المتاحون في رواية:\n<b>{riwaya}</b>",
        parse_mode="HTML",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# اختيار السورة بعد اختيار القارئ
# =========================================================

async def show_surahs_for_reciter(
    update,
    context,
    reciter,
    riwaya=None,
):
    user_id = update.effective_user.id

    user_states[user_id]["mode"] = "quran"
    user_states[user_id]["selected_reciter"] = reciter.get("name", "")
    user_states[user_id]["selected_riwaya"] = riwaya

    await update.message.reply_text(
        f"🎙️ القارئ: <b>{reciter.get('name', '')}</b>\n\n"
        "اختر السورة:",
        parse_mode="HTML",
        reply_markup=surah_keyboard(),
    )


# =========================================================
# تنزيل وإرسال الصوت
# =========================================================

def find_audio_url(reciter, sura_id, riwaya=None):
    moshaf = find_moshaf_for_reciter(
        reciter,
        riwaya,
    )

    if not moshaf:
        return None

    server = (
        moshaf.get("server")
        or moshaf.get("server_url")
        or ""
    )

    if not server:
        return None

    server = server.strip()

    if not server.endswith("/"):
        server += "/"

    file_name = f"{sura_id:03d}.mp3"

    return server + file_name


async def send_surah_audio(
    update,
    context,
    reciter,
    sura_id,
    riwaya=None,
):
    name = get_sura_name(sura_id)

    audio_url = find_audio_url(
        reciter,
        sura_id,
        riwaya,
    )

    if not audio_url:
        await update.message.reply_text(
            "تعذر العثور على ملف الصوت لهذه السورة.",
            reply_markup=back_keyboard(),
        )
        return

    try:
        await update.message.reply_text(
            f"⏳ جاري تجهيز سورة <b>{name}</b>...",
            parse_mode="HTML",
        )

        response = requests.get(
            audio_url,
            timeout=60,
            stream=True,
        )

        response.raise_for_status()

        content_length = response.headers.get("content-length")

        if content_length:
            if int(content_length) > MAX_AUDIO_BYTES:
                await update.message.reply_text(
                    "حجم الملف كبير جدًا لإرساله عبر البوت."
                )
                return

        data = response.content

        if len(data) > MAX_AUDIO_BYTES:
            await update.message.reply_text(
                "حجم الملف كبير جدًا لإرساله عبر البوت."
            )
            return

        audio = io.BytesIO(data)
        audio.name = f"{name}.mp3"
        audio.seek(0)

        caption = (
            f"🎙️ القارئ: {reciter.get('name', '')}\n"
            f"📖 سورة {name}"
        )

        markup = quran_open_markup(sura_id)

        await update.message.reply_audio(
            audio=audio,
            caption=caption,
            reply_markup=markup,
        )

    except Exception as e:
        logging.exception("Audio error: %s", e)

        await update.message.reply_text(
            "حدث خطأ أثناء تحميل السورة، حاول مرة أخرى."
        )


# =========================================================
# العشوائي
# =========================================================

async def random_surah(update, context):
    reciters = get_all_reciters()

    if not reciters:
        await update.message.reply_text(
            "تعذر تحميل القراء."
        )
        return

    reciter = random.choice(reciters)
    sura_id = random.randint(1, 114)

    await send_surah_audio(
        update,
        context,
        reciter,
        sura_id,
    )


# =========================================================
# الأذكار
# =========================================================

async def send_adhkar(
    update,
    context,
    audio_path,
    title,
):
    if audio_path.exists():
        try:
            with audio_path.open("rb") as audio:
                await update.message.reply_audio(
                    audio=audio,
                    caption=title,
                )
            return

        except Exception:
            logging.exception(
                "Failed sending adhkar audio"
            )

    await update.message.reply_text(
        f"{title}\n\n"
        "ملف الصوت غير موجود حاليًا."
    )


# =========================================================
# التفسير
# =========================================================

async def show_tafsir(update, context):
    await update.message.reply_text(
        "📚 <b>تفسير القرآن</b>\n\n"
        "يمكنك فتح موقع التفسير من الزر التالي:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📚 فتح تفسير القرآن",
                    url=TAFSIR_URL,
                )
            ]
        ]),
    )


# =========================================================
# الدرر السنية
# =========================================================

async def show_dorar(update, context):
    await update.message.reply_text(
        "📜 <b>الدرر السنية</b>\n\n"
        "للبحث في الأحاديث:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📜 فتح الدرر السنية",
                    url=DORAR_URL,
                )
            ]
        ]),
    )


# =========================================================
# القناة
# =========================================================

async def show_channel(update, context):
    await update.message.reply_text(
        "📢 <b>قناتنا على تيليجرام</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📢 فتح القناة",
                    url=CHANNEL_URL,
                )
            ]
        ]),
    )


# =========================================================
# اللغة
# =========================================================

async def show_language(update, context):
    await update.message.reply_text(
        "🌐 <b>تغيير اللغة</b>\n\n"
        "اختر اللغة:",
        parse_mode="HTML",
        reply_markup=menu_keyboard([
            ["🇸🇦 العربية"],
            ["🇬🇧 English"],
            [BTN_BACK, BTN_HOME],
        ]),
    )


# =========================================================
# الرجوع
# =========================================================

async def go_home(update, context):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "mode": None,
        "selected_reciter": None,
        "selected_riwaya": None,
    }

    await update.message.reply_text(
        "🏠 <b>القائمة الرئيسية</b>",
        parse_mode="HTML",
        reply_markup=MAIN_KEYBOARD,
    )


async def go_back(update, context):
    await go_home(update, context)


# =========================================================
# إخفاء القائمة
# =========================================================

async def hide_keyboard(update, context):
    await update.message.reply_text(
        "تم إخفاء القائمة.\n\n"
        "استخدم /start لإظهارها مرة أخرى.",
        reply_markup=ReplyKeyboardRemove(),
    )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "mode": None,
        "selected_reciter": None,
        "selected_riwaya": None,
    }

    await update.message.reply_text(
        "السلام عليكم ورحمة الله وبركاته 🌿\n\n"
        "أهلًا بك في بوت القرآن الكريم 📖\n\n"
        "اختر من القائمة بالأسفل:",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================================================
# Web App Quran Reader
# =========================================================

app = Flask(__name__)

quran_cache = {}


QURAN_HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0,
      maximum-scale=1.0, user-scalable=no">

<title>المصحف الشريف</title>

<script src="https://telegram.org/js/telegram-web-app.js"></script>

<style>

* {
    box-sizing: border-box;
}

html, body {
    margin: 0;
    padding: 0;
    background: #f7f1e3;
    color: #252016;
}

body {
    font-family:
        "Amiri",
        "Noto Naskh Arabic",
        "Traditional Arabic",
        serif;

    -webkit-tap-highlight-color: transparent;
}

.topbar {
    position: sticky;
    top: 0;
    z-index: 20;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 12px 14px;

    background: rgba(247,241,227,.96);
    backdrop-filter: blur(10px);

    border-bottom: 1px solid #d8cdb5;
}

.title {
    font-size: 21px;
    font-weight: bold;
}

.controls {
    display: flex;
    gap: 7px;
}

.control {
    width: 40px;
    height: 40px;

    border: 1px solid #cfc2a7;
    border-radius: 10px;

    background: #fffaf0;

    font-size: 22px;
    font-weight: bold;

    cursor: pointer;
}

.surah-box {
    margin: 18px 12px 8px;

    padding: 18px 12px;

    text-align: center;

    border: 1px solid #d8cdb5;
    border-radius: 14px;

    background: #fffaf0;
}

.surah-name {
    font-size: 28px;
    font-weight: bold;
    margin-bottom: 8px;
}

.meta {
    font-family: Arial, sans-serif;
    font-size: 13px;
    opacity: .7;
}

.basmala {
    text-align: center;

    font-size: 27px;

    margin: 22px 10px;
}

.reader {
    padding: 8px 18px 50px;

    line-height: 2.35;

    font-size: 29px;

    text-align: justify;

    word-spacing: 2px;
}

.ayah {
    display: inline;
}

.ayah-number {
    display: inline-flex;

    align-items: center;
    justify-content: center;

    width: 31px;
    height: 31px;

    margin: 0 4px;

    border: 1px solid #b99f7a;
    border-radius: 50%;

    font-family: Arial, sans-serif;
    font-size: 13px;

    vertical-align: middle;
}

.loading {
    text-align: center;

    padding: 50px 20px;

    font-family: Arial, sans-serif;
}

.error {
    text-align: center;

    padding: 40px 20px;

    font-family: Arial, sans-serif;
}

.surah-nav {
    display: flex;

    justify-content: space-between;

    gap: 10px;

    padding: 0 15px 40px;
}

.nav-btn {
    flex: 1;

    padding: 12px;

    border: 1px solid #cfc2a7;
    border-radius: 10px;

    background: #fffaf0;

    font-family: Arial, sans-serif;

    font-size: 15px;
}

@media (max-width: 600px) {

    .reader {
        font-size: 27px;
        line-height: 2.3;
        padding-left: 15px;
        padding-right: 15px;
    }

    .surah-name {
        font-size: 26px;
    }

    .basmala {
        font-size: 25px;
    }
}

</style>
</head>

<body>

<div class="topbar">

    <div class="title">
        📖 المصحف
    </div>

    <div class="controls">

        <button
            class="control"
            onclick="changeFont(-2)">
            −
        </button>

        <button
            class="control"
            onclick="changeFont(2)">
            +
        </button>

    </div>

</div>

<div id="content">

    <div class="loading">
        جاري تحميل المصحف...
    </div>

</div>

<script>

const tg = window.Telegram?.WebApp;

if (tg) {
    tg.ready();
    tg.expand();
}

let currentSura = 1;
let fontSize = Number(
    localStorage.getItem("quranFontSize") || 29
);

const params = new URLSearchParams(
    window.location.search
);

const requestedSura = parseInt(
    params.get("sura") || "1",
    10
);

if (
    requestedSura >= 1 &&
    requestedSura <= 114
) {
    currentSura = requestedSura;
}

function changeFont(amount) {

    fontSize += amount;

    if (fontSize < 20) {
        fontSize = 20;
    }

    if (fontSize > 45) {
        fontSize = 45;
    }

    localStorage.setItem(
        "quranFontSize",
        fontSize
    );

    document.querySelector(
        ".reader"
    ).style.fontSize = fontSize + "px";
}

async function loadSurah(id) {

    const content =
        document.getElementById("content");

    content.innerHTML =
        '<div class="loading">جاري تحميل السورة...</div>';

    try {

        const response =
            await fetch(
                "/api/quran/surah/" + id
            );

        if (!response.ok) {
            throw new Error(
                "HTTP " + response.status
            );
        }

        const data =
            await response.json();

        if (
            !data ||
            !data.data ||
            !data.data.ayahs
        ) {
            throw new Error(
                "Invalid Quran response"
            );
        }

        const surah =
            data.data;

        let html = "";

        html += `
            <div class="surah-box">
                <div class="surah-name">
                    سورة ${surah.name}
                </div>

                <div class="meta">
                    رقم السورة: ${surah.number}
                    · عدد الآيات: ${surah.numberOfAyahs}
                </div>
            </div>
        `;

        if (id !== 9) {
            html += `
                <div class="basmala">
                    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
                </div>
            `;
        }

        html += `
            <div
                class="reader"
                style="font-size:${fontSize}px"
            >
        `;

        for (const ayah of surah.ayahs) {

            let text = ayah.text || "";

            /*
             * إزالة البسملة من بداية الآية الأولى
             * في السور التي تحتويها من API.
             */
            if (
                ayah.numberInSurah === 1 &&
                id !== 1 &&
                id !== 9
            ) {
                text = text.replace(
                    /^بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\s*/,
                    ""
                );
            }

            html += `
                <span class="ayah">
                    ${text}
                    <span class="ayah-number">
                        ${ayah.numberInSurah}
                    </span>
                </span>
            `;
        }

        html += `
            </div>

            <div class="surah-nav">

                <button
                    class="nav-btn"
                    onclick="previousSurah()"
                    ${id <= 1 ? "disabled" : ""}
                >
                    ← السورة السابقة
                </button>

                <button
                    class="nav-btn"
                    onclick="nextSurah()"
                    ${id >= 114 ? "disabled" : ""}
                >
                    السورة التالية →
                </button>

            </div>
        `;

        content.innerHTML = html;

        window.scrollTo({
            top: 0,
            behavior: "instant"
        });

    } catch (error) {

        console.error(error);

        content.innerHTML = `
            <div class="error">
                <h3>تعذر تحميل المصحف</h3>
                <p>
                    تأكد من اتصال الإنترنت ثم حاول مرة أخرى.
                </p>

                <button
                    class="nav-btn"
                    onclick="loadSurah(${id})">
                    إعادة المحاولة
                </button>
            </div>
        `;
    }
}

function previousSurah() {

    if (currentSura > 1) {

        currentSura--;

        history.replaceState(
            null,
            "",
            "?sura=" + currentSura
        );

        loadSurah(currentSura);
    }
}

function nextSurah() {

    if (currentSura < 114) {

        currentSura++;

        history.replaceState(
            null,
            "",
            "?sura=" + currentSura
        );

        loadSurah(currentSura);
    }
}

loadSurah(currentSura);

</script>

</body>
</html>
"""


@app.route("/quran")
def quran_page():
    return render_template_string(QURAN_HTML)


@app.route("/")
def home_page():
    return (
        "Quran Bot is running."
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.route("/api/quran/surah/<int:sura_id>")
def quran_surah(sura_id):

    if sura_id < 1 or sura_id > 114:
        return jsonify({
            "error": "Invalid surah"
        }), 400

    if sura_id in quran_cache:
        return jsonify(
            quran_cache[sura_id]
        )

    url = (
        f"{QURAN_API}/surah/"
        f"{sura_id}/quran-uthmani"
    )

    try:

        response = requests.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        quran_cache[sura_id] = data

        return jsonify(data)

    except Exception as e:

        logging.exception(
            "Quran API error: %s",
            e,
        )

        return jsonify({
            "error": "Quran API unavailable"
        }), 502


def run_web_server():
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False,
    )


# =========================================================
# تشغيل البوت
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message:
        return

    text = (
        update.message.text or ""
    ).strip()

    user_id = update.effective_user.id
    state = get_state(user_id)

    mode = state.get("mode")

    # -----------------------------------------------------
    # القائمة الرئيسية
    # -----------------------------------------------------

    if text == BTN_QURAN:
        await show_quran(update, context)
        return

    if text == BTN_RECITERS:
        await show_reciters(update, context)
        return

    if text == BTN_REWAYAT:
        await show_rewayat(update, context)
        return

    if text == BTN_RANDOM:
        await random_surah(update, context)
        return

    if text == BTN_QUICK:
        await show_quick(update, context)
        return

    if text == BTN_ADVANCED:
        await show_advanced(update, context)
        return

    if text == BTN_MORNING:
        await send_adhkar(
            update,
            context,
            MORNING_AUDIO,
            "🌅 أذكار الصباح",
        )
        return

    if text == BTN_EVENING:
        await send_adhkar(
            update,
            context,
            EVENING_AUDIO,
            "🌙 أذكار المساء",
        )
        return

    if text == BTN_TAFSIR:
        await show_tafsir(update, context)
        return

    if text == BTN_DORAR:
        await show_dorar(update, context)
        return

    if text == BTN_CHANNEL:
        await show_channel(update, context)
        return

    if text == BTN_LANGUAGE:
        await show_language(update, context)
        return

    if text == BTN_HIDE:
        await hide_keyboard(update, context)
        return

    if text == BTN_BACK:
        await go_back(update, context)
        return

    if text == BTN_HOME:
        await go_home(update, context)
        return

    # -----------------------------------------------------
    # وضع اختيار السورة
    # -----------------------------------------------------

    if mode == "quran":

        match = re.match(
            r"^\s*(\d+)\.\s*(.+?)\s*$",
            text,
        )

        if match:

            sura_id = int(
                match.group(1)
            )

            if 1 <= sura_id <= 114:

                reciter_name = state.get(
                    "selected_reciter"
                )

                reciter = find_reciter_by_name(
                    reciter_name
                )

                if reciter:

                    await send_surah_audio(
                        update,
                        context,
                        reciter,
                        sura_id,
                        state.get(
                            "selected_riwaya"
                        ),
                    )

                    return

        # محاولة اسم السورة
        sura_id = get_sura_id_by_name(text)

        if sura_id:

            reciter_name = state.get(
                "selected_reciter"
            )

            reciter = find_reciter_by_name(
                reciter_name
            )

            if reciter:

                await send_surah_audio(
                    update,
                    context,
                    reciter,
                    sura_id,
                    state.get(
                        "selected_riwaya"
                    ),
                )

                return

    # -----------------------------------------------------
    # اختيار القارئ
    # -----------------------------------------------------

    if mode in (
        "reciter",
        "advanced",
        "reciter_riwaya",
    ):

        reciter = find_reciter_by_name(
            text
        )

        if reciter:

            await show_surahs_for_reciter(
                update,
                context,
                reciter,
                state.get(
                    "selected_riwaya"
                ),
            )

            return

    # -----------------------------------------------------
    # اختيار الرواية
    # -----------------------------------------------------

    if mode == "riwaya":

        await show_reciters_by_riwaya(
            update,
            context,
            text,
        )

        return

    # -----------------------------------------------------
    # الاختيار السريع
    # -----------------------------------------------------

    if mode == "quick":

        if len(text) <= 2:

            await quick_letter(
                update,
                context,
                text,
            )

            return

    # -----------------------------------------------------
    # إذا أرسل اسم قارئ بشكل مباشر
    # -----------------------------------------------------

    reciter = find_reciter_by_name(text)

    if reciter:

        await show_surahs_for_reciter(
            update,
            context,
            reciter,
        )

        return

    # -----------------------------------------------------
    # إذا أرسل رقم سورة
    # -----------------------------------------------------

    if text.isdigit():

        sura_id = int(text)

        if 1 <= sura_id <= 114:

            await open_quran_sura(
                update,
                context,
                sura_id,
            )

            return

    # -----------------------------------------------------
    # رد افتراضي
    # -----------------------------------------------------

    await update.message.reply_text(
        "اختر من القائمة بالأسفل 👇",
        reply_markup=MAIN_KEYBOARD,
    )


# =========================================================
# Main
# =========================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing"
        )

    logging.basicConfig(
        format=(
            "%(asctime)s - "
            "%(name)s - "
            "%(levelname)s - "
            "%(message)s"
        ),
        level=logging.INFO,
    )

    # تشغيل Web App بجانب البوت
    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True,
    )

    web_thread.start()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            handle_message,
        )
    )

    logging.info(
        "Bot started."
    )

    logging.info(
        "WEBAPP_URL=%s",
        WEBAPP_URL,
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
