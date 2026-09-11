import os
import random
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================================================
# إعدادات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# روابط اختيارية للملفات التي سنضعها لاحقًا في Railway
QURAN_PDF_URL = os.getenv("QURAN_PDF_URL", "")
TAFSIR_PDF_URL = os.getenv("TAFSIR_PDF_URL", "")

API = "https://www.mp3quran.net/api/v3"

PAGE_SIZE = 12

# =========================================================
# أسماء السور
# =========================================================

SURAHS = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة",
    "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
    "النحل", "الإسراء", "الكهف", "مريم", "طه",
    "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان",
    "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر",
    "يس", "الصافات", "ص", "الزمر", "غافر",
    "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
    "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
    "الذاريات", "الطور", "النجم", "القمر", "الرحمن",
    "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق",
    "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة",
    "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
    "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج",
    "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين",
    "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
    "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
    "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
    "المسد", "الإخلاص", "الفلق", "الناس"
]

# =========================================================
# جلب القراء من MP3Quran
# =========================================================

def get_reciters():
    try:
        response = requests.get(
            f"{API}/reciters?language=ar",
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data.get("reciters", [])

    except Exception as error:
        print("Reciters error:", error)
        return []


# =========================================================
# القائمة الرئيسية
# =========================================================

def main_menu():

    keyboard = [
        [
            InlineKeyboardButton(
                "📖 المصحف",
                callback_data="quran"
            ),
            InlineKeyboardButton(
                "🎙️ القرّاء",
                callback_data="reciters:0"
            )
        ],
        [
            InlineKeyboardButton(
                "📜 الروايات",
                callback_data="riwayat"
            )
        ],
        [
            InlineKeyboardButton(
                "🎲 عشوائي",
                callback_data="random"
            ),
            InlineKeyboardButton(
                "⚡ اختيار سريع",
                callback_data="quick"
            )
        ],
        [
            InlineKeyboardButton(
                "⚙️ اختيار متقدم",
                callback_data="advanced"
            )
        ],
        [
            InlineKeyboardButton(
                "🌅 أذكار الصباح",
                callback_data="morning"
            ),
            InlineKeyboardButton(
                "🌙 أذكار المساء",
                callback_data="evening"
            )
        ],
        [
            InlineKeyboardButton(
                "📕 القرآن الكريم PDF",
                callback_data="quran_pdf"
            )
        ],
        [
            InlineKeyboardButton(
                "📚 تفسير القرآن PDF",
                callback_data="tafsir_pdf"
            )
        ],
        [
            InlineKeyboardButton(
                "🌐 تغيير اللغة",
                callback_data="language"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🕌 قرآن بوت\n\n"
        "مرحبًا بك في بوت القرآن الكريم.\n\n"
        "اختر من القائمة:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# قائمة القراء
# =========================================================

def reciters_menu(page=0):

    reciters = get_reciters()

    if not reciters:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🏠 الرئيسية",
                    callback_data="home"
                )
            ]
        ])

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    current = reciters[start:end]

    buttons = []

    for i in range(0, len(current), 2):

        row = []

        for reciter in current[i:i + 2]:

            name = reciter.get("name", "قارئ")
            reciter_id = reciter.get("id")

            row.append(
                InlineKeyboardButton(
                    f"🎙️ {name}",
                    callback_data=f"reciter:{reciter_id}"
                )
            )

        buttons.append(row)

    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                "⬅️ السابق",
                callback_data=f"reciters:{page - 1}"
            )
        )

    if end < len(reciters):
        navigation.append(
            InlineKeyboardButton(
                "التالي ➡️",
                callback_data=f"reciters:{page + 1}"
            )
        )

    if navigation:
        buttons.append(navigation)

    buttons.append([
        InlineKeyboardButton(
            "🏠 الرئيسية",
            callback_data="home"
        )
    ])

    return InlineKeyboardMarkup(buttons)


# =========================================================
# روايات القارئ
# =========================================================

def get_reciter(reciter_id):

    try:

        response = requests.get(
            f"{API}/reciters",
            params={
                "language": "ar",
                "reciter": reciter_id
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        reciters = data.get("reciters", [])

        if reciters:
            return reciters[0]

    except Exception as error:
        print("Reciter error:", error)

    return None


def riwayat_menu(reciter_id):

    reciter = get_reciter(reciter_id)

    if not reciter:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ رجوع",
                    callback_data="reciters:0"
                )
            ]
        ])

    buttons = []

    for moshaf in reciter.get("moshaf", []):

        moshaf_id = moshaf.get("id")

        name = moshaf.get(
            "name",
            "رواية"
        )

        buttons.append([
            InlineKeyboardButton(
                f"📜 {name}",
                callback_data=f"moshaf:{reciter_id}:{moshaf_id}"
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "⬅️ القرّاء",
            callback_data="reciters:0"
        )
    ])

    return InlineKeyboardMarkup(buttons)


# =========================================================
# السور
# =========================================================

def surahs_menu(reciter_id, moshaf_id, page=0):

    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, 114)

    buttons = []

    for i in range(start, end, 2):

        row = []

        for number in range(i + 1, min(i + 3, end + 1)):

            row.append(
                InlineKeyboardButton(
                    f"📖 {number}. {SURAHS[number - 1]}",
                    callback_data=(
                        f"surah:{reciter_id}:"
                        f"{moshaf_id}:{number}"
                    )
                )
            )

        buttons.append(row)

    navigation = []

    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "⬅️ السابق",
                callback_data=(
                    f"surahs:{reciter_id}:"
                    f"{moshaf_id}:{page - 1}"
                )
            )
        )

    if end < 114:

        navigation.append(
            InlineKeyboardButton(
                "التالي ➡️",
                callback_data=(
                    f"surahs:{reciter_id}:"
                    f"{moshaf_id}:{page + 1}"
                )
            )
        )

    if navigation:
        buttons.append(navigation)

    buttons.append([
        InlineKeyboardButton(
            "⬅️ الرواية",
            callback_data=f"reciter:{reciter_id}"
        )
    ])

    return InlineKeyboardMarkup(buttons)


# =========================================================
# الحصول على رابط التلاوة
# =========================================================

def get_audio_url(reciter_id, moshaf_id, surah_number):

    reciter = get_reciter(reciter_id)

    if not reciter:
        return None, None

    for moshaf in reciter.get("moshaf", []):

        if str(moshaf.get("id")) == str(moshaf_id):

            server = moshaf.get("server")

            if not server:
                return None, None

            if not server.endswith("/"):
                server += "/"

            filename = f"{surah_number:03d}.mp3"

            url = server + filename

            return url, moshaf.get("name", "الرواية")

    return None, None


# =========================================================
# إرسال التلاوة
# =========================================================

async def send_surah(
    query,
    reciter_id,
    moshaf_id,
    surah_number
):

    reciter = get_reciter(reciter_id)

    if not reciter:

        await query.message.reply_text(
            "تعذر العثور على القارئ."
        )

        return

    reciter_name = reciter.get(
        "name",
        "القارئ"
    )

    url, riwaya = get_audio_url(
        reciter_id,
        moshaf_id,
        surah_number
    )

    if not url:

        await query.message.reply_text(
            "عذرًا، هذه السورة غير متوفرة لهذه الرواية."
        )

        return

    surah_name = SURAHS[surah_number - 1]

    await query.message.reply_text(
        f"⏳ جاري تجهيز التلاوة...\n\n"
        f"📖 سورة {surah_name}\n"
        f"🎙️ {reciter_name}\n"
        f"📜 {riwaya}"
    )

    try:

        await query.message.reply_audio(
            audio=url,
            title=f"سورة {surah_name}",
            performer=reciter_name,
            caption=(
                f"📖 سورة {surah_name}\n"
                f"🎙️ {reciter_name}\n"
                f"📜 {riwaya}"
            )
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "📖 سورة أخرى",
                    callback_data=(
                        f"surahs:{reciter_id}:"
                        f"{moshaf_id}:0"
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    "🏠 الرئيسية",
                    callback_data="home"
                )
            ]
        ]

        await query.message.reply_text(
            "تم إرسال التلاوة.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as error:

        print("Audio error:", error)

        await query.message.reply_text(
            "تعذر إرسال التلاوة حاليًا."
        )


# =========================================================
# العشوائي
# =========================================================

async def random_surah(query):

    reciters = get_reciters()

    if not reciters:

        await query.message.reply_text(
            "تعذر تحميل القراء حاليًا."
        )

        return

    valid = []

    for reciter in reciters:

        for moshaf in reciter.get("moshaf", []):

            surah_list = moshaf.get(
                "surah_list",
                ""
            )

            if "18" in surah_list.split(","):

                valid.append(
                    (
                        reciter,
                        moshaf
                    )
                )

    if not valid:
        await query.message.reply_text(
            "تعذر العثور على تلاوة عشوائية."
        )
        return

    reciter, moshaf = random.choice(valid)

    available = moshaf.get(
        "surah_list",
        ""
    ).split(",")

    available = [
        int(x)
        for x in available
        if x.isdigit()
    ]

    if not available:
        return

    surah_number = random.choice(available)

    await send_surah(
        query,
        reciter.get("id"),
        moshaf.get("id"),
        surah_number
    )


# =========================================================
# الأذكار
# =========================================================

MORNING_AZKAR = """
🌅 أذكار الصباح

1. أصبحنا وأصبح الملك لله، والحمد لله.

2. اللهم بك أصبحنا وبك أمسينا، وبك نحيا وبك نموت وإليك النشور.

3. رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد صلى الله عليه وسلم نبيًا.

4. اللهم إني أسألك العفو والعافية في الدنيا والآخرة.

5. سبحان الله وبحمده.

6. لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

7. أستغفر الله وأتوب إليه.
"""


EVENING_AZKAR = """
🌙 أذكار المساء

1. أمسينا وأمسى الملك لله، والحمد لله.

2. اللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير.

3. رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد صلى الله عليه وسلم نبيًا.

4. اللهم إني أسألك العفو والعافية في الدنيا والآخرة.

5. سبحان الله وبحمده.

6. لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

7. أستغفر الله وأتوب إليه.
"""


# =========================================================
# الأزرار
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    # الرئيسية
    if data == "home":

        await query.edit_message_text(
            "🕌 قرآن بوت\n\n"
            "اختر من القائمة:",
            reply_markup=main_menu()
        )

    # المصحف
    elif data == "quran":

        await query.edit_message_text(
            "📖 اختر طريقة الاستماع:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎙️ اختيار القارئ",
                        callback_data="reciters:0"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⚡ اختيار سريع",
                        callback_data="quick"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🎲 عشوائي",
                        callback_data="random"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 الرئيسية",
                        callback_data="home"
                    )
                ]
            ])
        )

    # القراء
    elif data.startswith("reciters:"):

        page = int(data.split(":")[1])

        await query.edit_message_text(
            "🎙️ اختر القارئ:",
            reply_markup=reciters_menu(page)
        )

    # قارئ
    elif data.startswith("reciter:"):

        reciter_id = data.split(":")[1]

        reciter = get_reciter(reciter_id)

        name = (
            reciter.get("name", "القارئ")
            if reciter
            else "القارئ"
        )

        await query.edit_message_text(
            f"🎙️ {name}\n\n"
            "📜 اختر الرواية:",
            reply_markup=riwayat_menu(reciter_id)
        )

    # الرواية
    elif data.startswith("moshaf:"):

        parts = data.split(":")

        reciter_id = parts[1]
        moshaf_id = parts[2]

        await query.edit_message_text(
            "📖 اختر السورة:",
            reply_markup=surahs_menu(
                reciter_id,
                moshaf_id,
                0
            )
        )

    # السور
    elif data.startswith("surahs:"):

        parts = data.split(":")

        reciter_id = parts[1]
        moshaf_id = parts[2]
        page = int(parts[3])

        await query.edit_message_text(
            "📖 اختر السورة:",
            reply_markup=surahs_menu(
                reciter_id,
                moshaf_id,
                page
            )
        )

    # سورة
    elif data.startswith("surah:"):

        parts = data.split(":")

        reciter_id = parts[1]
        moshaf_id = parts[2]
        surah_number = int(parts[3])

        await send_surah(
            query,
            reciter_id,
            moshaf_id,
            surah_number
        )

    # عشوائي
    elif data == "random":

        await random_surah(query)

    # اختيار سريع
    elif data == "quick":

        await query.edit_message_text(
            "⚡ اختيار سريع\n\n"
            "اختر القارئ:",
            reply_markup=reciters_menu(0)
        )

    # اختيار متقدم
    elif data == "advanced":

        await query.edit_message_text(
            "⚙️ الاختيار المتقدم\n\n"
            "اختر القارئ ثم الرواية ثم السورة.",
            reply_markup=reciters_menu(0)
        )

    # الروايات
    elif data == "riwayat":

        await query.edit_message_text(
            "📜 الروايات\n\n"
            "اختر قارئًا لعرض الروايات المتوفرة لديه:",
            reply_markup=reciters_menu(0)
        )

    # أذكار الصباح
    elif data == "morning":

        await query.edit_message_text(
            MORNING_AZKAR,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🌙 أذكار المساء",
                        callback_data="evening"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 الرئيسية",
                        callback_data="home"
                    )
                ]
            ])
        )

    # أذكار المساء
    elif data == "evening":

        await query.edit_message_text(
            EVENING_AZKAR,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🌅 أذكار الصباح",
                        callback_data="morning"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 الرئيسية",
                        callback_data="home"
                    )
                ]
            ])
        )

    # القرآن PDF
    elif data == "quran_pdf":

        if QURAN_PDF_URL:

            await query.message.reply_document(
                document=QURAN_PDF_URL,
                caption="📕 القرآن الكريم"
            )

        else:

            await query.message.reply_text(
                "📕 ملف القرآن الكريم لم تتم إضافته بعد."
            )

    # التفسير PDF
    elif data == "tafsir_pdf":

        if TAFSIR_PDF_URL:

            await query.message.reply_document(
                document=TAFSIR_PDF_URL,
                caption="📚 تفسير القرآن الكريم"
            )

        else:

            await query.message.reply_text(
                "📚 ملف التفسير لم تتم إضافته بعد."
            )

    # اللغة
    elif data == "language":

        await query.edit_message_text(
            "🌐 اختر اللغة:",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🇸🇦 العربية",
                        callback_data="home"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🇬🇧 English",
                        callback_data="english"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🏠 الرئيسية",
                        callback_data="home"
                    )
                ]
            ])
        )

    elif data == "english":

        await query.edit_message_text(
            "🕌 Quran Bot\n\n"
            "English interface will be added.",
            reply_markup=main_menu()
        )


# =========================================================
# تشغيل البوت
# =========================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود في Railway Variables"
        )

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    print("🕌 Quran Bot is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
