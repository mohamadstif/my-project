import os
import random
import tempfile
import asyncio
from pathlib import Path

import requests
from telegram import (
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# إعدادات البوت
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

API = "https://mp3quran.net/api/v3"

PAGE_SIZE = 10
SURAH_PAGE_SIZE = 10
MAX_AUDIO_BYTES = 50 * 1024 * 1024

BASE_DIR = Path(__file__).resolve().parent
FILES_DIR = BASE_DIR / "files"

QURAN_PDF = FILES_DIR / "quran.pdf"
TAFSIR_PDF = FILES_DIR / "tafsir.pdf"
MORNING_AUDIO = FILES_DIR / "adhkar_morning.mp3"
EVENING_AUDIO = FILES_DIR / "adhkar_evening.mp3"


# =========================================================
# القائمة الرئيسية - تبقى معلقة في الأسفل
# =========================================================

MAIN_KEYBOARD = [
    ["📖 المصحف", "🎙️ القرائ"],
    ["📜 الروايات", "🎲 عشوائي"],
    ["⚡ اختيار سريع", "⚙️ اختيار متقدم"],
    ["🌅 أذكار الصباح", "🌙 أذكار المساء"],
    ["📕 القرآن الكريم PDF"],
    ["📚 تفسير القرآن PDF"],
    ["📢 قناتنا على تيليجرام"],
    ["🌐 تغيير اللغة"],
]

HOME_MARKUP = ReplyKeyboardMarkup(
    MAIN_KEYBOARD,
    resize_keyboard=True,
    is_persistent=True,
)


# =========================================================
# رسالة الترحيب
# =========================================================

WELCOME = """السلام عليكم ورحمة الله وبركاته 🌿

أهلًا وسهلًا بك في قرآن بوت 🕌

نسأل الله أن يجعل هذا البوت سببًا لنشر كتابه،
وتذكيرنا به، والدلالة على الخير.

📖 استمع إلى القرآن الكريم
🎙️ اختر القارئ الذي تحبه
📜 اختر الرواية
🌅 أذكار الصباح والمساء
📕 المصحف وتفسير القرآن

﴿وَذَكِّرْ فَإِنَّ الذِّكْرَىٰ تَنفَعُ الْمُؤْمِنِينَ﴾

🌱 انشر الخير

قال رسول الله ﷺ:
«من دل على خير فله مثل أجر فاعله»

نسأل الله أن يكتب لك أجر كل من قرأ أو استمع أو انتفع. 🤍
"""


# =========================================================
# أسماء القرّاء
# =========================================================

RECITER_NAMES = [
    "حمود عبدالحكم",
    "مختار الحاج",
    "مشاري العفاسي",
    "مصطفى اللاهوني",
    "معمر الأندونيسي",
    "مفتاح السلطني",
    "نذير المالكي",
    "وشيار حيدر اربيلي",
    "وليد النائحي",
    "ياسر الفيلكاوي",
    "ياسر المزروعي",
    "يحيى حوا",
    "يوسف الشويعي",
    "أحمد الحذيفي",
    "أحمد الحواشي",
    "أحمد السويلم",
    "أحمد الطرابلسي",
    "أحمد النفيس",
    "أحمد بن علي العجمي",
    "أحمد خضر الطرابلسي",
    "أحمد خليل شاهين",
    "أحمد ديبان",
    "أحمد سعود",
    "أحمد صابر",
    "أحمد عامر",
    "أحمد نعينع",
    "أستاذ زامري",
    "إبراهيم الأخضر",
    "إبراهيم الجرمي",
    "إبراهيم السعدان",
    "إبراهيم كشيدان",
    "إسلام صبحي",
    "الدوكالي محمد العالم",
    "العشري عمران",
    "الفاتح محمد الزبير",
    "بدر التركي",
    "بيشه وا قادر الكردي",
    "جمال الدين الزيلعي",
    "جمعان العصيمي",
    "حسين آل الشيخ",
    "خالد الجليل",
    "خالد الشريمي",
    "خالد القحطاني",
    "خالد الوهيبي",
    "خالد كريم محمدي",
    "داود حمزة",
    "رشيد إفراد",
    "رضية عبدالرحمن",
    "رقية سولونق",
    "زكريا حمامة",
    "سابينة مامات",
    "سامي الدوسري",
    "سعد المقرن",
    "سلمان العتيبي",
    "سيد أحمد هاشمي",
    "سيدين عبدالرحمن",
    "شيخ أبو بكر الشاطري",
    "صابر عبدالحكم",
    "صالح الشمراني",
    "صالح الهبدان",
    "صلاح الهاشم",
    "صلاح مصلي",
    "عادل الكلباني",
    "عبدالإله بن عون",
    "عبدالبارئ محمد",
    "عبدالله بخاري",
    "عبدالله خياط",
    "عبدالله عواد الجهني",
    "عبدالله فهمي",
    "عبدالمجيد الأركاني",
    "عبدالمحسن العبيكان",
    "عبدالمحسن القاسم",
    "عبدالودود حنيف",
    "عثمان الأنصاري",
    "علي أبو هاشم",
    "علي جابر",
    "عماد زهير حافظ",
    "عمر القزابري",
    "فارس عباد",
    "فهد الكندري",
    "لافي العوني",
    "ماجد العنزي",
    "ماهر المعيقلي",
    "محمد أبوسنينة",
    "محمد الأمين قنيوة",
    "محمد البخيت",
    "محمد عثمان خان ( من الهند )",
    "خالد عبدالكافي",
    "خالد المهنا",
    "خالد الغامدي",
    "خالد الشارخ",
    "حمد الدغريري",
    "حاتم فريد الواعر",
    "جمال شاكر عبدالله",
    "توفيق الصايغ",
    "بندر بليله",
    "القارئ ياسين",
    "العيون الكوشي",
    "الزين محمد أحمد",
    "الحسيني العزازي",
    "إدريس أبكر",
    "إبراهيم العسيري",
    "إبراهيم الدوسري",
    "إبراهيم الجبرين",
    "أكرم العلاقمي",
    "أخيل عبدالحي روا",
    "أحمد عيسى المعصراوي",
    "أحمد طالب بن حميد",
    "محمد يحيى البارقي",
    "نايف سعد الفيصل",
    "راشد الحليبة",
    "سعود الفايز",
    "تركي الرميح",
    "زيد الشنطي",
    "حمزة بوديب",
    "يوسف العيدروس",
    "طارق محمد",
    "سعد أزويت",
    "عمر هشام العربي",
    "مشاري البغلي",
    "محمود أبو الوفاء الصعيدي",
    "إبراهيم درديساوي",
    "عبدالعزيز التركي",
    "أيمن سويد",
    "عبد الرحمن الجريذي",
    "الشحات محمد أنور",
    "إسلام عثمان",
    "عبدالولي الأركاني",
    "يوسف بن نوح أحمد",
    "يوسف الدغوش",
    "ياسر سلامة",
    "ياسر القرشي",
    "ياسر الدوسري",
    "وليد الدليمي",
    "وديع اليمني",
    "هيثم الدخين",
    "هزاع البلوشي",
    "هاشم أبو دلال",
    "نعمة الحسان",
    "نبيل الرفاعي",
    "ناصر القطامي",
    "ناصر العبيد",
    "منصور السالمي",
    "معيض الحارثي",
    "مصطفى رعد العزاوي",
    "مصطفى إسماعيل",
    "مروان العكري",
    "محمود علي البنا",
    "محمود خليل الحصري",
    "محمود الرفاعي",
    "محمد عبدالكريم",
    "محمد صديق المنشاوي",
    "محمد سايد",
    "محمد رشاد الشريف",
    "محمد خليل القارئ",
    "محمد جبريل",
    "محمد المحيسني",
    "محمد الطبلاوي",
    "محمد البراك",
    "محمد الأيراوي",
    "محمد أيوب",
    "ماهر شخاشيرو",
    "مالك شيبة الحمد",
    "ماجد الزامل",
    "فواز الكعبي",
    "فهد العتيبي",
    "فؤاد الخامري",
    "عمر الدريويز",
    "علي حجاج السويسي",
    "علي الحذيفي",
    "عكاشة كميني",
    "عبدالهادي أحمد كناكري",
    "عبدالمحسن العسكر",
    "عبدالمحسن الحارثي",
    "عبدالله كامل",
    "عبدالله غيلان",
    "عبدالله عبدل",
    "عبدالله بصفر",
    "عبدالله الموسى",
    "عبدالله الكندري",
    "عبدالله البعيجان",
    "عبدالغني عبدالله",
    "عبدالعزيز الزهراني",
    "عبدالعزيز الأحمد",
    "عبدالرحمن الماجد",
    "عبدالرحمن السويد",
    "عبدالباسط عبدالصمد",
    "عبدالبارئ الثبيتي",
    "عادل ريان",
    "طارق عبدالغني دعوب",
    "صلاح بو خاطر",
    "صلاح البدير",
    "صالح الصاهود",
    "صالح آل طالب",
    "شيرزاد عبدالرحمن طاهر",
    "شعبان الصياد",
    "سيد رمضان",
    "سهل ياسين",
    "سعود الشريم",
    "سعد الغامدي",
    "سامي الحسن",
    "زكي داغستاني",
    "رمضان شكور",
    "رعد محمد الكردي",
    "رشيد بلعالية",
    "رامي الدعيس",
    "خليفة الطنيجي",
]

# إزالة الأسماء المكررة مع الحفاظ على الترتيب
RECITER_NAMES = list(dict.fromkeys(RECITER_NAMES))


# =========================================================
# أذكار الصباح والمساء - النص
# =========================================================

MORNING_ADHKAR = """🌅 أذكار الصباح

أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

اللهم بك أصبحنا وبك أمسينا، وبك نحيا وبك نموت وإليك النشور.

رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.

آية الكرسي.

سورة الإخلاص × 3
سورة الفلق × 3
سورة الناس × 3

اللهم إني أصبحت أشهدك وأشهد حملة عرشك وملائكتك وجميع خلقك أنك أنت الله لا إله إلا أنت وحدك لا شريك لك وأن محمدًا عبدك ورسولك.

اللهم إني أسألك العفو والعافية في الدنيا والآخرة.

🤲 تقبل الله منا ومنكم.
"""

EVENING_ADHKAR = """🌙 أذكار المساء

أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.

اللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير.

رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.

آية الكرسي.

سورة الإخلاص × 3
سورة الفلق × 3
سورة الناس × 3

أعوذ بكلمات الله التامات من شر ما خلق.

اللهم إني أسألك العفو والعافية في الدنيا والآخرة.

🤲 تقبل الله منا ومنكم.
"""


# =========================================================
# تخزين مؤقت
# =========================================================

cache = {
    "suwar": None,
    "reciters": None,
    "riwayat": None,
}


# =========================================================
# أدوات عامة
# =========================================================

async def api_get(endpoint, params=None):
    def request():
        r = requests.get(
            f"{API}/{endpoint}",
            params=params or {"language": "ar"},
            timeout=30,
            headers={"User-Agent": "QuranBot/1.0"},
        )
        r.raise_for_status()
        return r.json()

    return await asyncio.to_thread(request)


async def get_suwar():
    if cache["suwar"] is None:
        try:
            data = await api_get("suwar", {"language": "ar"})
            cache["suwar"] = data.get("suwar", [])
        except Exception:
            cache["suwar"] = []

    return cache["suwar"]


async def get_reciters():
    if cache["reciters"] is None:
        try:
            data = await api_get("reciters", {"language": "ar"})
            cache["reciters"] = data.get("reciters", [])
        except Exception:
            cache["reciters"] = []

    return cache["reciters"]


async def get_riwayat():
    if cache["riwayat"] is None:
        try:
            data = await api_get("riwayat", {"language": "ar"})
            cache["riwayat"] = data.get("riwayat", [])
        except Exception:
            cache["riwayat"] = []

    return cache["riwayat"]


# =========================================================
# إيجاد القارئ من API
# =========================================================

async def find_reciter(name):
    reciters = await get_reciters()

    name_lower = name.strip().lower()

    # تطابق كامل
    for reciter in reciters:
        api_name = str(reciter.get("name", "")).strip()

        if api_name.lower() == name_lower:
            return reciter

    # تطابق جزئي
    for reciter in reciters:
        api_name = str(reciter.get("name", "")).strip()

        if name_lower in api_name.lower() or api_name.lower() in name_lower:
            return reciter

    return None


# =========================================================
# تحميل وإرسال الصوت
# =========================================================

async def download_audio(url, destination):
    def download():
        response = requests.get(
            url,
            stream=True,
            timeout=60,
            headers={"User-Agent": "QuranBot/1.0"},
        )
        response.raise_for_status()

        total = 0

        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if not chunk:
                    continue

                total += len(chunk)

                if total > MAX_AUDIO_BYTES:
                    raise ValueError(
                        "حجم الملف أكبر من الحد المسموح به من Telegram."
                    )

                f.write(chunk)

        return total

    return await asyncio.to_thread(download)


async def send_audio_from_url(message, url, title, performer):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False,
        ) as temp:
            temp_path = temp.name

        await download_audio(url, temp_path)

        with open(temp_path, "rb") as audio_file:
            await message.reply_audio(
                audio=audio_file,
                filename=f"{title}.mp3",
                title=title,
                performer=performer,
            )

    except Exception as e:
        print("Audio error:", e)

        await message.reply_text(
            "⚠️ تعذر إرسال الصوت حاليًا.\n"
            "حاول مرة أخرى بعد قليل."
        )

    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass


# =========================================================
# إرسال ملف محلي
# =========================================================

async def send_document(message, path, caption):
    if not path.exists():
        await message.reply_text(
            "⚠️ هذا الملف غير موجود حاليًا.\n"
            "سيتم إضافته إلى البوت في الخطوة القادمة."
        )
        return

    try:
        with path.open("rb") as f:
            await message.reply_document(
                document=f,
                filename=path.name,
                caption=caption,
            )

    except Exception as e:
        print("Document error:", e)

        await message.reply_text(
            "⚠️ حدث خطأ أثناء إرسال الملف."
        )


# =========================================================
# لوحة القرّاء
# =========================================================

async def show_reciters(message, page=0):
    names = RECITER_NAMES

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    current = names[start:end]

    keyboard = []

    for i in range(0, len(current), 2):
        row = current[i:i + 2]
        keyboard.append(row)

    if page > 0:
        keyboard.append(["⬅️ السابق"])

    if end < len(names):
        keyboard.append(["التالي ➡️"])

    keyboard.append(["🏠 الرئيسية"])

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )

    await message.reply_text(
        f"🎙️ القرائ\n\n"
        f"اختر القارئ:\n\n"
        f"الصفحة {page + 1} من "
        f"{(len(names) + PAGE_SIZE - 1) // PAGE_SIZE}",
        reply_markup=markup,
    )


# =========================================================
# لوحة السور
# =========================================================

async def show_surahs(message, reciter_name):
    suwar = await get_suwar()

    if not suwar:
        await message.reply_text(
            "⚠️ تعذر تحميل قائمة السور حاليًا."
        )
        return

    context = message._bot  # لا نستخدمه فعليًا

    keyboard = []

    for i in range(0, min(len(suwar), 20), 2):
        row = []

        for surah in suwar[i:i + 2]:
            number = surah.get("id")
            name = surah.get("name", "")

            row.append(f"{number} - {name}")

        keyboard.append(row)

    keyboard.append(["🏠 الرئيسية"])

    markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )

    await message.reply_text(
        f"🎙️ القارئ: {reciter_name}\n\n"
        "📖 اختر السورة:",
        reply_markup=markup,
    )


# =========================================================
# اختيار قارئ
# =========================================================

async def handle_reciter_choice(message, name):
    reciter = await find_reciter(name)

    if not reciter:
        await message.reply_text(
            "⚠️ لم أجد هذا القارئ في المصدر الصوتي حاليًا.\n"
            "اختر قارئًا آخر من القائمة."
        )
        return

    moshafs = reciter.get("moshaf", [])

    if not moshafs:
        await message.reply_text(
            "⚠️ لا توجد رواية صوتية متاحة لهذا القارئ حاليًا."
        )
        return

    # حفظ اختيار المستخدم
    # نضعه على كائن chat_data
    # ويتم استخدام أول مصحف افتراضيًا
    selected = moshafs[0]

    message.chat_data = getattr(message, "chat_data", {})

    await message.reply_text(
        f"🎙️ القارئ: {reciter.get('name', name)}\n\n"
        f"📜 الرواية: {selected.get('name', 'غير محددة')}\n\n"
        "اختر السورة من القائمة:",
    )

    # إرسال أول 20 سورة كأزرار
    suwar = await get_suwar()

    keyboard = []

    for i in range(0, min(20, len(suwar)), 2):
        row = []

        for surah in suwar[i:i + 2]:
            row.append(
                f"{surah.get('id')} - {surah.get('name')}"
            )

        keyboard.append(row)

    keyboard.append(["🏠 الرئيسية"])

    await message.reply_text(
        "📖 السور:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            is_persistent=True,
        ),
    )

    # حفظ بيانات القارئ في user_data
    return reciter, selected


# =========================================================
# استخراج رابط السورة
# =========================================================

def get_surah_url(moshaf, surah_id):
    server = str(moshaf.get("server", "")).strip()

    if not server:
        return None

    if not server.endswith("/"):
        server += "/"

    return f"{server}{int(surah_id):03d}.mp3"


# =========================================================
# إرسال سورة
# =========================================================

async def send_surah(update, context, surah_id):
    message = update.message

    reciter = context.user_data.get("reciter")
    moshaf = context.user_data.get("moshaf")

    if not reciter or not moshaf:
        await message.reply_text(
            "⚠️ اختر القارئ أولًا من قسم 🎙️ القرائ."
        )
        return

    url = get_surah_url(moshaf, surah_id)

    if not url:
        await message.reply_text(
            "⚠️ لم أستطع الحصول على رابط الصوت."
        )
        return

    suwar = await get_suwar()

    surah_name = str(surah_id)

    for surah in suwar:
        if int(surah.get("id", 0)) == int(surah_id):
            surah_name = surah.get("name", surah_name)
            break

    await message.reply_text(
        f"⏳ جاري تجهيز سورة {surah_name}...\n"
        f"🎙️ {reciter.get('name', '')}"
    )

    await send_audio_from_url(
        message,
        url,
        f"{surah_name} - {reciter.get('name', '')}",
        reciter.get("name", ""),
    )


# =========================================================
# العشوائي
# =========================================================

async def random_surah(update, context):
    message = update.message

    reciters = await get_reciters()
    suwar = await get_suwar()

    if not reciters or not suwar:
        await message.reply_text(
            "⚠️ تعذر تحميل البيانات حاليًا."
        )
        return

    reciter = random.choice(reciters)

    moshafs = reciter.get("moshaf", [])

    if not moshafs:
        await message.reply_text(
            "⚠️ لم أجد ملفًا صوتيًا لهذا القارئ."
        )
        return

    moshaf = random.choice(moshafs)
    surah = random.choice(suwar)

    url = get_surah_url(
        moshaf,
        surah.get("id"),
    )

    if not url:
        await message.reply_text(
            "⚠️ تعذر الحصول على الصوت."
        )
        return

    await message.reply_text(
        "🎲 اخترت لك سورة عشوائية:\n\n"
        f"📖 {surah.get('name')}\n"
        f"🎙️ {reciter.get('name')}\n"
        f"📜 {moshaf.get('name', '')}\n\n"
        "⏳ جاري تجهيز الصوت..."
    )

    await send_audio_from_url(
        message,
        url,
        f"{surah.get('name')} - {reciter.get('name')}",
        reciter.get("name", ""),
    )


# =========================================================
# الأذكار
# =========================================================

async def send_morning(message):
    await message.reply_text(
        MORNING_ADHKAR,
        reply_markup=HOME_MARKUP,
    )

    if MORNING_AUDIO.exists():
        try:
            with MORNING_AUDIO.open("rb") as f:
                await message.reply_audio(
                    audio=f,
                    filename="adhkar_morning.mp3",
                    title="أذكار الصباح",
                    performer="قرآن بوت",
                )
        except Exception as e:
            print("Morning audio error:", e)

    else:
        await message.reply_text(
            "🎧 ملف صوت أذكار الصباح سيتم إضافته لاحقًا.",
            reply_markup=HOME_MARKUP,
        )


async def send_evening(message):
    await message.reply_text(
        EVENING_ADHKAR,
        reply_markup=HOME_MARKUP,
    )

    if EVENING_AUDIO.exists():
        try:
            with EVENING_AUDIO.open("rb") as f:
                await message.reply_audio(
                    audio=f,
                    filename="adhkar_evening.mp3",
                    title="أذكار المساء",
                    performer="قرآن بوت",
                )
        except Exception as e:
            print("Evening audio error:", e)

    else:
        await message.reply_text(
            "🎧 ملف صوت أذكار المساء سيتم إضافته لاحقًا.",
            reply_markup=HOME_MARKUP,
        )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        WELCOME,
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# المصحف
# =========================================================

async def show_mushaf(message):
    await message.reply_text(
        "📖 المصحف\n\n"
        "اختر من القائمة السفلية ما تريد.",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# الروايات
# =========================================================

async def show_riwayat(message):
    riwayat = await get_riwayat()

    if not riwayat:
        await message.reply_text(
            "⚠️ تعذر تحميل الروايات حاليًا.",
            reply_markup=HOME_MARKUP,
        )
        return

    keyboard = []

    names = []

    for item in riwayat:
        name = item.get("name")

        if name and name not in names:
            names.append(name)

    for i in range(0, len(names), 2):
        keyboard.append(names[i:i + 2])

    keyboard.append(["🏠 الرئيسية"])

    await message.reply_text(
        "📜 الروايات\n\nاختر الرواية:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            is_persistent=True,
        ),
    )


# =========================================================
# اختيار سريع
# =========================================================

async def quick_select(message, context):
    reciters = await get_reciters()

    if not reciters:
        await message.reply_text(
            "⚠️ تعذر تحميل القرّاء.",
            reply_markup=HOME_MARKUP,
        )
        return

    # أشهر القراء الموجودين في القائمة
    preferred = [
        "مشاري العفاسي",
        "ماهر المعيقلي",
        "عبدالباسط عبدالصمد",
        "محمود خليل الحصري",
        "محمد صديق المنشاوي",
        "ياسر الدوسري",
        "سعد الغامدي",
        "فارس عباد",
        "عبدالله عواد الجهني",
        "أحمد بن علي العجمي",
    ]

    available = []

    for wanted in preferred:
        found = await find_reciter(wanted)

        if found and found not in available:
            available.append(found)

    keyboard = []

    for i in range(0, len(available), 2):
        keyboard.append([
            r.get("name", "")
            for r in available[i:i + 2]
        ])

    keyboard.append(["🏠 الرئيسية"])

    await message.reply_text(
        "⚡ اختيار سريع\n\n"
        "اختر القارئ:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            is_persistent=True,
        ),
    )


# =========================================================
# اختيار متقدم
# =========================================================

async def advanced_select(message):
    await message.reply_text(
        "⚙️ اختيار متقدم\n\n"
        "اختر القارئ أولًا من قائمة 🎙️ القرائ، "
        "ثم اختر الرواية والسورة.",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# PDF القرآن
# =========================================================

async def send_quran_pdf(message):
    await send_document(
        message,
        QURAN_PDF,
        "📕 القرآن الكريم\n\nنسأل الله أن يجعله نورًا لنا ولكم."
    )


# =========================================================
# PDF التفسير
# =========================================================

async def send_tafsir_pdf(message):
    await send_document(
        message,
        TAFSIR_PDF,
        "📚 تفسير القرآن الكريم\n\nبارك الله فيكم."
    )


# =========================================================
# قناة تيليجرام
# =========================================================

async def channel(message):
    await message.reply_text(
        "📢 قناتنا على تيليجرام\n\n"
        "اضغط هنا للانتقال إلى القناة:\n"
        "https://t.me/x7oly",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# اللغة
# =========================================================

async def language(message):
    await message.reply_text(
        "🌐 تغيير اللغة\n\n"
        "🇸🇦 العربية\n\n"
        "اللغة العربية هي اللغة الحالية.\n"
        "سنضيف اللغات الأخرى لاحقًا.",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# معالجة الرسائل والأزرار
# =========================================================

async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if not message or not message.text:
        return

    text = message.text.strip()

    # الرئيسية
    if text in ["🏠 الرئيسية", "🕌 قرآن بوت"]:
        context.user_data.clear()

        await message.reply_text(
            WELCOME,
            reply_markup=HOME_MARKUP,
        )
        return

    # القائمة الرئيسية
    if text == "📖 المصحف":
        await show_mushaf(message)
        return

    if text == "🎙️ القرائ":
        await show_reciters(message, 0)
        return

    if text == "📜 الروايات":
        await show_riwayat(message)
        return

    if text == "🎲 عشوائي":
        await random_surah(update, context)
        return

    if text == "⚡ اختيار سريع":
        await quick_select(message, context)
        return

    if text == "⚙️ اختيار متقدم":
        await advanced_select(message)
        return

    if text == "🌅 أذكار الصباح":
        await send_morning(message)
        return

    if text == "🌙 أذكار المساء":
        await send_evening(message)
        return

    if text == "📕 القرآن الكريم PDF":
        await send_quran_pdf(message)
        return

    if text == "📚 تفسير القرآن PDF":
        await send_tafsir_pdf(message)
        return

    if text == "📢 قناتنا على تيليجرام":
        await channel(message)
        return

    if text == "🌐 تغيير اللغة":
        await language(message)
        return

    # صفحات القرّاء
    if text == "التالي ➡️":
        page = context.user_data.get("reciter_page", 0) + 1
        context.user_data["reciter_page"] = page

        await show_reciters(message, page)
        return

    if text == "⬅️ السابق":
        page = max(
            0,
            context.user_data.get("reciter_page", 0) - 1
        )

        context.user_data["reciter_page"] = page

        await show_reciters(message, page)
        return

    # اختيار قارئ
    if text in RECITER_NAMES:
        reciter = await find_reciter(text)

        if not reciter:
            await message.reply_text(
                "⚠️ هذا القارئ غير متوفر حاليًا في المصدر الصوتي."
            )
            return

        moshafs = reciter.get("moshaf", [])

        if not moshafs:
            await message.reply_text(
                "⚠️ لا توجد روايات صوتية لهذا القارئ."
            )
            return

        context.user_data["reciter"] = reciter
        context.user_data["moshaf"] = moshafs[0]

        await message.reply_text(
            f"🎙️ {reciter.get('name', text)}\n\n"
            "📜 اختر الرواية:",
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        m.get("name", "الرواية")
                        for m in moshafs[i:i + 2]
                    ]
                    for i in range(0, len(moshafs), 2)
                ]
                + [["🏠 الرئيسية"]],
                resize_keyboard=True,
                is_persistent=True,
            ),
        )
        return

    # اختيار الرواية
    selected_reciter = context.user_data.get("reciter")

    if selected_reciter:
        for moshaf in selected_reciter.get("moshaf", []):
            if text == moshaf.get("name"):
                context.user_data["moshaf"] = moshaf

                await message.reply_text(
                    "📖 اختر السورة:",
                    reply_markup=HOME_MARKUP,
                )

                suwar = await get_suwar()

                keyboard = []

                for i in range(0, min(30, len(suwar)), 2):
                    keyboard.append([
                        f"{s.get('id')} - {s.get('name')}"
                        for s in suwar[i:i + 2]
                    ])

                keyboard.append(["🏠 الرئيسية"])

                await message.reply_text(
                    "السور:",
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard,
                        resize_keyboard=True,
                        is_persistent=True,
                    ),
                )
                return

    # اختيار السورة
    if " - " in text:
        possible_id = text.split(" - ")[0].strip()

        if possible_id.isdigit():
            await send_surah(
                update,
                context,
                int(possible_id),
            )
            return

    # أي نص غير معروف
    await message.reply_text(
        "اختر من الأزرار الموجودة أسفل الشاشة 👇",
        reply_markup=HOME_MARKUP,
    )


# =========================================================
# تشغيل البوت
# =========================================================

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود في متغيرات البيئة."
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
            text_router,
        )
    )

    print("Quran Bot is running...")

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
