import os
import random
import tempfile
import asyncio
from pathlib import Path

import requests

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# الإعدادات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

API = "https://mp3quran.net/api/v3"

RECITERS_PAGE_SIZE = 8
SURAHS_PAGE_SIZE = 10

# Telegram يسمح للبوتات بإرسال ملفات حتى 50MB
MAX_AUDIO_BYTES = 50 * 1024 * 1024


# =========================================================
# القائمة الرئيسية - تظهر أسفل المحادثة
# =========================================================

MAIN_KEYBOARD = [
    ["📖 المصحف", "🎙️ القرّاء"],
    ["📜 الروايات", "🎲 عشوائي"],
    ["⚡ اختيار سريع", "⚙️ اختيار متقدم"],
    ["🌅 أذكار الصباح", "🌙 أذكار المساء"],
    ["📕 القرآن الكريم PDF"],
    ["📚 تفسير القرآن PDF"],
    ["🌐 تغيير اللغة"],
]

HOME_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True,
    is_persistent=True,
)


# =========================================================
# التخزين المؤقت
# =========================================================

CACHE = {
    "suwar": None,
    "reciters": None,
    "riwayat": None,
}


# =========================================================
# الاتصال بـ MP3Quran
# =========================================================

def api_get(path, params=None):
    response = requests.get(
        f"{API}/{path}",
        params=params or {},
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


async def get_suwar():
    if CACHE["suwar"] is None:
        data = await asyncio.to_thread(
            api_get,
            "suwar",
            {"language": "ar"},
        )

        CACHE["suwar"] = data.get("suwar", [])

    return CACHE["suwar"]


async def get_reciters(params=None):
    if not params:
        if CACHE["reciters"] is None:
            data = await asyncio.to_thread(
                api_get,
                "reciters",
                {"language": "ar"},
            )

            CACHE["reciters"] = data.get("reciters", [])

        return CACHE["reciters"]

    data = await asyncio.to_thread(
        api_get,
        "reciters",
        {
            "language": "ar",
            **params,
        },
    )

    return data.get("reciters", [])


async def get_riwayat():
    if CACHE["riwayat"] is None:
        data = await asyncio.to_thread(
            api_get,
            "riwayat",
            {"language": "ar"},
        )

        CACHE["riwayat"] = data.get("riwayat", [])

    return CACHE["riwayat"]


# =========================================================
# الصفحة الرئيسية
# =========================================================

def home_text():
    return (
        "🕌 <b>قرآن بوت</b>\n\n"
        "اختر من القائمة الموجودة أسفل الشاشة:"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        home_text(),
        parse_mode="HTML",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# أزرار القرّاء
# =========================================================

def reciters_keyboard(reciters, page=0):

    start = page * RECITERS_PAGE_SIZE
    end = min(
        start + RECITERS_PAGE_SIZE,
        len(reciters),
    )

    rows = []

    for reciter in reciters[start:end]:

        rows.append([
            InlineKeyboardButton(
                reciter.get("name", "قارئ"),
                callback_data=f"R:{reciter.get('id')}",
            )
        ])

    navigation = []

    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "⬅️ السابق",
                callback_data=f"RP:{page - 1}",
            )
        )

    if end < len(reciters):

        navigation.append(
            InlineKeyboardButton(
                "التالي ➡️",
                callback_data=f"RP:{page + 1}",
            )
        )

    if navigation:
        rows.append(navigation)

    rows.append([
        InlineKeyboardButton(
            "🏠 القائمة الرئيسية",
            callback_data="HOME",
        )
    ])

    return InlineKeyboardMarkup(rows)


async def show_reciters(
    message,
    page=0,
    reciters=None,
):

    if reciters is None:
        reciters = await get_reciters()

    reciters = [
        r for r in reciters
        if r.get("moshaf")
    ]

    if not reciters:

        await message.reply_text(
            "تعذر تحميل قائمة القرّاء.",
            reply_markup=HOME_MARKUP,
        )

        return

    await message.reply_text(
        f"🎙️ <b>اختر القارئ</b>\n\n"
        f"الصفحة {page + 1}",
        parse_mode="HTML",
        reply_markup=reciters_keyboard(
            reciters,
            page,
        ),
    )


# =========================================================
# الروايات
# =========================================================

async def show_riwayat(message, page=0):

    riwayat = await get_riwayat()

    start = page * RECITERS_PAGE_SIZE
    end = min(
        start + RECITERS_PAGE_SIZE,
        len(riwayat),
    )

    rows = []

    for item in riwayat[start:end]:

        rows.append([
            InlineKeyboardButton(
                item.get("name", "رواية"),
                callback_data=f"W:{item.get('id')}",
            )
        ])

    navigation = []

    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "⬅️ السابق",
                callback_data=f"WP:{page - 1}",
            )
        )

    if end < len(riwayat):

        navigation.append(
            InlineKeyboardButton(
                "التالي ➡️",
                callback_data=f"WP:{page + 1}",
            )
        )

    if navigation:
        rows.append(navigation)

    rows.append([
        InlineKeyboardButton(
            "🏠 القائمة الرئيسية",
            callback_data="HOME",
        )
    ])

    await message.reply_text(
        "📜 <b>اختر الرواية</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(rows),
    )


# =========================================================
# البحث عن القارئ والمصحف
# =========================================================

def find_reciter(reciters, reciter_id):

    for reciter in reciters:

        if str(reciter.get("id")) == str(reciter_id):
            return reciter

    return None


def find_moshaf(reciter, moshaf_id=None):

    moshafs = reciter.get("moshaf") or []

    if not moshafs:
        return None

    if moshaf_id is None:
        return moshafs[0]

    for moshaf in moshafs:

        if str(moshaf.get("id")) == str(moshaf_id):
            return moshaf

    return moshafs[0]


# =========================================================
# قائمة المصاحف/الروايات عند القارئ
# =========================================================

async def show_moshafs(message, reciter):

    moshafs = reciter.get("moshaf") or []

    rows = []

    for moshaf in moshafs:

        rows.append([
            InlineKeyboardButton(
                moshaf.get(
                    "name",
                    "الرواية",
                ),
                callback_data=(
                    f"M:{reciter.get('id')}:"
                    f"{moshaf.get('id')}"
                ),
            )
        ])

    rows.append([
        InlineKeyboardButton(
            "🏠 القائمة الرئيسية",
            callback_data="HOME",
        )
    ])

    await message.reply_text(
        f"🎙️ <b>{reciter.get('name')}</b>\n\n"
        "اختر الرواية أو نوع المصحف:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(rows),
    )


# =========================================================
# قائمة السور
# =========================================================

async def show_surahs(
    message,
    reciter,
    moshaf,
    page=0,
):

    suwar = await get_suwar()

    allowed = str(
        moshaf.get("surah_list", "")
    )

    if allowed:

        allowed_ids = {
            int(x)
            for x in allowed.split(",")
            if x.strip().isdigit()
        }

        suwar = [
            s
            for s in suwar
            if int(s.get("id", 0)) in allowed_ids
        ]

    start = page * SURAHS_PAGE_SIZE

    end = min(
        start + SURAHS_PAGE_SIZE,
        len(suwar),
    )

    rows = []

    for surah in suwar[start:end]:

        rows.append([
            InlineKeyboardButton(
                f"{surah.get('id')}. "
                f"{surah.get('name', '').strip()}",
                callback_data=f"S:{surah.get('id')}",
            )
        ])

    navigation = []

    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "⬅️ السابق",
                callback_data=f"SP:{page - 1}",
            )
        )

    if end < len(suwar):

        navigation.append(
            InlineKeyboardButton(
                "التالي ➡️",
                callback_data=f"SP:{page + 1}",
            )
        )

    if navigation:
        rows.append(navigation)

    rows.append([
        InlineKeyboardButton(
            "🔙 اختيار قارئ آخر",
            callback_data="RECITERS:0",
        )
    ])

    rows.append([
        InlineKeyboardButton(
            "🏠 القائمة الرئيسية",
            callback_data="HOME",
        )
    ])

    await message.reply_text(
        f"📖 <b>{reciter.get('name')}</b>\n\n"
        f"اختر السورة:\n"
        f"الصفحة {page + 1}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(rows),
    )


# =========================================================
# تحميل الصوت
# =========================================================

async def download_audio(
    url,
    destination,
):

    def download():

        with requests.get(
            url,
            stream=True,
            timeout=(20, 120),
            headers={
                "User-Agent": "QuranBot/1.0"
            },
        ) as response:

            response.raise_for_status()

            content_length = response.headers.get(
                "content-length"
            )

            if (
                content_length
                and int(content_length)
                > MAX_AUDIO_BYTES
            ):
                raise ValueError(
                    "FILE_TOO_LARGE"
                )

            size = 0

            with open(
                destination,
                "wb",
            ) as file:

                for chunk in response.iter_content(
                    chunk_size=256 * 1024
                ):

                    if not chunk:
                        continue

                    size += len(chunk)

                    if size > MAX_AUDIO_BYTES:

                        raise ValueError(
                            "FILE_TOO_LARGE"
                        )

                    file.write(chunk)

            return size

    return await asyncio.to_thread(download)


# =========================================================
# إرسال السورة
# =========================================================

async def send_surah_audio(
    update,
    context,
    surah_id,
):

    chat = update.effective_chat

    reciter = context.user_data.get(
        "reciter"
    )

    moshaf = context.user_data.get(
        "moshaf"
    )

    if not reciter or not moshaf:

        await chat.send_message(
            "اختر القارئ أولًا.",
            reply_markup=HOME_MARKUP,
        )

        return

    suwar = await get_suwar()

    surah = next(
        (
            s
            for s in suwar
            if int(s.get("id", 0))
            == int(surah_id)
        ),
        None,
    )

    if not surah:

        await chat.send_message(
            "لم أجد هذه السورة."
        )

        return

    server = str(
        moshaf.get("server", "")
    ).rstrip("/")

    if not server:

        await chat.send_message(
            "لا يوجد رابط صوتي لهذا القارئ."
        )

        return

    audio_url = (
        f"{server}/"
        f"{int(surah_id):03d}.mp3"
    )

    status = await chat.send_message(
        f"⏳ جاري تجهيز "
        f"<b>{surah.get('name', '').strip()}</b>...",
        parse_mode="HTML",
    )

    temp_path = None

    try:

        fd, temp_path = tempfile.mkstemp(
            suffix=".mp3"
        )

        os.close(fd)

        # تنزيل الصوت إلى Railway أولًا
        await download_audio(
            audio_url,
            temp_path,
        )

        await status.edit_text(
            f"📤 جاري إرسال "
            f"<b>{surah.get('name', '').strip()}</b>...",
            parse_mode="HTML",
        )

        # رفع الملف نفسه إلى Telegram
        with open(
            temp_path,
            "rb",
        ) as audio_file:

            await chat.send_audio(
                audio=audio_file,
                filename=(
                    f"{int(surah_id):03d}.mp3"
                ),
                title=surah.get(
                    "name",
                    "سورة",
                ).strip(),
                performer=reciter.get(
                    "name",
                    "قارئ",
                ),
                caption=(
                    f"📖 "
                    f"{surah.get('name', '').strip()}\n"
                    f"🎙️ "
                    f"{reciter.get('name', '')}"
                ),
                read_timeout=120,
                write_timeout=120,
                connect_timeout=30,
            )

        await status.delete()

    except ValueError as error:

        if str(error) == "FILE_TOO_LARGE":

            await status.edit_text(
                "⚠️ ملف هذه السورة أكبر من "
                "50 MB، وTelegram لا يسمح "
                "للبوت بإرسالها بهذا الحجم."
            )

        else:

            await status.edit_text(
                "❌ تعذر إرسال الصوت."
            )

    except Exception as error:

        print(
            "Audio error:",
            type(error).__name__,
            str(error),
        )

        await status.edit_text(
            "❌ تعذر إرسال الملف الصوتي.\n"
            "جرّب قارئًا أو سورة أخرى."
        )

    finally:

        if temp_path:

            try:
                Path(temp_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass


# =========================================================
# العشوائي
# =========================================================

async def random_audio(
    update,
    context,
):

    reciters = [
        r
        for r in await get_reciters()
        if r.get("moshaf")
    ]

    if not reciters:

        await update.message.reply_text(
            "تعذر تحميل القرّاء."
        )

        return

    choices = []

    for reciter in reciters:

        for moshaf in reciter.get(
            "moshaf",
            [],
        ):

            if int(
                moshaf.get(
                    "surah_total",
                    0,
                )
                or 0
            ) >= 114:

                choices.append(
                    (
                        reciter,
                        moshaf,
                    )
                )

    if not choices:

        choices = [
            (
                r,
                r["moshaf"][0],
            )
            for r in reciters
            if r.get("moshaf")
        ]

    reciter, moshaf = random.choice(
        choices
    )

    allowed = str(
        moshaf.get(
            "surah_list",
            "",
        )
    )

    ids = [
        int(x)
        for x in allowed.split(",")
        if x.strip().isdigit()
    ]

    if not ids:
        ids = list(range(1, 115))

    surah_id = random.choice(ids)

    context.user_data["reciter"] = reciter
    context.user_data["moshaf"] = moshaf

    await send_surah_audio(
        update,
        context,
        surah_id,
    )


# =========================================================
# الأذكار
# =========================================================

MORNING = """🌅 أذكار الصباح

• أصبحنا وأصبح الملك لله، والحمد لله.
• اللهم بك أصبحنا وبك أمسينا وبك نحيا وبك نموت وإليك النشور.
• رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.
• حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم.
• سبحان الله وبحمده.
"""


EVENING = """🌙 أذكار المساء

• أمسينا وأمسى الملك لله، والحمد لله.
• اللهم بك أمسينا وبك أصبحنا وبك نحيا وبك نموت وإليك المصير.
• رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.
• حسبي الله لا إله إلا هو، عليه توكلت وهو رب العرش العظيم.
• سبحان الله وبحمده.
"""


# =========================================================
# أزرار القائمة السفلية
# =========================================================

async def text_router(
    update,
    context,
):

    text = (
        update.message.text
        or ""
    ).strip()

    if text in (
        "📖 المصحف",
        "🎙️ القرّاء",
        "⚙️ اختيار متقدم",
    ):

        await show_reciters(
            update.message,
            0,
        )

        return

    if text == "📜 الروايات":

        await show_riwayat(
            update.message,
            0,
        )

        return

    if text in (
        "🎲 عشوائي",
        "⚡ اختيار سريع",
    ):

        await random_audio(
            update,
            context,
        )

        return

    if text == "🌅 أذكار الصباح":

        await update.message.reply_text(
            MORNING,
            reply_markup=HOME_MARKUP,
        )

        return

    if text == "🌙 أذكار المساء":

        await update.message.reply_text(
            EVENING,
            reply_markup=HOME_MARKUP,
        )

        return

    if text == "📕 القرآن الكريم PDF":

        url = os.getenv(
            "QURAN_PDF_URL",
            "",
        ).strip()

        if url:

            await update.message.reply_text(
                f"📕 القرآن الكريم PDF\n{url}",
                reply_markup=HOME_MARKUP,
            )

        else:

            await update.message.reply_text(
                "📕 رابط PDF غير مضبوط حاليًا.",
                reply_markup=HOME_MARKUP,
            )

        return

    if text == "📚 تفسير القرآن PDF":

        url = os.getenv(
            "TAFSIR_PDF_URL",
            "",
        ).strip()

        if url:

            await update.message.reply_text(
                f"📚 تفسير القرآن PDF\n{url}",
                reply_markup=HOME_MARKUP,
            )

        else:

            await update.message.reply_text(
                "📚 رابط تفسير PDF غير مضبوط حاليًا.",
                reply_markup=HOME_MARKUP,
            )

        return

    if text == "🌐 تغيير اللغة":

        await update.message.reply_text(
            "🌐 اللغة الحالية: العربية\n\n"
            "دعم اللغات الأخرى سنضيفه لاحقًا.",
            reply_markup=HOME_MARKUP,
        )

        return


# =========================================================
# الأزرار الداخلية
# =========================================================

async def callback_handler(
    update,
    context,
):

    query = update.callback_query

    await query.answer()

    data = query.data

    # الرئيسية
    if data == "HOME":

        await query.message.reply_text(
            home_text(),
            parse_mode="HTML",
            reply_markup=HOME_MARKUP,
        )

        return

    # صفحات القراء
    if data.startswith("RP:"):

        page = int(
            data.split(":")[1]
        )

        await show_reciters(
            query.message,
            page,
        )

        return

    if data.startswith("RECITERS:"):

        page = int(
            data.split(":")[1]
        )

        await show_reciters(
            query.message,
            page,
        )

        return

    # اختيار قارئ
    if data.startswith("R:"):

        reciter_id = data.split(":")[1]

        reciters = await get_reciters()

        reciter = find_reciter(
            reciters,
            reciter_id,
        )

        if not reciter:

            await query.message.reply_text(
                "القارئ غير موجود."
            )

            return

        moshafs = (
            reciter.get("moshaf")
            or []
        )

        if len(moshafs) == 1:

            moshaf = moshafs[0]

            context.user_data[
                "reciter"
            ] = reciter

            context.user_data[
                "moshaf"
            ] = moshaf

            await show_surahs(
                query.message,
                reciter,
                moshaf,
                0,
            )

        else:

            await show_moshafs(
                query.message,
                reciter,
            )

        return

    # اختيار الرواية/المصحف
    if data.startswith("M:"):

        _, reciter_id, moshaf_id = (
            data.split(":")
        )

        reciters = await get_reciters()

        reciter = find_reciter(
            reciters,
            reciter_id,
        )

        if not reciter:

            await query.message.reply_text(
                "القارئ غير موجود."
            )

            return

        moshaf = find_moshaf(
            reciter,
            moshaf_id,
        )

        context.user_data[
            "reciter"
        ] = reciter

        context.user_data[
            "moshaf"
        ] = moshaf

        await show_surahs(
            query.message,
            reciter,
            moshaf,
            0,
        )

        return

    # صفحات السور
    if data.startswith("SP:"):

        page = int(
            data.split(":")[1]
        )

        reciter = context.user_data.get(
            "reciter"
        )

        moshaf = context.user_data.get(
            "moshaf"
        )

        if reciter and moshaf:

            await show_surahs(
                query.message,
                reciter,
                moshaf,
                page,
            )

        return

    # اختيار سورة
    if data.startswith("S:"):

        surah_id = int(
            data.split(":")[1]
        )

        await send_surah_audio(
            update,
            context,
            surah_id,
        )

        return

    # صفحات الروايات
    if data.startswith("WP:"):

        page = int(
            data.split(":")[1]
        )

        await show_riwayat(
            query.message,
            page,
        )

        return

    # اختيار رواية
    if data.startswith("W:"):

        rewaya_id = data.split(":")[1]

        reciters = await get_reciters(
            {
                "rewaya": rewaya_id
            }
        )

        await show_reciters(
            query.message,
            0,
            reciters,
        )

        return


# =========================================================
# الأخطاء
# =========================================================

async def error_handler(
    update,
    context,
):

    print(
        "Update error:",
        context.error,
    )


# =========================================================
# تشغيل البوت
# =========================================================

def main():

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN غير موجود في Railway Variables"
        )

    application = (
        Application
        .builder()
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
        CallbackQueryHandler(
            callback_handler,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT
            & ~filters.COMMAND,
            text_router,
        )
    )

    application.add_error_handler(
        error_handler
    )

    print(
        "Quran Bot is running..."
    )

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
