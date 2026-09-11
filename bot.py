import os
import random
import difflib
import requests

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================================================
# الإعدادات
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

QURAN_PDF_URL = os.getenv("QURAN_PDF_URL", "")
TAFSIR_PDF_URL = os.getenv("TAFSIR_PDF_URL", "")

API = "https://www.mp3quran.net/api/v3"

PAGE_SIZE = 10

# =========================================================
# أسماء السور
# =========================================================

SURAHS = [
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
# القراء الذين طلبتهم
# =========================================================

REQUESTED_RECITERS = [
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
    "محمد عثمان خان",
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

# =========================================================
# الأذكار
# =========================================================

MORNING_AZKAR = """
أذكار الصباح

1. آية الكرسي.
2. قل هو الله أحد، وقل أعوذ برب الفلق، وقل أعوذ برب الناس. ثلاث مرات.
3. أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.
4. اللهم بك أصبحنا وبك أمسينا وبك نحيا وبك نموت وإليك النشور.
5. رضيت بالله رباً، وبالإسلام ديناً، وبمحمد صلى الله عليه وسلم نبياً. ثلاث مرات.
6. حسبي الله لا إله إلا هو عليه توكلت وهو رب العرش العظيم. سبع مرات.
7. اللهم إني أسألك العفو والعافية في الدنيا والآخرة.
8. سبحان الله وبحمده. مائة مرة.
"""

EVENING_AZKAR = """
أذكار المساء

1. آية الكرسي.
2. قل هو الله أحد، وقل أعوذ برب الفلق، وقل أعوذ برب الناس. ثلاث مرات.
3. أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.
4. اللهم بك أمسينا وبك أصبحنا وبك نحيا وبك نموت وإليك المصير.
5. رضيت بالله رباً، وبالإسلام ديناً، وبمحمد صلى الله عليه وسلم نبياً. ثلاث مرات.
6. أعوذ بكلمات الله التامات من شر ما خلق. ثلاث مرات.
7. سبحان الله وبحمده. مائة مرة.
"""

# =========================================================
# جلب البيانات من MP3Quran
# =========================================================

def api_get(url):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


def get_all_reciters():
    data = api_get(f"{API}/reciters?language=ar")
    return data.get("reciters", [])


def normalize(text):
    if not text:
        return ""

    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ة": "ه",
        "ؤ": "و",
        "ئ": "ي",
    }

    text = text.strip().lower()

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


def find_reciter(name, reciters):
    target = normalize(name)

    best = None
    best_score = 0

    for reciter in reciters:
        api_name = reciter.get("name", "")
        score = difflib.SequenceMatcher(
            None,
            target,
            normalize(api_name)
        ).ratio()

        if target in normalize(api_name) or normalize(api_name) in target:
            score += 0.35

        if score > best_score:
            best_score = score
            best = reciter

    if best_score >= 0.45:
        return best

    return None


# =========================================================
# القائمة الرئيسية
# =========================================================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("📖 المصحف", callback_data="quran"),
            InlineKeyboardButton("🎙️ القرّاء", callback_data="reciters:0"),
        ],
        [
            InlineKeyboardButton("📜 الروايات", callback_data="riwayat"),
            InlineKeyboardButton("🎲 عشوائي", callback_data="random"),
        ],
        [
            InlineKeyboardButton("⚡ اختيار سريع", callback_data="quick"),
            InlineKeyboardButton("⚙️ اختيار متقدم", callback_data="advanced"),
        ],
        [
            InlineKeyboardButton("🌅 أذكار الصباح", callback_data="morning"),
            InlineKeyboardButton("🌙 أذكار المساء", callback_data="evening"),
        ],
        [
            InlineKeyboardButton("📕 القرآن الكريم PDF", callback_data="quran_pdf"),
        ],
        [
            InlineKeyboardButton("📚 تفسير القرآن PDF", callback_data="tafsir_pdf"),
        ],
        [
            InlineKeyboardButton("🌐 تغيير اللغة", callback_data="language"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕌 قرآن بوت\n\n"
        "مرحباً بك في قرآن بوت.\n"
        "اختر من القائمة ما تريد:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# قائمة السور
# =========================================================

def surah_menu(page=0):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    keyboard = []

    for i in range(start, min(end, len(SURAHS))):
        keyboard.append([
            InlineKeyboardButton(
                f"{i + 1}. {SURAHS[i]}",
                callback_data=f"surah:{i + 1}"
            )
        ])

    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                "السابق",
                callback_data=f"surahpage:{page - 1}"
            )
        )

    if end < len(SURAHS):
        navigation.append(
            InlineKeyboardButton(
                "التالي",
                callback_data=f"surahpage:{page + 1}"
            )
        )

    if navigation:
        keyboard.append(navigation)

    keyboard.append([
        InlineKeyboardButton("رجوع", callback_data="home")
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# قائمة القراء
# =========================================================

def reciter_menu(page=0):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    keyboard = []

    for i in range(start, min(end, len(REQUESTED_RECITERS))):
        name = REQUESTED_RECITERS[i]

        keyboard.append([
            InlineKeyboardButton(
                name,
                callback_data=f"reciter:{i}"
            )
        ])

    navigation = []

    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                "السابق",
                callback_data=f"reciters:{page - 1}"
            )
        )

    if end < len(REQUESTED_RECITERS):
        navigation.append(
            InlineKeyboardButton(
                "التالي",
                callback_data=f"reciters:{page + 1}"
            )
        )

    if navigation:
        keyboard.append(navigation)

    keyboard.append([
        InlineKeyboardButton("رجوع", callback_data="home")
    ])

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# الروايات
# =========================================================

def riwayat_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "حفص عن عاصم - مرتل",
                callback_data="riwaya:hafs"
            )
        ],
        [
            InlineKeyboardButton(
                "ورش عن نافع",
                callback_data="riwaya:warch"
            )
        ],
        [
            InlineKeyboardButton(
                "قالون عن نافع",
                callback_data="riwaya:qalon"
            )
        ],
        [
            InlineKeyboardButton(
                "الدوري عن أبي عمرو",
                callback_data="riwaya:douri"
            )
        ],
        [
            InlineKeyboardButton(
                "رجوع",
                callback_data="home"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================================================
# تشغيل سورة لقارئ
# =========================================================

async def send_surah(
    query,
    reciter_name,
    surah_number
):
    await query.answer()

    reciters = get_all_reciters()

    reciter = find_reciter(
        reciter_name,
        reciters
    )

    if not reciter:
        await query.message.reply_text(
            "تعذر العثور على هذا القارئ في مصدر الصوت حالياً."
        )
        return

    moshaf_list = reciter.get("moshaf", [])

    if not moshaf_list:
        await query.message.reply_text(
            "لا توجد رواية صوتية متاحة لهذا القارئ."
        )
        return

    moshaf = moshaf_list[0]

    server = moshaf.get("server", "")

    if not server:
        await query.message.reply_text(
            "تعذر الحصول على رابط الصوت."
        )
        return

    surah_list = str(
        moshaf.get("surah_list", "")
    ).split(",")

    if str(surah_number) not in surah_list:
        await query.message.reply_text(
            "هذه السورة غير متوفرة بهذه الرواية لهذا القارئ."
        )
        return

    audio_url = (
        server.rstrip("/")
        + "/"
        + str(surah_number).zfill(3)
        + ".mp3"
    )

    surah_name = SURAHS[surah_number - 1]

    caption = (
        f"🎙️ القارئ: {reciter.get('name', reciter_name)}\n"
        f"📖 السورة: {surah_name}\n"
        f"📜 الرواية: {moshaf.get('name', 'غير محددة')}"
    )

    try:
        await query.message.reply_audio(
            audio=audio_url,
            title=f"{surah_name} - {reciter.get('name', reciter_name)}",
            performer=reciter.get("name", reciter_name),
            caption=caption,
        )
    except Exception as error:
        print("Audio error:", error)

        await query.message.reply_text(
            "تعذر إرسال الملف الصوتي. حاول مرة أخرى."
        )


# =========================================================
# أزرار البوت
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    data = query.data

    # الصفحة الرئيسية
    if data == "home":
        await query.answer()

        await query.edit_message_text(
            "🕌 قرآن بوت\n\nاختر من القائمة:",
            reply_markup=main_menu()
        )
        return

    # المصحف
    if data == "quran":
        await query.answer()

        await query.edit_message_text(
            "📖 اختر السورة:",
            reply_markup=surah_menu(0)
        )
        return

    # صفحات السور
    if data.startswith("surahpage:"):
        page = int(data.split(":")[1])

        await query.answer()

        await query.edit_message_text(
            "📖 اختر السورة:",
            reply_markup=surah_menu(page)
        )
        return

    # القراء
    if data.startswith("reciters:"):
        page = int(data.split(":")[1])

        await query.answer()

        await query.edit_message_text(
            "🎙️ اختر القارئ:",
            reply_markup=reciter_menu(page)
        )
        return

    # اختيار قارئ
    if data.startswith("reciter:"):
        index = int(data.split(":")[1])

        if index >= len(REQUESTED_RECITERS):
            await query.answer("القارئ غير موجود")
            return

        name = REQUESTED_RECITERS[index]

        context.user_data["reciter_name"] = name

        await query.answer()

        await query.edit_message_text(
            f"🎙️ القارئ المختار:\n{name}\n\n"
            "📖 اختر السورة:",
            reply_markup=surah_menu(0)
        )
        return

    # اختيار سورة
    if data.startswith("surah:"):
        number = int(data.split(":")[1])

        reciter_name = context.user_data.get(
            "reciter_name"
        )

        await query.answer()

        if not reciter_name:
            await query.message.reply_text(
                "اختر القارئ أولاً من قائمة القراء."
            )
            return

        await query.message.reply_text(
            f"جاري تجهيز سورة {SURAHS[number - 1]}..."
        )

        await send_surah(
            query,
            reciter_name,
            number
        )
        return

    # الروايات
    if data == "riwayat":
        await query.answer()

        await query.edit_message_text(
            "📜 اختر الرواية:",
            reply_markup=riwayat_menu()
        )
        return

    # الرواية
    if data.startswith("riwaya:"):
        await query.answer()

        await query.edit_message_text(
            "📜 الرواية المختارة.\n\n"
            "اختر القارئ من قائمة القراء:",
            reply_markup=reciter_menu(0)
        )
        return

    # عشوائي
    if data == "random":
        await query.answer()

        reciters = get_all_reciters()

        if not reciters:
            await query.message.reply_text(
                "تعذر تحميل قائمة القراء حالياً."
            )
            return

        reciter = random.choice(reciters)

        moshaf_list = reciter.get("moshaf", [])

        if not moshaf_list:
            await query.message.reply_text(
                "تعذر العثور على تسجيل لهذا القارئ."
            )
            return

        moshaf = random.choice(moshaf_list)

        available = str(
            moshaf.get("surah_list", "")
        ).split(",")

        available = [
            int(x)
            for x in available
            if x.strip().isdigit()
        ]

        if not available:
            await query.message.reply_text(
                "تعذر العثور على سورة."
            )
            return

        surah_number = random.choice(available)

        context.user_data["reciter_name"] = reciter.get(
            "name",
            ""
        )

        await query.message.reply_text(
            f"🎲 اختيار عشوائي\n\n"
            f"🎙️ {reciter.get('name', '')}\n"
            f"📖 {SURAHS[surah_number - 1]}"
        )

        await send_surah(
            query,
            reciter.get("name", ""),
            surah_number
        )
        return

    # اختيار سريع
    if data == "quick":
        await query.answer()

        context.user_data["reciter_name"] = None

        await query.edit_message_text(
            "⚡ اختيار سريع\n\n"
            "اختر القارئ:",
            reply_markup=reciter_menu(0)
        )
        return

    # اختيار متقدم
    if data == "advanced":
        await query.answer()

        await query.edit_message_text(
            "⚙️ الاختيار المتقدم\n\n"
            "اختر القارئ أولاً:",
            reply_markup=reciter_menu(0)
        )
        return

    # أذكار الصباح
    if data == "morning":
        await query.answer()

        await query.edit_message_text(
            MORNING_AZKAR,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "رجوع",
                        callback_data="home"
                    )
                ]
            ])
        )
        return

    # أذكار المساء
    if data == "evening":
        await query.answer()

        await query.edit_message_text(
            EVENING_AZKAR,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "رجوع",
                        callback_data="home"
                    )
                ]
            ])
        )
        return

    # القرآن PDF
    if data == "quran_pdf":
        await query.answer()

        if not QURAN_PDF_URL:
            await query.message.reply_text(
                "📕 ملف القرآن PDF لم تتم إضافة رابطه بعد.\n\n"
                "سنضيفه في إعدادات Railway لاحقاً."
            )
            return

        await query.message.reply_document(
            document=QURAN_PDF_URL,
            caption="📕 القرآن الكريم"
        )
        return

    # تفسير PDF
    if data == "tafsir_pdf":
        await query.answer()

        if not TAFSIR_PDF_URL:
            await query.message.reply_text(
                "📚 ملف تفسير القرآن PDF لم تتم إضافة رابطه بعد.\n\n"
                "سنضيفه في إعدادات Railway لاحقاً."
            )
            return

        await query.message.reply_document(
            document=TAFSIR_PDF_URL,
            caption="📚 تفسير القرآن الكريم"
        )
        return

    # اللغة
    if data == "language":
        await query.answer()

        keyboard = [
            [
                InlineKeyboardButton(
                    "العربية",
                    callback_data="lang:ar"
                ),
                InlineKeyboardButton(
                    "English",
                    callback_data="lang:en"
                ),
            ],
            [
                InlineKeyboardButton(
                    "رجوع",
                    callback_data="home"
                )
            ]
        ]

        await query.edit_message_text(
            "🌐 اختر اللغة:",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )
        return

    # العربية
    if data == "lang:ar":
        await query.answer("تم اختيار العربية")

        await query.edit_message_text(
            "🕌 قرآن بوت\n\nاختر من القائمة:",
            reply_markup=main_menu()
        )
        return

    # الإنجليزية
    if data == "lang:en":
        await query.answer("English selected")

        keyboard = [
            [
                InlineKeyboardButton(
                    "📖 Quran",
                    callback_data="quran"
                ),
                InlineKeyboardButton(
                    "🎙️ Reciters",
                    callback_data="reciters:0"
                )
            ],
            [
                InlineKeyboardButton(
                    "🎲 Random",
                    callback_data="random"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌐 Arabic",
                    callback_data="lang:ar"
                )
            ]
        ]

        await query.edit_message_text(
            "🕌 Quran Bot\n\nChoose:",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )
        return


# =========================================================
# تشغيل البوت
# =========================================================

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN غير موجود في Railway Variables"
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
        CallbackQueryHandler(button_handler)
    )

    print("Quran Bot is running...")

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
