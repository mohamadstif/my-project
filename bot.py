import io
import logging
import os
import random
import re
import unicodedata
from pathlib import Path

import requests

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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
# الإعدادات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

API_BASE = "https://mp3quran.net/api/v3"

QURAN_SITE = "https://quran.com"
TAFSIR_URL = "https://quranenc.com/ar"
DORAR_URL = "https://dorar.net/hadith/search"
CHANNEL_URL = "https://t.me/x7oly"

# رابط التطبيق المصغر
MINI_APP_URL = "https://mohamadstif.github.io/my-project/"

# الحد الأقصى للرفع عبر Bot API العادي
MAX_AUDIO_BYTES = 50 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"

MORNING_AUDIO = FILES_DIR / "adhkar_morning.mp3"
EVENING_AUDIO = FILES_DIR / "adhkar_evening.mp3"


# =========================================================
# أزرار البوت
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


# =========================================================
# روابط سور القرآن في Quran.com
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
    21: "al-anbiya",
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
    42: "ash-shura",
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
    62: "al-jumua",
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
# لوحة القائمة الرئيسية
# =========================================================

MAIN_KEYBOARD = [
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


HOME_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True,
    is_persistent=True,
    one_time_keyboard=False,
)


def menu_keyboard(rows):
    rows = list(rows)

    rows.append([BTN_BACK, BTN_HOME])
    rows.append([BTN_HIDE])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
    )


# =========================================================
# الكاش
# =========================================================

_cache = {
    "reciters": None,
    "suras": None,
    "riwayat": None,
}


# =========================================================
# أدوات مساعدة
# =========================================================

def normalize_text(text):
    if not text:
        return ""

    text = str(text)

    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    text = "".join(
        ch for ch in text
        if not unicodedata.combining(ch)
    )

    text = (
        text.replace("أ", "ا")
        .replace("إ", "ا")
        .replace("آ", "ا")
        .replace("ٱ", "ا")
        .replace("ى", "ي")
        .replace("ة", "ه")
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def get_name(item):
    if isinstance(item, dict):
        return str(
            item.get("name")
            or item.get("title")
            or ""
        ).strip()

    return str(item).strip()


def get_sura_name(sura):
    if not isinstance(sura, dict):
        return ""

    return str(
        sura.get("name")
        or sura.get("sura_name")
        or sura.get("title")
        or ""
    ).strip()


def get_sura_id(sura):
    if not isinstance(sura, dict):
        return None

    for key in (
        "id",
        "sura_id",
        "number",
    ):
        value = sura.get(key)

        if value is not None:
            try:
                return int(value)
            except Exception:
                pass

    return None


def get_moshaf_list(reciter):
    if not isinstance(reciter, dict):
        return []

    moshaf = reciter.get("moshaf")

    if isinstance(moshaf, list):
        return moshaf

    return []


def get_moshaf_server(moshaf):
    if not isinstance(moshaf, dict):
        return ""

    return str(
        moshaf.get("server")
        or moshaf.get("url")
        or ""
    ).strip()


def get_moshaf_surah_list(moshaf):
    if not isinstance(moshaf, dict):
        return ""

    return str(
        moshaf.get("surah_list")
        or moshaf.get("sura_list")
        or ""
    ).strip()


def get_moshaf_rewaya_id(moshaf):
    if not isinstance(moshaf, dict):
        return None

    for key in (
        "rewaya_id",
        "riwaya_id",
        "rewayaId",
    ):
        value = moshaf.get(key)

        if value is not None:
            return str(value).strip()

    return None


def get_moshaf_rewaya_name(moshaf):
    if not isinstance(moshaf, dict):
        return ""

    for key in (
        "rewaya",
        "riwaya",
        "rewaya_name",
        "name",
    ):
        value = moshaf.get(key)

        if isinstance(value, dict):
            value = (
                value.get("name")
                or value.get("title")
                or ""
            )

        if value:
            return str(value).strip()

    return ""


def get_riwaya_id(item):
    if not isinstance(item, dict):
        return None

    for key in (
        "id",
        "rewaya_id",
        "riwaya_id",
    ):
        value = item.get(key)

        if value is not None:
            return str(value).strip()

    return None


def get_riwaya_name(item):
    if not isinstance(item, dict):
        return get_name(item)

    return str(
        item.get("name")
        or item.get("title")
        or item.get("rewaya")
        or item.get("riwaya")
        or ""
    ).strip()


# =========================================================
# API
# =========================================================

def api_get(endpoint, params=None):
    url = f"{API_BASE}/{endpoint}"

    try:
        response = requests.get(
            url,
            params=params or {"language": "ar"},
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:
        logging.exception(
            "API error: %s",
            e,
        )

        return None


def get_reciters():
    if _cache["reciters"] is not None:
        return _cache["reciters"]

    data = api_get(
        "reciters",
        {"language": "ar"},
    )

    if not data:
        return []

    reciters = data.get(
        "reciters",
        [],
    )

    if not isinstance(reciters, list):
        reciters = []

    _cache["reciters"] = reciters

    return reciters


def get_suras():
    if _cache["suras"] is not None:
        return _cache["suras"]

    data = api_get(
        "suwar",
        {"language": "ar"},
    )

    if not data:
        return []

    suras = data.get(
        "suwar",
        [],
    )

    if not isinstance(suras, list):
        suras = []

    _cache["suras"] = suras

    return suras


def get_riwayat():
    if _cache["riwayat"] is not None:
        return _cache["riwayat"]

    data = api_get(
        "riwayat",
        {"language": "ar"},
    )

    if not data:
        return []

    riwayat = data.get(
        "riwayat",
        [],
    )

    if not isinstance(riwayat, list):
        riwayat = []

    _cache["riwayat"] = riwayat

    return riwayat


# =========================================================
# ترتيب القراء
# =========================================================

PREFERRED_RECITERS = [
    "عبد الباسط عبد الصمد",
    "مشاري راشد العفاسي",
    "ماهر المعيقلي",
    "أحمد العجمي",
    "ياسر الدوسري",
    "سعد الغامدي",
    "عبد الرحمن السديس",
    "سعود الشريم",
    "ناصر القطامي",
    "أبو بكر الشاطري",
    "محمد صديق المنشاوي",
    "محمود خليل الحصري",
    "محمد أيوب",
    "علي جابر",
    "عبد الله خياط",
    "عبد الله بصفر",
    "خالد الجليل",
    "فارس عباد",
    "إدريس أبكر",
    "صلاح بو خاطر",
    "هاني الرفاعي",
    "نبيل الرفاعي",
    "أحمد الحذيفي",
]


def sort_reciters(reciters):
    preferred_map = {
        normalize_text(name): index
        for index, name in enumerate(
            PREFERRED_RECITERS
        )
    }

    def sort_key(reciter):
        name = get_name(reciter)
        normalized = normalize_text(name)

        if normalized in preferred_map:
            return (
                0,
                preferred_map[normalized],
                normalized,
            )

        return (
            1,
            normalized,
        )

    return sorted(
        reciters,
        key=sort_key,
    )


def unique_reciters(reciters):
    seen = set()
    result = []

    for reciter in sort_reciters(reciters):
        name = get_name(reciter)

        if not name:
            continue

        key = normalize_text(name)

        if key in seen:
            continue

        seen.add(key)
        result.append(reciter)

    return result


# =========================================================
# لوحة جميع القراء
# =========================================================

def make_all_reciter_keyboard(reciters):
    reciters = unique_reciters(
        reciters
    )

    names = [
        get_name(reciter)
        for reciter in reciters
    ]

    rows = []

    for i in range(
        0,
        len(names),
        2,
    ):
        rows.append(
            names[i:i + 2]
        )

    rows.append(
        [BTN_BACK, BTN_HOME]
    )

    rows.append(
        [BTN_HIDE]
    )

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
    )


# =========================================================
# الرسالة الترحيبية
# =========================================================

WELCOME_TEXT = """
🌿 أهلاً وسهلاً بك في قرآن بوت 🕌

نسأل الله أن يجعل القرآن ربيع قلوبنا ونور صدورنا.

﴿ وَذَكِّرْ فَإِنَّ الذِّكْرَىٰ تَنْفَعُ الْمُؤْمِنِينَ ﴾

قال رسول الله ﷺ:
«مَن دلَّ على خيرٍ فله مثلُ أجرِ فاعلِه»

اختر ما تريد من القائمة بالأسفل 👇
"""


# =========================================================
# القائمة الرئيسية
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=HOME_MARKUP,
    )


async def show_home(
    update,
    context,
):
    context.user_data.clear()

    await update.message.reply_text(
        "🏠 القائمة الرئيسية\n\n"
        "اختر من الأزرار الموجودة بالأسفل 👇",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# إخفاء لوحة الأزرار
# =========================================================

async def hide_keyboard(
    update,
    context,
):
    context.user_data.clear()

    await update.message.reply_text(
        "✅ تم إخفاء لوحة الأزرار.\n\n"
        "لإظهارها من جديد أرسل /start",
        reply_markup=ReplyKeyboardRemove(),
    )


# =========================================================
# المصحف
# =========================================================

async def show_quran(
    update,
    context,
):
    suras = get_suras()

    if not suras:
        await update.message.reply_text(
            "⚠️ تعذر تحميل السور حاليًا.",
            reply_markup=menu_keyboard([]),
        )
        return

    context.user_data.clear()

    context.user_data["mode"] = "quran"
    context.user_data["quran_mode"] = True

    rows = []
    names = []

    for sura in suras:
        name = get_sura_name(sura)

        if name:
            names.append(name)

    for i in range(
        0,
        len(names),
        3,
    ):
        rows.append(
            names[i:i + 3]
        )

    await update.message.reply_text(
        "📖 اختر السورة:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# فتح السورة في التطبيق المصغر
# =========================================================

async def open_quran_sura(
    update,
    context,
    sura,
):
    sura_id = get_sura_id(sura)

    if not sura_id:
        await update.message.reply_text(
            "⚠️ لم أستطع معرفة رقم السورة."
        )
        return

    sura_name = get_sura_name(sura)

    # فتح التطبيق المصغر على نفس السورة
    mini_app_url = (
        f"{MINI_APP_URL}?surah={sura_id}"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📖 فتح المصحف",
                    web_app=WebAppInfo(
                        url=mini_app_url
                    ),
                )
            ]
        ]
    )

    await update.message.reply_text(
        f"📖 سورة {sura_name}\n\n"
        "اضغط الزر لفتح السورة في المصحف:",
        reply_markup=keyboard,
    )


# =========================================================
# البحث عن السورة
# =========================================================

def find_sura_by_name(name):
    target = normalize_text(name)

    for sura in get_suras():

        if normalize_text(
            get_sura_name(sura)
        ) == target:
            return sura

    return None


# =========================================================
# القراء
# =========================================================

async def show_reciters(
    update,
    context,
    mode="reciters",
    title="🎙️ اختر القارئ:",
):
    reciters = unique_reciters(
        get_reciters()
    )

    if not reciters:
        await update.message.reply_text(
            "⚠️ تعذر تحميل قائمة القراء حاليًا.",
            reply_markup=menu_keyboard([]),
        )
        return

    context.user_data["mode"] = mode
    context.user_data["quran_mode"] = False
    context.user_data["reciter_list"] = reciters

    await update.message.reply_text(
        f"{title}\n\n"
        f"عدد القراء المتاحين: {len(reciters)}",
        reply_markup=make_all_reciter_keyboard(
            reciters
        ),
    )


# =========================================================
# اختيار سريع
# =========================================================

async def show_quick(
    update,
    context,
):
    context.user_data.clear()
    context.user_data["mode"] = "quick"
    context.user_data["quran_mode"] = False

    letters = [
        "ا",
        "ب",
        "ت",
        "ث",
        "ج",
        "ح",
        "خ",
        "د",
        "ذ",
        "ر",
        "ز",
        "س",
        "ش",
        "ص",
        "ض",
        "ط",
        "ظ",
        "ع",
        "غ",
        "ف",
        "ق",
        "ك",
        "ل",
        "م",
        "ن",
        "ه",
        "و",
        "ي",
    ]

    rows = []

    for i in range(
        0,
        len(letters),
        5,
    ):
        rows.append(
            letters[i:i + 5]
        )

    await update.message.reply_text(
        "⚡ اختيار سريع\n\n"
        "اختر أول حرف من اسم القارئ:",
        reply_markup=menu_keyboard(rows),
    )


async def quick_letter(
    update,
    context,
    letter,
):
    reciters = unique_reciters(
        get_reciters()
    )

    normalized_letter = normalize_text(
        letter
    )

    matched = []

    for reciter in reciters:

        name = normalize_text(
            get_name(reciter)
        )

        if name.startswith(
            normalized_letter
        ):
            matched.append(reciter)

    if not matched:
        await update.message.reply_text(
            "❌ لم أجد قارئًا بهذا الحرف.",
            reply_markup=menu_keyboard([]),
        )
        return

    context.user_data["mode"] = (
        "quick_reciter"
    )

    context.user_data["quran_mode"] = False

    context.user_data[
        "reciter_list"
    ] = matched

    await update.message.reply_text(
        f"⚡ القراء الذين يبدأ اسمهم "
        f"بحرف «{letter}»:",
        reply_markup=make_all_reciter_keyboard(
            matched
        ),
    )


# =========================================================
# الاختيار المتقدم
# =========================================================

async def show_advanced(
    update,
    context,
):
    context.user_data.clear()

    await show_reciters(
        update,
        context,
        mode="advanced_reciter",
        title="⚙️ اختيار متقدم\n\nاختر القارئ:",
    )


# =========================================================
# إيجاد القارئ
# =========================================================

def find_reciter_by_name(
    name,
    reciters=None,
):
    target = normalize_text(name)

    if reciters is None:
        reciters = get_reciters()

    for reciter in reciters:

        if normalize_text(
            get_name(reciter)
        ) == target:
            return reciter

    return None


# =========================================================
# مطابقة الرواية مع المصحف
# =========================================================

def moshaf_matches_riwaya(
    moshaf,
    selected_id,
    selected_name,
):
    moshaf_id = get_moshaf_rewaya_id(
        moshaf
    )

    moshaf_name = normalize_text(
        get_moshaf_rewaya_name(
            moshaf
        )
    )

    wanted_name = normalize_text(
        selected_name
    )

    if selected_id and moshaf_id:

        if str(moshaf_id) == str(
            selected_id
        ):
            return True

    if wanted_name and moshaf_name:

        if wanted_name == moshaf_name:
            return True

        if wanted_name in moshaf_name:
            return True

        if moshaf_name in wanted_name:
            return True

    return False


# =========================================================
# الروايات
# =========================================================

async def show_riwayat(
    update,
    context,
):
    riwayat = get_riwayat()

    if not riwayat:
        await update.message.reply_text(
            "⚠️ تعذر تحميل الروايات حاليًا.",
            reply_markup=menu_keyboard([]),
        )
        return

    context.user_data.clear()

    context.user_data["mode"] = "riwaya"
    context.user_data["quran_mode"] = False

    names = []

    for item in riwayat:

        name = get_riwaya_name(item)

        if name:
            names.append(name)

    rows = []

    for i in range(
        0,
        len(names),
        2,
    ):
        rows.append(
            names[i:i + 2]
        )

    await update.message.reply_text(
        "📜 اختر الرواية:",
        reply_markup=menu_keyboard(rows),
    )


async def handle_riwaya_selected(
    update,
    context,
    name,
):
    riwayat = get_riwayat()

    selected = None

    for item in riwayat:

        if normalize_text(
            get_riwaya_name(item)
        ) == normalize_text(name):

            selected = item
            break

    if selected is None:
        await update.message.reply_text(
            "⚠️ لم أجد هذه الرواية.",
            reply_markup=menu_keyboard([]),
        )
        return

    selected_id = get_riwaya_id(
        selected
    )

    selected_name = get_riwaya_name(
        selected
    )

    matching = []

    for reciter in get_reciters():

        moshafs = get_moshaf_list(
            reciter
        )

        for moshaf in moshafs:

            if moshaf_matches_riwaya(
                moshaf,
                selected_id,
                selected_name,
            ):
                matching.append(reciter)
                break

    matching = unique_reciters(
        matching
    )

    context.user_data[
        "selected_riwaya_id"
    ] = selected_id

    context.user_data[
        "selected_riwaya_name"
    ] = selected_name

    context.user_data[
        "mode"
    ] = "riwaya_reciter"

    context.user_data[
        "quran_mode"
    ] = False

    context.user_data[
        "reciter_list"
    ] = matching

    if not matching:
        await update.message.reply_text(
            f"📜 الرواية: {selected_name}\n\n"
            "⚠️ لم أجد قراء مرتبطين "
            "بهذه الرواية في المصدر الحالي.",
            reply_markup=menu_keyboard([]),
        )
        return

    await update.message.reply_text(
        f"📜 الرواية: {selected_name}\n\n"
        f"🎙️ اختر القارئ:\n"
        f"عدد القراء: {len(matching)}",
        reply_markup=make_all_reciter_keyboard(
            matching
        ),
    )


# =========================================================
# اختيار القارئ
# =========================================================

async def handle_reciter_selected(
    update,
    context,
):
    name = update.message.text

    reciters = context.user_data.get(
        "reciter_list"
    )

    if not reciters:
        reciters = get_reciters()

    reciter = find_reciter_by_name(
        name,
        reciters,
    )

    if not reciter:
        return False

    moshafs = get_moshaf_list(
        reciter
    )

    if not moshafs:
        await update.message.reply_text(
            "⚠️ لا توجد مصاحف صوتية متاحة لهذا القارئ.",
            reply_markup=menu_keyboard([]),
        )
        return True

    selected_riwaya_id = (
        context.user_data.get(
            "selected_riwaya_id"
        )
    )

    selected_riwaya_name = (
        context.user_data.get(
            "selected_riwaya_name"
        )
    )

    if (
        selected_riwaya_id
        or selected_riwaya_name
    ):

        filtered = [
            moshaf
            for moshaf in moshafs
            if moshaf_matches_riwaya(
                moshaf,
                selected_riwaya_id,
                selected_riwaya_name,
            )
        ]

        if filtered:
            moshafs = filtered

    context.user_data[
        "selected_reciter"
    ] = reciter

    context.user_data[
        "moshaf_list"
    ] = moshafs

    context.user_data[
        "mode"
    ] = "moshaf"

    context.user_data[
        "quran_mode"
    ] = False

    names = []

    for moshaf in moshafs:

        moshaf_name = (
            get_moshaf_rewaya_name(
                moshaf
            )
            or moshaf.get("name")
            or "مصحف صوتي"
        )

        names.append(
            str(moshaf_name)
        )

    rows = []

    for i in range(
        0,
        len(names),
        2,
    ):
        rows.append(
            names[i:i + 2]
        )

    await update.message.reply_text(
        f"🎙️ القارئ: "
        f"{get_name(reciter)}\n\n"
        "📜 اختر الرواية / المصحف:",
        reply_markup=menu_keyboard(rows),
    )

    return True


# =========================================================
# اختيار المصحف الصوتي
# =========================================================

def find_moshaf_by_name(
    name,
    moshafs,
):
    target = normalize_text(name)

    for moshaf in moshafs:

        moshaf_name = (
            get_moshaf_rewaya_name(
                moshaf
            )
            or moshaf.get("name")
            or "مصحف صوتي"
        )

        if normalize_text(
            moshaf_name
        ) == target:

            return moshaf

    return None


async def handle_moshaf_selected(
    update,
    context,
):
    name = update.message.text

    moshafs = context.user_data.get(
        "moshaf_list",
        [],
    )

    moshaf = find_moshaf_by_name(
        name,
        moshafs,
    )

    if not moshaf:
        return False

    context.user_data[
        "selected_moshaf"
    ] = moshaf

    context.user_data[
        "mode"
    ] = "sura"

    context.user_data[
        "quran_mode"
    ] = False

    suras = get_suras()

    allowed = get_moshaf_surah_list(
        moshaf
    )

    allowed_ids = set()

    if allowed:

        for value in re.split(
            r"[,\s]+",
            allowed,
        ):
            value = value.strip()

            if value.isdigit():
                allowed_ids.add(
                    int(value)
                )

    names = []

    for sura in suras:

        sid = get_sura_id(sura)

        if (
            allowed_ids
            and sid not in allowed_ids
        ):
            continue

        name = get_sura_name(sura)

        if name:
            names.append(name)

    rows = []

    for i in range(
        0,
        len(names),
        3,
    ):
        rows.append(
            names[i:i + 3]
        )

    reciter = context.user_data.get(
        "selected_reciter"
    )

    await update.message.reply_text(
        f"🎙️ {get_name(reciter)}\n\n"
        "📖 اختر السورة:",
        reply_markup=menu_keyboard(rows),
    )

    return True


# =========================================================
# إرسال السورة الصوتية
# =========================================================

async def send_surah_audio(
    update,
    context,
    sura,
):
    reciter = context.user_data.get(
        "selected_reciter"
    )

    moshaf = context.user_data.get(
        "selected_moshaf"
    )

    if not reciter or not moshaf:
        await update.message.reply_text(
            "⚠️ حدث خطأ في الاختيار."
        )
        return

    server = get_moshaf_server(
        moshaf
    )

    sura_id = get_sura_id(
        sura
    )

    if not server or not sura_id:
        await update.message.reply_text(
            "⚠️ الرابط الصوتي غير متوفر لهذه السورة."
        )
        return

    server = (
        server.rstrip("/")
        + "/"
    )

    filename = f"{sura_id:03d}.mp3"

    url = server + filename

    await update.message.reply_text(
        f"⏳ جاري تجهيز سورة "
        f"{get_sura_name(sura)}..."
    )

    try:

        response = requests.get(
            url,
            timeout=90,
            stream=True,
        )

        response.raise_for_status()

        total = 0
        chunks = []

        for chunk in response.iter_content(
            chunk_size=1024 * 256
        ):

            if not chunk:
                continue

            total += len(chunk)

            # يبقى السقف موجودًا لأن Bot API العادي
            # لا يقبل رفع ملف صوتي أكبر من 50MB.
            if total > MAX_AUDIO_BYTES:

                await update.message.reply_text(
                    "⚠️ حجم هذه السورة أكبر من "
                    "الحد المسموح به لإرسال الملفات "
                    "عبر البوت حاليًا.\n\n"
                    "السورة محفوظة كملف واحد، "
                    "لكن إرسال الملفات الأكبر من 50MB "
                    "يحتاج إلى Local Bot API Server."
                )

                return

            chunks.append(chunk)

        audio_data = b"".join(
            chunks
        )

        if not audio_data:
            raise ValueError(
                "Empty audio response"
            )

        audio = io.BytesIO(
            audio_data
        )

        audio.name = (
            f"{get_sura_name(sura)}.mp3"
        )

        caption = (
            f"🎙️ {get_name(reciter)}\n"
            f"📜 "
            f"{get_moshaf_rewaya_name(moshaf) or 'مصحف'}\n"
            f"📖 سورة "
            f"{get_sura_name(sura)}"
        )

        # =================================================
        # زر فتح التطبيق المصغر على نفس السورة
        # =================================================

        mini_app_url = (
            f"{MINI_APP_URL}?surah={sura_id}"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📖 فتح المصحف",
                        web_app=WebAppInfo(
                            url=mini_app_url
                        ),
                    )
                ]
            ]
        )

        await update.message.reply_audio(
            audio=audio,
            caption=caption,
            reply_markup=keyboard,
        )

    except Exception as e:

        logging.exception(
            "Audio error: %s",
            e,
        )

        await update.message.reply_text(
            "❌ تعذر تحميل السورة الصوتية حاليًا.\n"
            "حاول مرة أخرى بعد قليل."
        )


# =========================================================
# اختيار السورة الصوتية
# =========================================================

async def handle_sura_selected(
    update,
    context,
):
    name = update.message.text

    sura = find_sura_by_name(
        name
    )

    if not sura:
        return False

    await send_surah_audio(
        update,
        context,
        sura,
    )

    return True


# =========================================================
# العشوائي
# =========================================================

async def show_random(
    update,
    context,
):
    context.user_data.clear()

    context.user_data[
        "quran_mode"
    ] = False

    reciters = unique_reciters(
        get_reciters()
    )

    valid_reciters = []

    for reciter in reciters:

        moshafs = get_moshaf_list(
            reciter
        )

        good_moshafs = [
            m
            for m in moshafs
            if get_moshaf_server(m)
        ]

        if good_moshafs:
            valid_reciters.append(
                (
                    reciter,
                    good_moshafs,
                )
            )

    if not valid_reciters:
        await update.message.reply_text(
            "⚠️ لا توجد تلاوات متاحة حاليًا."
        )
        return

    reciter, moshafs = random.choice(
        valid_reciters
    )

    moshaf = random.choice(
        moshafs
    )

    suras = get_suras()

    allowed = get_moshaf_surah_list(
        moshaf
    )

    allowed_ids = set()

    if allowed:

        for value in re.split(
            r"[,\s]+",
            allowed,
        ):

            if value.isdigit():
                allowed_ids.add(
                    int(value)
                )

    valid_suras = []

    for sura in suras:

        sid = get_sura_id(
            sura
        )

        if (
            not allowed_ids
            or sid in allowed_ids
        ):
            valid_suras.append(
                sura
            )

    if not valid_suras:
        valid_suras = suras

    sura = random.choice(
        valid_suras
    )

    context.user_data[
        "selected_reciter"
    ] = reciter

    context.user_data[
        "selected_moshaf"
    ] = moshaf

    await send_surah_audio(
        update,
        context,
        sura,
    )


# =========================================================
# الأذكار
# =========================================================

MORNING_TEXT = """
🌅 أذكار الصباح

أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

اللهم بك أصبحنا وبك أمسينا، وبك نحيا وبك نموت وإليك النشور.

رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.

سبحان الله وبحمده.
"""


EVENING_TEXT = """
🌙 أذكار المساء

أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

اللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير.

رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.

سبحان الله وبحمده.
"""


async def show_morning(
    update,
    context,
):
    await update.message.reply_text(
        MORNING_TEXT,
        reply_markup=menu_keyboard([]),
    )

    if MORNING_AUDIO.exists():

        try:

            with MORNING_AUDIO.open(
                "rb"
            ) as audio:

                await update.message.reply_audio(
                    audio=audio,
                    caption="🌅 أذكار الصباح",
                )

        except Exception:

            logging.exception(
                "Morning audio error"
            )


async def show_evening(
    update,
    context,
):
    await update.message.reply_text(
        EVENING_TEXT,
        reply_markup=menu_keyboard([]),
    )

    if EVENING_AUDIO.exists():

        try:

            with EVENING_AUDIO.open(
                "rb"
            ) as audio:

                await update.message.reply_audio(
                    audio=audio,
                    caption="🌙 أذكار المساء",
                )

        except Exception:

            logging.exception(
                "Evening audio error"
            )


# =========================================================
# تفسير القرآن
# =========================================================

async def show_tafsir(
    update,
    context,
):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📚 فتح تفسير القرآن",
                    url=TAFSIR_URL,
                )
            ]
        ]
    )

    await update.message.reply_text(
        "📚 تفسير القرآن\n\n"
        "يمكنك فتح موسوعة القرآن والتفاسير "
        "من الزر بالأسفل:",
        reply_markup=keyboard,
    )


# =========================================================
# الدرر السنية
# =========================================================

async def show_dorar(
    update,
    context,
):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📜 فتح الموسوعة الحديثية",
                    url=DORAR_URL,
                )
            ]
        ]
    )

    await update.message.reply_text(
        "📜 الدرر السنية\n\n"
        "الموسوعة الحديثية للبحث "
        "والتحقق من الأحاديث:",
        reply_markup=keyboard,
    )


# =========================================================
# القناة
# =========================================================

async def show_channel(
    update,
    context,
):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 الانتقال إلى قناتنا",
                    url=CHANNEL_URL,
                )
            ]
        ]
    )

    await update.message.reply_text(
        "📢 قناتنا على تيليجرام:",
        reply_markup=keyboard,
    )


# =========================================================
# اللغة
# =========================================================

async def show_language(
    update,
    context,
):
    rows = [
        ["🇸🇦 العربية"],
        ["🇬🇧 English"],
    ]

    await update.message.reply_text(
        "🌐 اختر اللغة:",
        reply_markup=menu_keyboard(rows),
    )


# =========================================================
# الرجوع
# =========================================================

async def go_back(
    update,
    context,
):
    mode = context.user_data.get(
        "mode"
    )

    if mode == "sura":

        if context.user_data.get(
            "quran_mode"
        ):

            await show_home(
                update,
                context,
            )

            return

        await show_reciters(
            update,
            context,
            mode="reciters",
            title="🎙️ اختر القارئ:",
        )

        return

    if mode == "moshaf":

        await show_reciters(
            update,
            context,
            mode="reciters",
            title="🎙️ اختر القارئ:",
        )

        return

    if mode in (
        "advanced_reciter",
        "quick_reciter",
        "riwaya_reciter",
    ):

        await show_home(
            update,
            context,
        )

        return

    if mode == "quick":

        await show_home(
            update,
            context,
        )

        return

    if mode in (
        "quran",
        "riwaya",
    ):

        await show_home(
            update,
            context,
        )

        return

    await show_home(
        update,
        context,
    )


# =========================================================
# معالج الرسائل الرئيسي
# =========================================================

async def handle_message(
    update,
    context,
):
    text = (
        update.message.text or ""
    ).strip()

    # =====================================================
    # إخفاء القائمة
    # =====================================================

    if text == BTN_HIDE:

        await hide_keyboard(
            update,
            context,
        )

        return

    # =====================================================
    # الرئيسية
    # =====================================================

    if text == BTN_HOME:

        await show_home(
            update,
            context,
        )

        return

    # =====================================================
    # رجوع
    # =====================================================

    if text == BTN_BACK:

        await go_back(
            update,
            context,
        )

        return

    # =====================================================
    # أزرار القائمة الرئيسية
    # =====================================================

    if text == BTN_QURAN:

        await show_quran(
            update,
            context,
        )

        return

    if text == BTN_RECITERS:

        await show_reciters(
            update,
            context,
            mode="reciters",
            title="🎙️ اختر القارئ:",
        )

        return

    if text == BTN_REWAYAT:

        await show_riwayat(
            update,
            context,
        )

        return

    if text == BTN_RANDOM:

        await show_random(
            update,
            context,
        )

        return

    if text == BTN_QUICK:

        await show_quick(
            update,
            context,
        )

        return

    if text == BTN_ADVANCED:

        await show_advanced(
            update,
            context,
        )

        return

    if text == BTN_MORNING:

        await show_morning(
            update,
            context,
        )

        return

    if text == BTN_EVENING:

        await show_evening(
            update,
            context,
        )

        return

    # =====================================================
    # تفسير القرآن
    # =====================================================

    if text == BTN_TAFSIR:

        await show_tafsir(
            update,
            context,
        )

        return

    # =====================================================
    # الدرر السنية
    # =====================================================

    if text == BTN_DORAR:

        await show_dorar(
            update,
            context,
        )

        return

    # =====================================================
    # القناة
    # =====================================================

    if text == BTN_CHANNEL:

        await show_channel(
            update,
            context,
        )

        return

    # =====================================================
    # اللغة
    # =====================================================

    if text == BTN_LANGUAGE:

        await show_language(
            update,
            context,
        )

        return

    # =====================================================
    # الحالة الحالية
    # =====================================================

    mode = context.user_data.get(
        "mode"
    )

    # =====================================================
    # المصحف
    #
    # اختيار السورة هنا يفتح التطبيق المصغر
    # مباشرة على نفس السورة.
    # =====================================================

    if mode == "quran":

        sura = find_sura_by_name(
            text
        )

        if sura:

            await open_quran_sura(
                update,
                context,
                sura,
            )

            return

    # =====================================================
    # اختيار الرواية
    # =====================================================

    if mode == "riwaya":

        await handle_riwaya_selected(
            update,
            context,
            text,
        )

        return

    # =====================================================
    # اختيار القارئ
    # =====================================================

    if mode in (
        "reciters",
        "quick_reciter",
        "advanced_reciter",
        "riwaya_reciter",
    ):

        handled = (
            await handle_reciter_selected(
                update,
                context,
            )
        )

        if handled:
            return

    # =====================================================
    # اختيار المصحف الصوتي
    # =====================================================

    if mode == "moshaf":

        handled = (
            await handle_moshaf_selected(
                update,
                context,
            )
        )

        if handled:
            return

    # =====================================================
    # اختيار السورة الصوتية
    # =====================================================

    if mode == "sura":

        handled = (
            await handle_sura_selected(
                update,
                context,
            )
        )

        if handled:
            return

    # =====================================================
    # اختيار حرف الاختيار السريع
    # =====================================================

    if mode == "quick":

        letters = {
            "ا", "ب", "ت", "ث",
            "ج", "ح", "خ", "د",
            "ذ", "ر", "ز", "س",
            "ش", "ص", "ض", "ط",
            "ظ", "ع", "غ", "ف",
            "ق", "ك", "ل", "م",
            "ن", "ه", "و", "ي",
        }

        if text in letters:

            await quick_letter(
                update,
                context,
                text,
            )

            return

    # =====================================================
    # اللغة
    # =====================================================

    if text == "🇸🇦 العربية":

        await update.message.reply_text(
            "🇸🇦 تم اختيار اللغة العربية.",
            reply_markup=HOME_MARKUP,
        )

        return

    if text == "🇬🇧 English":

        await update.message.reply_text(
            "🇬🇧 English language selection "
            "will be added to the next version.",
            reply_markup=HOME_MARKUP,
        )

        return

    # =====================================================
    # رسالة افتراضية
    # =====================================================

    await update.message.reply_text(
        "اختر أحد الأزرار الموجودة بالأسفل 👇",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# معالجة الأخطاء
# =========================================================

async def error_handler(
    update,
    context,
):
    logging.exception(
        "Unhandled exception",
        exc_info=context.error,
    )


# =========================================================
# تشغيل البوت
# =========================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN is missing."
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

    application.add_error_handler(
        error_handler
    )

    logging.info(
        "Bot is starting..."
    )

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
