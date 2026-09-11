import io
import logging
import os
import random
import re
import threading
import unicodedata
from pathlib import Path

import requests
from flask import Flask, jsonify, request

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
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

TAFSIR_URL = "https://quranenc.com/ar"
DORAR_URL = "https://dorar.net/hadith/search"
CHANNEL_URL = "https://t.me/x7oly"

MAX_AUDIO_BYTES = 49 * 1024 * 1024

PORT = int(os.getenv("PORT", "8080"))

# Railway يعطيك RAILWAY_PUBLIC_DOMAIN بعد إنشاء Public Domain
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()

# الأفضل أن تضيف WEBAPP_URL يدويًا في Railway.
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

if not WEBAPP_URL and RAILWAY_PUBLIC_DOMAIN:
    WEBAPP_URL = f"https://{RAILWAY_PUBLIC_DOMAIN}/quran"

# إزالة / الأخيرة
WEBAPP_URL = WEBAPP_URL.rstrip("/")


# =========================================================
# Flask Web App
# =========================================================

flask_app = Flask(__name__)


@flask_app.route("/")
def home():
    return """
    <!doctype html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>المصحف</title>
    </head>
    <body style="font-family:Arial;text-align:center;padding:40px">
        <h2>📖 المصحف</h2>
        <p>الخدمة تعمل بنجاح.</p>
        <a href="/quran">فتح المصحف</a>
    </body>
    </html>
    """


@flask_app.route("/quran")
def quran_page():
    sura = request.args.get("sura", "1")

    try:
        sura = int(sura)
    except Exception:
        sura = 1

    if sura < 1 or sura > 114:
        sura = 1

    html = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width,initial-scale=1,maximum-scale=1">

<title>📖 المصحف</title>

<script src="https://telegram.org/js/telegram-web-app.js"></script>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f5f0e6;
    color: #24221e;
    font-family: "Amiri", "Noto Naskh Arabic", serif;
}

.top {
    position: sticky;
    top: 0;
    z-index: 10;
    background: #eee5d4;
    border-bottom: 1px solid #d8ccb8;
    padding: 12px 10px;
    text-align: center;
}

.title {
    font-size: 21px;
    font-weight: bold;
}

.controls {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 9px;
}

button {
    border: 0;
    border-radius: 10px;
    padding: 9px 14px;
    background: #ded4c2;
    color: #24221e;
    font-size: 15px;
}

.container {
    max-width: 850px;
    margin: auto;
    padding: 20px 15px 50px;
}

.surah-title {
    text-align: center;
    font-size: 30px;
    margin: 10px 0;
}

.basmala {
    text-align: center;
    font-size: 25px;
    margin: 20px 0 30px;
}

.ayah {
    line-height: 2.35;
    font-size: 26px;
    text-align: justify;
    margin-bottom: 10px;
}

.number {
    display: inline-flex;
    width: 31px;
    height: 31px;
    border: 1px solid #777;
    border-radius: 50%;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    margin: 0 5px;
    vertical-align: middle;
}

.loading {
    text-align: center;
    font-size: 20px;
    padding: 50px 10px;
}

.bottom {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-top: 30px;
}

.bottom button {
    flex: 1;
}
</style>
</head>

<body>

<div class="top">
    <div class="title">📖 المصحف</div>

    <div class="controls">
        <button onclick="changeFont(-2)">−</button>
        <button onclick="changeFont(2)">+</button>
    </div>
</div>

<div class="container">

    <div id="title" class="surah-title">المصحف</div>

    <div class="basmala">
        بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
    </div>

    <div id="content" class="loading">
        جاري تحميل السورة...
    </div>

    <div class="bottom">
        <button onclick="previousSurah()">السورة السابقة</button>
        <button onclick="nextSurah()">السورة التالية</button>
    </div>

</div>

<script>
const tg = window.Telegram && window.Telegram.WebApp;

if (tg) {
    tg.ready();
    tg.expand();
}

let currentSurah = __SURA__;
let fontSize = Number(localStorage.getItem("quranFontSize") || 26);

document.documentElement.style.setProperty(
    "--quran-font-size",
    fontSize + "px"
);

async function loadSurah(id) {
    if (id < 1 || id > 114) return;

    currentSurah = id;

    document.getElementById("content").innerHTML =
        '<div class="loading">جاري تحميل السورة...</div>';

    try {
        const response = await fetch("/api/quran/surah/" + id);

        if (!response.ok) {
            throw new Error("API error");
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error("No data");
        }

        document.getElementById("title").innerText =
            data.surah.name;

        let html = "";

        for (const ayah of data.surah.ayahs) {
            html += `
                <span class="ayah">
                    ${ayah.text}
                    <span class="number">${ayah.numberInSurah}</span>
                </span>
            `;
        }

        document.getElementById("content").innerHTML = html;

        applyFont();

        history.replaceState(
            null,
            "",
            "/quran?sura=" + id
        );

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    } catch (error) {
        document.getElementById("content").innerHTML =
            '<div class="loading">تعذر تحميل السورة. حاول مرة أخرى.</div>';
    }
}

function applyFont() {
    document.querySelectorAll(".ayah").forEach(function(el) {
        el.style.fontSize = fontSize + "px";
    });
}

function changeFont(value) {
    fontSize += value;

    if (fontSize < 18) fontSize = 18;
    if (fontSize > 42) fontSize = 42;

    localStorage.setItem(
        "quranFontSize",
        fontSize
    );

    applyFont();
}

function previousSurah() {
    if (currentSurah > 1) {
        loadSurah(currentSurah - 1);
    }
}

function nextSurah() {
    if (currentSurah < 114) {
        loadSurah(currentSurah + 1);
    }
}

loadSurah(currentSurah);
</script>

</body>
</html>
"""

    html = html.replace("__SURA__", str(sura))

    return html


@flask_app.route("/api/quran/surah/<int:sura_id>")
def quran_api(sura_id):
    if sura_id < 1 or sura_id > 114:
        return jsonify({
            "success": False,
            "error": "Invalid surah"
        }), 400

    url = (
        "https://api.alquran.cloud/v1/"
        f"surah/{sura_id}/quran-uthmani"
    )

    try:
        response = requests.get(
            url,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if data.get("status") != "OK":
            return jsonify({
                "success": False
            }), 502

        return jsonify({
            "success": True,
            "surah": data["data"]
        })

    except Exception as e:
        logging.exception(
            "Quran API error: %s",
            e
        )

        return jsonify({
            "success": False,
            "error": "Quran API unavailable"
        }), 502


def run_flask():
    flask_app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


# =========================================================
# Logging
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================================================
# أسماء السور
# =========================================================

SURAH_NAMES = [
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
# أزرار القائمة الرئيسية
# =========================================================

BTN_RECITERS = "🎙️ القرائ"
BTN_RIWAYAT = "📜 الروايات"
BTN_RANDOM = "🎲 عشوائي"
BTN_QUICK = "⚡ اختيار سريع"
BTN_ADVANCED = "⚙️ اختيار متقدم"
BTN_MORNING = "🌅 أذكار الصباح"
BTN_EVENING = "🌙 أذكار المساء"
BTN_TAFSIR = "📚 تفسير القرآن"
BTN_DORAR = "📜 الدرر السنية"
BTN_CHANNEL = "📢 قناتنا على تيليجرام"
BTN_LANGUAGE = "🌐 تغيير اللغة"
BTN_HIDE = "❌ إخفاء القائمة"

BTN_BACK = "🔙 رجوع"
BTN_HOME = "🏠 القائمة الرئيسية"


# =========================================================
# القائمة السفلية
# =========================================================

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [BTN_RECITERS, BTN_RIWAYAT],
        [BTN_RANDOM, BTN_QUICK],
        [BTN_ADVANCED],
        [BTN_MORNING, BTN_EVENING],
        [BTN_TAFSIR, BTN_DORAR],
        [BTN_CHANNEL, BTN_LANGUAGE],
        [BTN_HIDE],
    ],
    resize_keyboard=True,
    is_persistent=True,
    input_field_placeholder="اختر من القائمة..."
)


BACK_KEYBOARD = ReplyKeyboardMarkup(
    [
        [BTN_BACK, BTN_HOME],
    ],
    resize_keyboard=True,
    is_persistent=True
)


# =========================================================
# Cache
# =========================================================

_cache = {}


def api_get(endpoint, params=None):
    key = (
        endpoint,
        tuple(sorted((params or {}).items()))
    )

    if key in _cache:
        return _cache[key]

    url = API_BASE + endpoint

    response = requests.get(
        url,
        params=params or {},
        timeout=25
    )

    response.raise_for_status()

    data = response.json()

    _cache[key] = data

    return data


# =========================================================
# أدوات
# =========================================================

def normalize_text(text):
    text = str(text or "")

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )

    return text.lower().strip()


def quran_web_url(sura_id=None):
    if not WEBAPP_URL:
        return None

    if sura_id:
        return f"{WEBAPP_URL}/?sura={int(sura_id)}"

    return WEBAPP_URL


def quran_open_markup(sura_id=None):
    url = quran_web_url(sura_id)

    if not url:
        return None

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📖 فتح المصحف",
                web_app=WebAppInfo(url=url)
            )
        ]
    ])


def surah_name(sura_id):
    if 1 <= int(sura_id) <= 114:
        return SURAH_NAMES[int(sura_id) - 1]

    return f"السورة {sura_id}"


def back_markup():
    return BACK_KEYBOARD


# =========================================================
# زر تيليجرام الأزرق
# =========================================================

async def setup_quran_menu_button(application):
    if not WEBAPP_URL:
        logger.warning(
            "WEBAPP_URL غير موجود، لذلك لم يتم إنشاء زر المصحف الأزرق."
        )
        return

    try:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="📖 المصحف",
                web_app=WebAppInfo(
                    url=WEBAPP_URL
                )
            )
        )

        logger.info(
            "تم إنشاء زر المصحف الأزرق: %s",
            WEBAPP_URL
        )

    except Exception as e:
        logger.exception(
            "فشل إنشاء زر المصحف: %s",
            e
        )


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    text = (
        "السلام عليكم ورحمة الله وبركاته 🌿\n\n"
        "أهلاً بك في بوت القرآن الكريم 📖\n\n"
        "اختر من القائمة الموجودة أسفل الشاشة.\n\n"
        "ويمكنك فتح المصحف مباشرة من زر "
        "📖 المصحف بجانب خانة الكتابة."
    )

    await update.message.reply_text(
        text,
        reply_markup=MAIN_KEYBOARD
    )


# =========================================================
# المصحف
# =========================================================

async def show_quran(update, context):
    if not WEBAPP_URL:
        await update.message.reply_text(
            "⚠️ المصحف غير مفعّل حالياً.\n\n"
            "يجب إضافة WEBAPP_URL في Railway."
        )
        return

    await update.message.reply_text(
        "📖 اضغط هنا لفتح المصحف:",
        reply_markup=quran_open_markup()
    )


# =========================================================
# القراء
# =========================================================

def get_reciters():
    data = api_get(
        "/reciters",
        {"language": "ar"}
    )

    return data.get("reciters", [])


def get_riwayat():
    data = api_get(
        "/riwayat",
        {"language": "ar"}
    )

    return data.get("riwayat", [])


def get_all_moshaf(reciter):
    result = []

    for moshaf in reciter.get("moshaf", []):
        result.append(moshaf)

    return result


def find_reciter(reciter_id):
    for reciter in get_reciters():
        if str(reciter.get("id")) == str(reciter_id):
            return reciter

    return None


def get_moshaf(reciter, moshaf_id=None):
    moshafs = get_all_moshaf(reciter)

    if not moshafs:
        return None

    if moshaf_id is None:
        return moshafs[0]

    for moshaf in moshafs:
        if str(moshaf.get("id")) == str(moshaf_id):
            return moshaf

    return moshafs[0]


def has_surah(moshaf, sura_id):
    values = str(
        moshaf.get("surah_list", "")
    ).split(",")

    return str(sura_id) in values


# =========================================================
# عرض القراء
# =========================================================

async def show_reciters(update, context):
    try:
        reciters = get_reciters()

        if not reciters:
            await update.message.reply_text(
                "لم أستطع تحميل القراء حالياً.",
                reply_markup=BACK_KEYBOARD
            )
            return

        buttons = []

        for reciter in reciters:
            name = reciter.get(
                "name",
                "قارئ غير معروف"
            )

            rid = reciter.get("id")

            buttons.append([
                InlineKeyboardButton(
                    f"🎙️ {name}",
                    callback_data=f"reciter:{rid}"
                )
            ])

        await update.message.reply_text(
            "🎙️ اختر القارئ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        logger.exception(e)

        await update.message.reply_text(
            "حدث خطأ أثناء تحميل قائمة القراء.",
            reply_markup=BACK_KEYBOARD
        )


# =========================================================
# اختيار السورة للقارئ
# =========================================================

async def show_reciter_surahs(
    query,
    reciter_id
):
    reciter = find_reciter(reciter_id)

    if not reciter:
        await query.edit_message_text(
            "القارئ غير موجود."
        )
        return

    context_text = (
        f"🎙️ القارئ: {reciter.get('name')}\n\n"
        "اختر الرواية:"
    )

    moshafs = get_all_moshaf(reciter)

    buttons = []

    for moshaf in moshafs:
        mid = moshaf.get("id")
        name = moshaf.get(
            "name",
            "رواية غير معروفة"
        )

        buttons.append([
            InlineKeyboardButton(
                f"📜 {name}",
                callback_data=f"moshaf:{reciter_id}:{mid}"
            )
        ])

    await query.edit_message_text(
        context_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_moshaf_surahs(
    query,
    reciter_id,
    moshaf_id
):
    reciter = find_reciter(reciter_id)

    if not reciter:
        await query.edit_message_text(
            "القارئ غير موجود."
        )
        return

    moshaf = get_moshaf(
        reciter,
        moshaf_id
    )

    if not moshaf:
        await query.edit_message_text(
            "الرواية غير موجودة."
        )
        return

    surahs = []

    for value in str(
        moshaf.get("surah_list", "")
    ).split(","):

        value = value.strip()

        if value.isdigit():
            sid = int(value)

            if 1 <= sid <= 114:
                surahs.append(sid)

    buttons = []

    row = []

    for sid in surahs:
        row.append(
            InlineKeyboardButton(
                f"{sid}. {surah_name(sid)}",
                callback_data=(
                    f"play:{reciter_id}:"
                    f"{moshaf_id}:{sid}"
                )
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await query.edit_message_text(
        (
            f"🎙️ {reciter.get('name')}\n"
            f"📜 {moshaf.get('name')}\n\n"
            "اختر السورة:"
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# الروايات
# =========================================================

async def show_riwayat(update, context):
    try:
        riwayat = get_riwayat()

        if not riwayat:
            await update.message.reply_text(
                "لم أستطع تحميل الروايات حالياً.",
                reply_markup=BACK_KEYBOARD
            )
            return

        buttons = []

        for item in riwayat:
            rid = item.get("id")

            name = item.get(
                "name",
                "رواية"
            )

            buttons.append([
                InlineKeyboardButton(
                    f"📜 {name}",
                    callback_data=f"riwaya:{rid}"
                )
            ])

        await update.message.reply_text(
            "📜 اختر الرواية:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception:
        logger.exception("Riwayat error")

        await update.message.reply_text(
            "حدث خطأ أثناء تحميل الروايات.",
            reply_markup=BACK_KEYBOARD
        )


async def show_riwaya_reciters(
    query,
    riwaya_id
):
    data = api_get(
        "/reciters",
        {
            "language": "ar",
            "rewaya": riwaya_id
        }
    )

    reciters = data.get(
        "reciters",
        []
    )

    if not reciters:
        await query.edit_message_text(
            "لا يوجد قراء لهذه الرواية حالياً."
        )
        return

    buttons = []

    for reciter in reciters:
        rid = reciter.get("id")

        buttons.append([
            InlineKeyboardButton(
                f"🎙️ {reciter.get('name')}",
                callback_data=f"reciter:{rid}"
            )
        ])

    await query.edit_message_text(
        "🎙️ اختر القارئ:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# اختيار سريع
# =========================================================

async def quick_choice(update, context):
    try:
        reciters = get_reciters()

        available = []

        for reciter in reciters:
            for moshaf in get_all_moshaf(reciter):
                surahs = str(
                    moshaf.get(
                        "surah_list",
                        ""
                    )
                ).split(",")

                valid_surahs = [
                    int(x)
                    for x in surahs
                    if x.strip().isdigit()
                ]

                if valid_surahs:
                    available.append(
                        (
                            reciter,
                            moshaf,
                            valid_surahs
                        )
                    )

        if not available:
            await update.message.reply_text(
                "لا توجد تسجيلات متاحة حالياً.",
                reply_markup=BACK_KEYBOARD
            )
            return

        reciter, moshaf, surahs = random.choice(
            available
        )

        sid = random.choice(surahs)

        await send_surah_audio(
            update,
            reciter,
            moshaf,
            sid
        )

    except Exception:
        logger.exception("Quick choice error")

        await update.message.reply_text(
            "حدث خطأ أثناء الاختيار السريع.",
            reply_markup=BACK_KEYBOARD
        )


# =========================================================
# عشوائي
# =========================================================

async def random_choice(update, context):
    await quick_choice(
        update,
        context
    )


# =========================================================
# اختيار متقدم
# =========================================================

async def show_advanced(update, context):
    try:
        reciters = get_reciters()

        buttons = []

        for reciter in reciters:
            rid = reciter.get("id")

            buttons.append([
                InlineKeyboardButton(
                    f"🎙️ {reciter.get('name')}",
                    callback_data=f"advanced:{rid}"
                )
            ])

        await update.message.reply_text(
            "⚙️ الاختيار المتقدم\n\n"
            "اختر القارئ أولاً:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception:
        logger.exception("Advanced error")

        await update.message.reply_text(
            "حدث خطأ.",
            reply_markup=BACK_KEYBOARD
        )


async def advanced_reciter(
    query,
    reciter_id
):
    reciter = find_reciter(reciter_id)

    if not reciter:
        await query.edit_message_text(
            "القارئ غير موجود."
        )
        return

    buttons = []

    for moshaf in get_all_moshaf(reciter):
        mid = moshaf.get("id")

        buttons.append([
            InlineKeyboardButton(
                f"📜 {moshaf.get('name')}",
                callback_data=(
                    f"advancedmoshaf:"
                    f"{reciter_id}:{mid}"
                )
            )
        ])

    await query.edit_message_text(
        (
            f"🎙️ {reciter.get('name')}\n\n"
            "اختر الرواية:"
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# =========================================================
# إرسال الصوت
# =========================================================

def audio_urls(moshaf, sura_id):
    server = str(
        moshaf.get("server", "")
    ).strip()

    if not server:
        return []

    server = server.rstrip("/") + "/"

    sid = int(sura_id)

    return [
        f"{server}{sid:03d}.mp3",
        f"{server}{sid}.mp3",
    ]


def download_audio(url):
    response = requests.get(
        url,
        timeout=60,
        stream=True
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

        if total > MAX_AUDIO_BYTES:
            raise ValueError(
                "Audio file is too large"
            )

        chunks.append(chunk)

    return b"".join(chunks)


async def send_surah_audio(
    update,
    reciter,
    moshaf,
    sura_id
):
    name = reciter.get(
        "name",
        "المؤدي غير معروف"
    )

    moshaf_name = moshaf.get(
        "name",
        ""
    )

    title = surah_name(sura_id)

    urls = audio_urls(
        moshaf,
        sura_id
    )

    if not urls:
        await update.message.reply_text(
            "لا يوجد رابط صوت لهذه السورة.",
            reply_markup=BACK_KEYBOARD
        )
        return

    audio_data = None

    for url in urls:
        try:
            logger.info(
                "Trying audio URL: %s",
                url
            )

            audio_data = download_audio(url)

            if audio_data:
                break

        except Exception as e:
            logger.warning(
                "Audio URL failed: %s - %s",
                url,
                e
            )

    if not audio_data:
        await update.message.reply_text(
            "حدث خطأ أثناء تحميل السورة، "
            "حاول مرة أخرى.",
            reply_markup=BACK_KEYBOARD
        )
        return

    caption = (
        f"🎧 {title}\n\n"
        f"🎙️ القارئ: {name}\n"
        f"📜 {moshaf_name}"
    )

    keyboard = quran_open_markup(
        sura_id
    )

    audio_file = io.BytesIO(
        audio_data
    )

    audio_file.name = (
        f"{sura_id:03d}-{title}.mp3"
    )

    await update.message.reply_audio(
        audio=audio_file,
        caption=caption,
        reply_markup=keyboard,
        title=f"{title} - {name}",
        performer=name
    )


# =========================================================
# الأذكار
# =========================================================

MORNING_TEXT = """
🌅 أذكار الصباح

أصبحنا وأصبح الملك لله، والحمد لله.

اللهم بك أصبحنا وبك أمسينا، وبك نحيا وبك نموت وإليك النشور.

رضيت بالله رباً، وبالإسلام ديناً، وبمحمد ﷺ نبياً.

حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم.

سبحان الله وبحمده.

اللهم صل وسلم على نبينا محمد ﷺ.
"""


EVENING_TEXT = """
🌙 أذكار المساء

أمسينا وأمسى الملك لله، والحمد لله.

اللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير.

رضيت بالله رباً، وبالإسلام ديناً، وبمحمد ﷺ نبياً.

حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم.

سبحان الله وبحمده.

اللهم صل وسلم على نبينا محمد ﷺ.
"""


async def morning(update, context):
    await update.message.reply_text(
        MORNING_TEXT,
        reply_markup=BACK_KEYBOARD
    )


async def evening(update, context):
    await update.message.reply_text(
        EVENING_TEXT,
        reply_markup=BACK_KEYBOARD
    )


# =========================================================
# التفسير
# =========================================================

async def show_tafsir(update, context):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📚 فتح تفسير القرآن",
                url=TAFSIR_URL
            )
        ]
    ])

    await update.message.reply_text(
        "📚 تفسير القرآن\n\n"
        "اضغط على الزر لفتح موقع تفسير القرآن:",
        reply_markup=keyboard
    )


# =========================================================
# الدرر السنية
# =========================================================

async def show_dorar(update, context):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📜 فتح الدرر السنية",
                url=DORAR_URL
            )
        ]
    ])

    await update.message.reply_text(
        "📜 الدرر السنية\n\n"
        "اضغط على الزر لفتح الموقع:",
        reply_markup=keyboard
    )


# =========================================================
# القناة
# =========================================================

async def show_channel(update, context):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📢 فتح القناة",
                url=CHANNEL_URL
            )
        ]
    ])

    await update.message.reply_text(
        "📢 قناتنا على تيليجرام:",
        reply_markup=keyboard
    )


# =========================================================
# اللغة
# =========================================================

async def show_language(update, context):
    await update.message.reply_text(
        "🌐 تغيير اللغة\n\n"
        "اللغة العربية مفعلة حالياً.\n\n"
        "سيتم إضافة اللغات الأخرى لاحقاً.",
        reply_markup=BACK_KEYBOARD
    )


# =========================================================
# الرجوع
# =========================================================

async def go_back(update, context):
    await update.message.reply_text(
        "رجعنا للقائمة الرئيسية 🏠",
        reply_markup=MAIN_KEYBOARD
    )


async def go_home(update, context):
    await update.message.reply_text(
        "🏠 القائمة الرئيسية",
        reply_markup=MAIN_KEYBOARD
    )


# =========================================================
# إخفاء القائمة
# =========================================================

async def hide_menu(update, context):
    await update.message.reply_text(
        "تم إخفاء القائمة.\n\n"
        "اكتب /start لإظهارها من جديد.",
        reply_markup=ReplyKeyboardRemove()
    )


# =========================================================
# Callback Queries
# =========================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    data = query.data or ""

    try:

        # ---------------------------------------------
        # اختيار قارئ
        # ---------------------------------------------

        if data.startswith("reciter:"):
            reciter_id = data.split(":")[1]

            await show_reciter_surahs(
                query,
                reciter_id
            )

            return

        # ---------------------------------------------
        # اختيار رواية
        # ---------------------------------------------

        if data.startswith("moshaf:"):
            parts = data.split(":")

            reciter_id = parts[1]
            moshaf_id = parts[2]

            await show_moshaf_surahs(
                query,
                reciter_id,
                moshaf_id
            )

            return

        # ---------------------------------------------
        # تشغيل سورة
        # ---------------------------------------------

        if data.startswith("play:"):
            parts = data.split(":")

            reciter_id = parts[1]
            moshaf_id = parts[2]
            sura_id = int(parts[3])

            reciter = find_reciter(
                reciter_id
            )

            if not reciter:
                await query.message.reply_text(
                    "القارئ غير موجود."
                )
                return

            moshaf = get_moshaf(
                reciter,
                moshaf_id
            )

            if not moshaf:
                await query.message.reply_text(
                    "الرواية غير موجودة."
                )
                return

            await query.message.reply_text(
                "⏳ جاري تحميل السورة..."
            )

            await send_surah_audio(
                query,
                reciter,
                moshaf,
                sura_id
            )

            return

        # ---------------------------------------------
        # الرواية
        # ---------------------------------------------

        if data.startswith("riwaya:"):
            riwaya_id = data.split(":")[1]

            await show_riwaya_reciters(
                query,
                riwaya_id
            )

            return

        # ---------------------------------------------
        # اختيار متقدم
        # ---------------------------------------------

        if data.startswith("advanced:"):
            reciter_id = data.split(":")[1]

            await advanced_reciter(
                query,
                reciter_id
            )

            return

        # ---------------------------------------------
        # اختيار متقدم - الرواية
        # ---------------------------------------------

        if data.startswith("advancedmoshaf:"):
            parts = data.split(":")

            reciter_id = parts[1]
            moshaf_id = parts[2]

            await show_moshaf_surahs(
                query,
                reciter_id,
                moshaf_id
            )

            return

    except Exception:
        logger.exception(
            "Callback error"
        )

        try:
            await query.message.reply_text(
                "حدث خطأ، حاول مرة أخرى."
            )
        except Exception:
            pass


# =========================================================
# الرسائل النصية
# =========================================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (update.message.text or "").strip()

    if text == BTN_RECITERS:
        await show_reciters(
            update,
            context
        )
        return

    if text == BTN_RIWAYAT:
        await show_riwayat(
            update,
            context
        )
        return

    if text == BTN_RANDOM:
        await random_choice(
            update,
            context
        )
        return

    if text == BTN_QUICK:
        await quick_choice(
            update,
            context
        )
        return

    if text == BTN_ADVANCED:
        await show_advanced(
            update,
            context
        )
        return

    if text == BTN_MORNING:
        await morning(
            update,
            context
        )
        return

    if text == BTN_EVENING:
        await evening(
            update,
            context
        )
        return

    if text == BTN_TAFSIR:
        await show_tafsir(
            update,
            context
        )
        return

    if text == BTN_DORAR:
        await show_dorar(
            update,
            context
        )
        return

    if text == BTN_CHANNEL:
        await show_channel(
            update,
            context
        )
        return

    if text == BTN_LANGUAGE:
        await show_language(
            update,
            context
        )
        return

    if text == BTN_BACK:
        await go_back(
            update,
            context
        )
        return

    if text == BTN_HOME:
        await go_home(
            update,
            context
        )
        return

    if text == BTN_HIDE:
        await hide_menu(
            update,
            context
        )
        return

    # في حال كتب المستخدم "المصحف"
    if text in [
        "📖 المصحف",
        "المصحف",
        "/quran"
    ]:
        await show_quran(
            update,
            context
        )
        return

    await update.message.reply_text(
        "اختر من القائمة الموجودة أسفل الشاشة 👇",
        reply_markup=MAIN_KEYBOARD
    )


# =========================================================
# Main
# =========================================================

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود في Railway Variables"
        )

    # تشغيل Flask في الخلفية
    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    logger.info(
        "Flask server started on port %s",
        PORT
    )

    if WEBAPP_URL:
        logger.info(
            "WEBAPP_URL = %s",
            WEBAPP_URL
        )
    else:
        logger.warning(
            "WEBAPP_URL غير موجود."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(setup_quran_menu_button)
        .build()
    )

    # الأوامر
    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "quran",
            show_quran
        )
    )

    # أزرار Inline
    application.add_handler(
        CallbackQueryHandler(
            callback_handler
        )
    )

    # الرسائل
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    logger.info(
        "Bot started successfully."
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
