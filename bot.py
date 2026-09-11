import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في ملف .env")

CHANNEL_USERNAME = "@x7oly"
CHANNEL_LINK = "https://t.me/x7oly"

LANGUAGES = {
    "ar": "🇸🇦 العربية",
    "en": "🇬🇧 English",
    "fr": "🇫🇷 Français",
    "tr": "🇹🇷 Türkçe",
    "ur": "🇵🇰 اردو",
    "id": "🇮🇩 Indonesia",
}

DEFAULT_LANGUAGE = "ar"
from typing import List, Dict

# =============== أسماء السور ===============
SURAH_NAMES: Dict[str, List[str]] = {
    "ar": [
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
        "المسد", "الإخلاص", "الفلق", "الناس",
    ],
    "en": [
        "Al-Fatiha", "Al-Baqarah", "Aal-e-Imran", "An-Nisa", "Al-Ma'idah",
        "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus",
        "Hud", "Yusuf", "Ar-Ra'd", "Ibrahim", "Al-Hijr",
        "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Taha",
        "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan",
        "Ash-Shu'ara", "An-Naml", "Al-Qasas", "Al-Ankabut", "Ar-Rum",
        "Luqman", "As-Sajda", "Al-Ahzab", "Saba", "Fatir",
        "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir",
        "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiya",
        "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf",
        "Adh-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman",
        "Al-Waqi'a", "Al-Hadid", "Al-Mujadila", "Al-Hashr", "Al-Mumtahina",
        "As-Saff", "Al-Jumu'a", "Al-Munafiqun", "At-Taghabun", "At-Talaq",
        "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqa", "Al-Ma'arij",
        "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyama",
        "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "Abasa",
        "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj",
        "At-Tariq", "Al-A'la", "Al-Ghashiya", "Al-Fajr", "Al-Balad",
        "Ash-Shams", "Al-Layl", "Ad-Duha", "Ash-Sharh", "At-Tin",
        "Al-Alaq", "Al-Qadr", "Al-Bayyina", "Az-Zalzala", "Al-Adiyat",
        "Al-Qari'a", "At-Takathur", "Al-Asr", "Al-Humaza", "Al-Fil",
        "Quraysh", "Al-Ma'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr",
        "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas",
    ],
}

# =============== القراء (60 قارئ) ===============
RECITERS: List[Dict[str, str]] = [
    {"id": "ar.abdulbasitmurattal",     "name": "عبد الباسط عبد الصمد (مرتل)"},
    {"id": "ar.abdulbasitmujawwad",     "name": "عبد الباسط عبد الصمد (مجود)"},
    {"id": "ar.abdurrahmaansudais",     "name": "عبد الرحمن السديس"},
    {"id": "ar.saudalshuraym",          "name": "سعود الشريم"},
    {"id": "ar.misharyalafasy",         "name": "مشاري العفاسي"},
    {"id": "ar.mahermuaiqly",           "name": "ماهر المعيقلي"},
    {"id": "ar.saoodshuraym",           "name": "سعود الشريم (مجود)"},
    {"id": "ar.yasseraldosari",         "name": "ياسر الدوسري"},
    {"id": "ar.naifalqurashi",          "name": "نايف القرشي"},
    {"id": "ar.ahmadalajmy",            "name": "أحمد العجمي"},
    {"id": "ar.abdullahbasfar",         "name": "عبد الله باسفر"},
    {"id": "ar.khalifahaltunaiji",      "name": "خليفة الطنيجي"},
    {"id": "ar.abobakeralshatri",       "name": "أبو بكر الشاطري"},
    {"id": "ar.hanialrifai",            "name": "هاني الرفاعي"},
    {"id": "ar.aliabdurrahmanahudhaifi","name": "علي الحذيفي"},
    {"id": "ar.muhammadjibreel",        "name": "محمد جبريل"},
    {"id": "ar.wadialyemeni",           "name": "وادي اليمني"},
    {"id": "ar.khalidjalil",            "name": "خالد الجليل"},
    {"id": "ar.tareqibrahim",           "name": "طارق إبراهيم"},
    {"id": "ar.nasserqatami",           "name": "ناصر القطامي"},
    {"id": "ar.salahbukhatir",          "name": "صلاح بو خاطر"},
    {"id": "ar.mahmoudali",            "name": "محمود علي"},
    {"id": "ar.ibrahimakhder",          "name": "إبراهيم الأخضر"},
    {"id": "ar.muhammadayyoub",         "name": "محمد أيوب"},
    {"id": "ar.saadghamidi",            "name": "سعد الغامدي"},
    {"id": "ar.abdullahjuhani",         "name": "عبد الله الجهني"},
    {"id": "ar.abdulmuhsenalqasim",     "name": "عبد المحسن القاسم"},
    {"id": "ar.ahmedalhussary",         "name": "أحمد الحصري"},
    {"id": "ar.aliabdullahjabir",       "name": "علي بن عبد الله جابر"},
    {"id": "ar.muhammadal-minshawi",    "name": "محمد المنشاوي"},
    {"id": "ar.mahmoudalhosary",        "name": "محمود الحصري"},
    {"id": "ar.mustafaismail",          "name": "مصطفى إسماعيل"},
    {"id": "ar.muhammadalbarrak",       "name": "محمد البراك"},
    {"id": "ar.abdullahalmusallam",     "name": "عبد الله المسلم"},
    {"id": "ar.ahmedal-thunayyan",      "name": "أحمد الثنيان"},
    {"id": "ar.abdulazizal-ahmadi",     "name": "عبد العزيز الأحمدي"},
    {"id": "ar.abdulrahmanal-majed",    "name": "عبد الرحمن الماجد"},
    {"id": "ar.ahmedbinali",            "name": "أحمد بن علي"},
    {"id": "ar.faisalalshmry",          "name": "فيصل الشمري"},
    {"id": "ar.hamzabukamal",           "name": "حمزة بوكمال"},
    {"id": "ar.hussainalsheikh",        "name": "حسين الشيخ"},
    {"id": "ar.ibrahimal-jibreen",      "name": "إبراهيم الجبرين"},
    {"id": "ar.khalidalhareth",         "name": "خالد الحارث"},
    {"id": "ar.maheral-hawari",         "name": "ماهر الهواري"},
    {"id": "ar.muhammadalhasan",        "name": "محمد الحسن"},
    {"id": "ar.muhammadal-luhaidan",    "name": "محمد اللحيدان"},
    {"id": "ar.muhammadal-tablawy",     "name": "محمد الطبلاوي"},
    {"id": "ar.nasseral-saadi",         "name": "ناصر السعدي"},
    {"id": "ar.omaral-qazwini",         "name": "عمر القزويني"},
    {"id": "ar.osaamakhayat",           "name": "أسامة خياط"},
    {"id": "ar.ramadanalnafea",         "name": "رمضان النافع"},
    {"id": "ar.salihahmad",             "name": "صالح أحمد"},
    {"id": "ar.salehal-aboody",         "name": "صالح العبودي"},
    {"id": "ar.salahal-budair",         "name": "صلاح البدير"},
    {"id": "ar.talhaal-balbali",        "name": "طلحه البلبل"},
    {"id": "ar.zaidal-hussain",         "name": "زيد الحسين"},
    {"id": "ar.ziadal-abdullah",        "name": "زياد العبد الله"},
    {"id": "ar.abdulraheemm",           "name": "عبد الرحيم م"},
    {"id": "ar.zakeriyah",              "name": "ذاكريا"},
]

# =============== القراءات العشر ===============
QIRAAT: List[Dict[str, str]] = [
    {"id": "quran",         "name": "📖 رواية حفص عن عاصم"},
    {"id": "quran/warsh",   "name": "📖 رواية ورش عن نافع"},
    {"id": "quran/qaloon",  "name": "📖 رواية قالون عن نافع"},
    {"id": "quran/doori",   "name": "📖 رواية الدوري عن أبي عمرو"},
    {"id": "quran/sousi",   "name": "📖 رواية السوسي عن أبي عمرو"},
    {"id": "quran/hisham",  "name": "📖 رواية هشام عن ابن عامر"},
    {"id": "quran/ibnthaker", "name": "📖 رواية ابن ذكوان عن ابن عامر"},
    {"id": "quran/shuba",   "name": "📖 رواية شعبة عن عاصم"},
    {"id": "quran/khalad",  "name": "📖 رواية خلف عن حمزة"},
    {"id": "quran/khallad", "name": "📖 رواية خلاد عن حمزة"},
]

# =============== أذكار الصباح ===============
MORNING_ADHKAR: List[Dict[str, str]] = [
    {
        "text": "اللَّهُ لاَ إِلَهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ... آية الكرسي",
        "reference": "سورة البقرة - الآية 255",
        "audio_url": "https://www.example.com/adhkar/ayatalkursi.mp3",
    },
    {
        "text": "أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ",
        "reference": "قراءة المعوذات (الإخلاص - الفلق - الناس) 3 مرات",
        "audio_url": None,
    },
    {
        "text": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ لاَ إِلَهَ إِلاَّ اللَّهُ وَحْدَهُ لاَ شَرِيكَ لَهُ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ الْمَصِيرُ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ أَنْتَ رَبِّي لاَ إِلَهَ إِلاَّ أَنْتَ خَلَقْتَنِي وَأَنَا عَبْدُكَ...",
        "reference": "سيد الاستغفار",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ إِنِّي أَصْبَحْتُ أُشْهِدُكَ وَأُشْهِدُ حَمَلَةَ عَرْشِكَ وَمَلاَئِكَتَكَ وَجَمِيعَ خَلْقِكَ أَنَّكَ أَنْتَ اللَّهُ لاَ إِلَهَ إِلاَّ أَنْتَ وَأَنَّ مُحَمَّدًا عَبْدُكَ وَرَسُولُكَ",
        "reference": "أذكار الصباح (4 مرات)",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ مَا أَصْبَحَ بِي مِنْ نِعْمَةٍ أَوْ بِأَحَدٍ مِنْ خَلْقِكَ فَمِنْكَ وَحْدَكَ لاَ شَرِيكَ لَكَ فَلَكَ الْحَمْدُ وَلَكَ الشُّكْرُ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، اللَّهُمَّ عَافِنِي فِي بَصَرِي، لاَ إِلَهَ إِلاَّ أَنْتَ",
        "reference": "أذكار الصباح (3 مرات)",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ وَعَذَابِ الْقَبْرِ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ: عَدَدَ خَلْقِهِ وَرِضَا نَفْسِهِ وَزِنَةَ عَرْشِهِ وَمِدَادَ كَلِمَاتِهِ",
        "reference": "أذكار الصباح (3 مرات)",
        "audio_url": None,
    },
    {
        "text": "سُبْحَانَ اللَّهِ الْعَظِيمِ وَبِحَمْدِهِ",
        "reference": "أذكار الصباح (100 مرة)",
        "audio_url": None,
    },
    {
        "text": "لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
        "reference": "أذكار الصباح (10 مرات أو مرة)",
        "audio_url": None,
    },
    {
        "text": "بِسْمِ اللَّهِ الَّذِي لاَ يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الأَرْضِ وَلاَ فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ",
        "reference": "أذكار الصباح (3 مرات)",
        "audio_url": None,
    },
    {
        "text": "رَضِيتُ بِاللَّهِ رَبًّا، وَبِالإِسْلاَمِ دِينًا، وَبِمُحَمَّدٍ صلى الله عليه وسلم نَبِيًّا",
        "reference": "أذكار الصباح (3 مرات)",
        "audio_url": None,
    },
    {
        "text": "يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ أَصْلِحْ لِي شَأْنِي كُلَّهُ وَلاَ تَكِلْنِي إِلَى نَفْسِي طَرْفَةَ عَيْنٍ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "أَصْبَحْنَا عَلَى فِطْرَةِ الإِسْلاَمِ وَعَلَى كَلِمَةِ الإِخْلاَصِ وَعَلَى دِينِ نَبِيِّنَا مُحَمَّدٍ صلى الله عليه وسلم وَعَلَى مِلَّةِ أَبِينَا إِبْرَاهِيمَ حَنِيفًا مُسْلِمًا وَمَا كَانَ مِنَ الْمُشْرِكِينَ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ إِنَّا نَعُوذُ بِكَ مِنْ أَنْ نُشْرِكَ بِكَ شَيْئًا نَعْلَمُهُ وَنَسْتَغْفِرُكَ لِمَا لاَ نَعْلَمُهُ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
    {
        "text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ وَالْعَجْزِ وَالْكَسَلِ وَالْجُبْنِ وَالْبُخْلِ وَضَلَعِ الدَّيْنِ وَغَلَبَةِ الرِّجَالِ",
        "reference": "أذكار الصباح",
        "audio_url": None,
    },
]

# =============== فضل قراءة القرآن ===============
VIRTUES: List[Dict[str, str]] = [
    {
        "title": "✨ فضل قراءة القرآن",
        "text": "قال الله تعالى:\n"
                "﴿إِنَّ الَّذِينَ يَتْلُونَ كِتَابَ اللَّهِ وَأَقَامُوا الصَّلَاةَ وَأَنفَقُوا مِمَّا رَزَقْنَاهُمْ سِرًّا وَعَلَانِيَةً يَرْجُونَ تِجَارَةً لَّن تَبُورَ﴾\n"
                "[فاطر: 29]",
    },
    {
        "title": "🌙 حديث شريف",
        "text": "قال رسول الله ﷺ:\n"
                "«اقْرَؤُوا الْقُرْآنَ فَإِنَّهُ يَأْتِي يَوْمَ الْقِيَامَةِ شَفِيعًا لِأَصْحَابِهِ»\n"
                "[رواه مسلم]",
    },
    {
        "title": "📖 حديث شريف",
        "text": "قال رسول الله ﷺ:\n"
                "«خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ»\n"
                "[رواه البخاري]",
    },
    {
        "title": "💎 حديث شريف",
        "text": "قال رسول الله ﷺ:\n"
                "«مَنْ قَرَأَ حَرْفًا مِنْ كِتَابِ اللَّهِ فَلَهُ بِهِ حَسَنَةٌ، وَالْحَسَنَةُ بِعَشْرِ أَمْثَالِهَا، لَا أَقُولُ الم حَرْفٌ، وَلَكِنْ أَلِفٌ حَرْفٌ وَلَامٌ حَرْفٌ وَمِيمٌ حَرْفٌ»\n"
                "[رواه الترمذي]",
    },
    {
        "title": "🌟 حديث شريف",
        "text": "قال رسول الله ﷺ:\n"
                "«يُقَالُ لِصَاحِبِ الْقُرْآنِ: اقْرَأْ وَارْتَقِ وَرَتِّلْ كَمَا كُنْتَ تُرَتِّلُ فِي الدُّنْيَا، فَإِنَّ مَنْزِلَكَ عِنْدَ آخِرِ آيَةٍ تَقْرَؤُهَا»\n"
                "[رواه أبو داود والترمذي]",
    },
    {
        "title": "🌿 حديث شريف",
        "text": "قال رسول الله ﷺ:\n"
                "«مَثَلُ الْمُؤْمِنِ الَّذِي يَقْرَأُ الْقُرْآنَ مَثَلُ الْأُتْرُجَّةِ، رِيحُهَا طَيِّبٌ وَطَعْمُهَا طَيِّبٌ»\n"
                "[رواه البخاري ومسلم]",
    },
    {
        "title": "🤲 دعاء ختم القرآن",
        "text": "اللَّهُمَّ ارْحَمْنِي بِالْقُرْآنِ الْعَظِيمِ، وَاجْعَلْهُ لِي إِمَامًا وَنُورًا وَهُدًى وَرَحْمَةً، "
                "اللَّهُمَّ ذَكِّرْنِي مِنْهُ مَا نَسِيتُ وَعَلِّمْنِي مِنْهُ مَا جَهِلْتُ وَارْزُقْنِي تِلَاوَتَهُ آنَاءَ اللَّيْلِ وَأَطْرَافَ النَّهَارِ، "
                "وَاجْعَلْهُ لِي حُجَّةً يَا رَبَّ الْعَالَمِينَ",
    },
]
import httpx
from typing import Optional, Dict, Any

BASE_URL = "https://api.alquran.cloud/v1"

async def fetch_surah_text(surah_number: int) -> Optional[str]:
    """جلب نص السورة من API"""
    url = f"{BASE_URL}/surah/{surah_number}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    surah = data.get("data", {})
                    ayahs = surah.get("ayahs", [])
                    text = ""
                    for idx, ayah in enumerate(ayahs, 1):
                        text += f"{idx}. {ayah.get('text', '')}\n"
                    return text
        return None
    except (httpx.TimeoutException, httpx.RequestError) as e:
        print(f"⚠️ فشل الاتصال: {e}")
        return None


async def fetch_ayahs_paginated(surah_number: int, page: int = 0, page_size: int = 10) -> Optional[Dict[str, Any]]:
    """جلب آيات السورة مع التقسيم إلى صفحات"""
    url = f"{BASE_URL}/surah/{surah_number}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    ayahs = data["data"]["ayahs"]
                    total = len(ayahs)
                    start = page * page_size
                    end = min(start + page_size, total)
                    verses = []
                    for i in range(start, end):
                        ayah = ayahs[i]
                        verses.append({
                            "number": i + 1,
                            "text": ayah.get("text", ""),
                            "surah": surah_number,
                        })
                    return {
                        "verses": verses,
                        "total": total,
                        "page": page,
                        "page_size": page_size,
                        "has_next": end < total,
                        "has_prev": page > 0,
                    }
        return None
    except (httpx.TimeoutException, httpx.RequestError) as e:
        print(f"⚠️ فشل الاتصال: {e}")
        return None


async def fetch_audio_url(surah_number: int, reciter_id: str) -> Optional[str]:
    """جلب رابط صوت السورة من قارئ معين"""
    url = f"{BASE_URL}/surah/{surah_number}/{reciter_id}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    return data["data"].get("ayahs", [{}])[0].get("audio", None)
        return None
    except (httpx.TimeoutException, httpx.RequestError) as e:
        print(f"⚠️ فشل الاتصال: {e}")
        return None


async def fetch_surah_info(surah_number: int) -> Optional[Dict[str, Any]]:
    """جلب معلومات السورة"""
    url = f"{BASE_URL}/surah/{surah_number}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == 200:
                    surah = data["data"]
                    return {
                        "number": surah["number"],
                        "name": surah["name"],
                        "englishName": surah["englishName"],
                        "revelationType": surah["revelationType"],
                        "numberOfAyahs": surah["numberOfAyahs"],
                    }
        return None
    except (httpx.TimeoutException, httpx.RequestError) as e:
        print(f"⚠️ فشل الاتصال: {e}")
        return None


async def fetch_adhkar_audio() -> Dict[int, str]:
    """مصدر صوت للأذكار - نستخدم روابط عامة أو نحتفظ بها محلياً"""
    # يمكن استخدام روابط صوتية من مصادر موثوقة
    # أو تركها None ليتم عرض النص فقط
    return {}
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import CHANNEL_LINK, LANGUAGES
from data import SURAH_NAMES, RECITERS, QIRAAT, MORNING_ADHKAR, VIRTUES

# =============== القائمة الرئيسية ===============
def main_menu(lang: str = "ar") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📖 المصحف للقراءة", callback_data="read_quran")],
        [InlineKeyboardButton("🎲 سورة عشوائية", callback_data="random_surah")],
        [InlineKeyboardButton("🌐 تغيير اللغة", callback_data="change_lang")],
        [InlineKeyboardButton("⚙️ الإعدادات المتقدمة", callback_data="advanced_settings")],
        [InlineKeyboardButton("📿 أذكار الصباح", callback_data="morning_adhkar")],
        [InlineKeyboardButton("✨ فضل قراءة القرآن", callback_data="virtues")],
        [InlineKeyboardButton("📢 قناة البوت", url=CHANNEL_LINK)],
    ]
    return InlineKeyboardMarkup(keyboard)


# =============== قائمة السور (مع أزرار التصفح) ===============
def surah_list_keyboard(page: int = 0, lang: str = "ar") -> InlineKeyboardMarkup:
    surahs = SURAH_NAMES.get(lang, SURAH_NAMES["ar"])
    page_size = 10
    start = page * page_size
    end = min(start + page_size, len(surahs))
    
    keyboard = []
    for i in range(start, end):
        num = i + 1
        name = surahs[i]
        keyboard.append([
            InlineKeyboardButton(f"{num}. {name}", callback_data=f"surah_{num}")
        ])
    
    nav_buttons = []
    total_pages = (len(surahs) + page_size - 1) // page_size
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"surah_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"surah_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


# =============== أزرار السورة (نص / صوت / رجوع) ===============
def surah_action_keyboard(surah_number: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📖 قراءة النص", callback_data=f"read_{surah_number}")],
        [InlineKeyboardButton("🎧 استماع", callback_data=f"play_{surah_number}")],
        [InlineKeyboardButton("🔙 رجوع للسور", callback_data="read_quran")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# =============== أزرار الإعدادات المتقدمة ===============
def advanced_settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎙️ اختيار القارئ", callback_data="choose_reciter")],
        [InlineKeyboardButton("📖 اختيار القراءة (القراءات العشر)", callback_data="choose_qiraat")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# =============== قائمة القراء (مقسمة صفحات) ===============
def reciters_keyboard(page: int = 0, selected: str = "") -> InlineKeyboardMarkup:
    page_size = 8
    start = page * page_size
    end = min(start + page_size, len(RECITERS))
    
    keyboard = []
    for i in range(start, end):
        reciter = RECITERS[i]
        mark = "✅ " if reciter["id"] == selected else ""
        keyboard.append([
            InlineKeyboardButton(f"{mark}{reciter['name']}", callback_data=f"reciter_{reciter['id']}")
        ])
    
    nav_buttons = []
    total_pages = (len(RECITERS) + page_size - 1) // page_size
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"reciter_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"reciter_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="advanced_settings")])
    
    return InlineKeyboardMarkup(keyboard)


# =============== قائمة القراءات العشر ===============
def qiraat_keyboard(selected: str = "") -> InlineKeyboardMarkup:
    keyboard = []
    for qiraa in QIRAAT:
        mark = "✅ " if qiraa["id"] == selected else ""
        keyboard.append([
            InlineKeyboardButton(f"{mark}{qiraa['name']}", callback_data=f"qiraa_{qiraa['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="advanced_settings")])
    return InlineKeyboardMarkup(keyboard)


# =============== قائمة اللغات ===============
def lang_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for code, name in LANGUAGES.items():
        keyboard.append([
            InlineKeyboardButton(name, callback_data=f"lang_{code}")
        ])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


# =============== أزرار الأذكار ===============
def adhkar_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    page_size = 5
    total = len(MORNING_ADHKAR)
    total_pages = (total + page_size - 1) // page_size
    
    keyboard = []
    start = page * page_size
    end = min(start + page_size, total)
    
    for i in range(start, end):
        dhikr = MORNING_ADHKAR[i]
        # عرض أول 30 حرف من الذكر
        preview = dhikr["text"][:30] + "..." if len(dhikr["text"]) > 30 else dhikr["text"]
        keyboard.append([
            InlineKeyboardButton(f"📿 {preview}", callback_data=f"dhikr_{i}")
        ])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"adhkar_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"adhkar_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


# =============== أزرار الفضائل ===============
def virtues_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    page_size = 1  # عرض فضيلة واحدة كل مرة
    total = len(VIRTUES)
    total_pages = (total + page_size - 1) // page_size
    
    keyboard = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"virtue_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"virtue_page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)


# =============== أزرار التصفح في القراءة ===============
def reading_pagination_keyboard(surah_number: int, page: int, total_pages: int) -> InlineKeyboardMarkup:
    keyboard = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"read_page_{surah_number}_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"read_page_{surah_number}_{page+1}"))
    keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🎧 استماع", callback_data=f"play_{surah_number}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للسور", callback_data="read_quran")])
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from config import CHANNEL_LINK, DEFAULT_LANGUAGE
from data import SURAH_NAMES, RECITERS, QIRAAT, MORNING_ADHKAR, VIRTUES
from keyboards import (
    main_menu, surah_list_keyboard, surah_action_keyboard,
    advanced_settings_keyboard, reciters_keyboard, qiraat_keyboard,
    lang_keyboard, adhkar_keyboard, virtues_keyboard,
    reading_pagination_keyboard,
)
from api_client import (
    fetch_surah_text, fetch_ayahs_paginated,
    fetch_audio_url, fetch_surah_info,
)

# =============== تخزين بيانات المستخدمين مؤقتاً ===============
user_data_store = {}

def get_user_data(user_id: int) -> dict:
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            "lang": DEFAULT_LANGUAGE,
            "reciter": RECITERS[0]["id"] if RECITERS else "ar.abdulbasitmurattal",
            "qiraa": "quran",
        }
    return user_data_store[user_id]


# =============== أمر /start ===============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user_data(user.id)
    
    welcome_text = (
        f"🌙 *بسم الله الرحمن الرحيم*\n\n"
        f"أهلاً بك يا {user.first_name} في بوت القرآن الكريم 🕌\n\n"
        f"هذا البوت مخصص لتلاوة وقراءة القرآن الكريم، والأذكار، والفضائل.\n"
        f"اختر ما تريد من القائمة أدناه 👇\n\n"
        f"`#قناة_البوت:` {CHANNEL_LINK}"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu(user_data["lang"]),
        parse_mode="Markdown",
    )


# =============== معالجة النصوص ===============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إذا أرسل المستخدم نصاً، نعرض له القائمة"""
    await update.message.reply_text(
        "🕌 استخدم الأزرار للتنقل في القائمة.",
        reply_markup=main_menu(),
    )


# =============== معالج الأزرار (callback_query) ===============
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    user_data = get_user_data(user_id)
    lang = user_data["lang"]

    # ---- رجوع للقائمة الرئيسية ----
    if data == "main_menu":
        await query.edit_message_text(
            "🌙 القائمة الرئيسية:",
            reply_markup=main_menu(lang),
        )

    # ---- المصحف للقراءة ----
    elif data == "read_quran":
        surah_list = SURAH_NAMES.get(lang, SURAH_NAMES["ar"])
        await query.edit_message_text(
            f"📖 *اختر سورة من القرآن:*\n"
            f"إجمالي {len(surah_list)} سورة",
            reply_markup=surah_list_keyboard(0, lang),
            parse_mode="Markdown",
        )

    # ---- تصفح السور ----
    elif data.startswith("surah_page_"):
        page = int(data.split("_")[2])
        await query.edit_message_text(
            "📖 اختر سورة:",
            reply_markup=surah_list_keyboard(page, lang),
        )

    # ---- اختيار سورة معينة ----
    elif data.startswith("surah_"):
        num = int(data.split("_")[1])
        info = await fetch_surah_info(num)
        if info:
            msg = (
                f"📖 *{info['name']} - {info['englishName']}*\n"
                f"🔢 رقم السورة: {info['number']}\n"
                f"📝 عدد الآيات: {info['numberOfAyahs']}\n"
                f"📍 النوع: {info['revelationType']}\n\n"
                f"اختر ما تريد:"
            )
        else:
            # بيانات احتياطية
            msg = f"📖 سورة {SURAH_NAMES['ar'][num-1]}\n\nاختر ما تريد:"
        
        await query.edit_message_text(
            msg,
            reply_markup=surah_action_keyboard(num),
            parse_mode="Markdown",
        )

    # ---- قراءة النص ----
    elif data.startswith("read_"):
        num = int(data.split("_")[1])
        await query.edit_message_text(
            f"⏳ جاري تحميل سورة {SURAH_NAMES['ar'][num-1]}...\n"
            f"يرجى الانتظار قليلاً."
        )
        
        result = await fetch_ayahs_paginated(num, 0, 10)
        if result and result["verses"]:
            text = f"📖 *سورة {SURAH_NAMES['ar'][num-1]}*\n\n"
            for v in result["verses"]:
                text += f"{v['number']}. {v['text']}\n"
            
            total_pages = (result["total"] + 9) // 10
            await query.edit_message_text(
                text,
                reply_markup=reading_pagination_keyboard(num, 0, total_pages),
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text(
                "❌ تعذر تحميل النص. قد يكون هناك مشكلة في الاتصال.\n"
                "حاول مرة أخرى لاحقاً.",
                reply_markup=surah_action_keyboard(num),
            )

    # ---- التصفح بين صفحات الآيات ----
    elif data.startswith("read_page_"):
        parts = data.split("_")
        num = int(parts[2])
        page = int(parts[3])
        
        result = await fetch_ayahs_paginated(num, page, 10)
        if result and result["verses"]:
            text = f"📖 *سورة {SURAH_NAMES['ar'][num-1]}*\n\n"
            for v in result["verses"]:
                text += f"{v['number']}. {v['text']}\n"
            
            total_pages = (result["total"] + 9) // 10
            await query.edit_message_text(
                text,
                reply_markup=reading_pagination_keyboard(num, page, total_pages),
                parse_mode="Markdown",
            )

    # ---- تشغيل الصوت ----
    elif data.startswith("play_"):
        num = int(data.split("_")[1])
        reciter_id = user_data["reciter"]
        
        # البحث عن اسم القارئ
        reciter_name = reciter_id
        for r in RECITERS:
            if r["id"] == reciter_id:
                reciter_name = r["name"]
                break
        
        audio_url = await fetch_audio_url(num, reciter_id)
        if audio_url:
            await query.edit_message_text(
                f"🎧 *تشغيل سورة {SURAH_NAMES['ar'][num-1]}*\n"
                f"القارئ: {reciter_name}\n\n"
                f"⏳ جاري تحميل الصوت...",
                parse_mode="Markdown",
            )
            # إرسال الملف الصوتي
            await query.message.reply_audio(
                audio=audio_url,
                title=f"سورة {SURAH_NAMES['ar'][num-1]}",
                performer=reciter_name,
                caption=f"🎧 تلاوة سورة {SURAH_NAMES['ar'][num-1]}",
            )
        else:
            await query.edit_message_text(
                "❌ تعذر تحميل الصوت. تأكد من اختيار قارئ صحيح.\n"
                "يمكنك تغيير القارئ من الإعدادات المتقدمة.",
                reply_markup=surah_action_keyboard(num),
            )

    # ---- سورة عشوائية ----
    elif data == "random_surah":
        num = random.randint(1, 114)
        surah_name = SURAH_NAMES["ar"][num - 1]
        
        result = await fetch_ayahs_paginated(num, 0, 5)
        if result and result["verses"]:
            text = f"🎲 *سورة عشوائية:* {surah_name}\n\n"
            for v in result["verses"]:
                text += f"{v['number']}. {v['text']}\n"
            text += "\n..."
            
            await query.edit_message_text(
                text,
                reply_markup=surah_action_keyboard(num),
                parse_mode="Markdown",
            )
        else:
            await query.edit_message_text(
                f"🎲 سورة عشوائية: *{surah_name}*\n\n"
                f"تعذر تحميل النص.",
                reply_markup=surah_action_keyboard(num),
                parse_mode="Markdown",
            )

    # ---- تغيير اللغة ----
    elif data == "change_lang":
        await query.edit_message_text(
            "🌐 اختر اللغة المفضلة:",
            reply_markup=lang_keyboard(),
        )

    # ---- اختيار لغة ----
    elif data.startswith("lang_"):
        code = data.split("_")[1]
        user_data["lang"] = code
        lang_name = {"ar": "العربية", "en": "English", "fr": "Français",
                     "tr": "Türkçe", "ur": "اردو", "id": "Indonesia"}.get(code, code)
        await query.edit_message_text(
            f"✅ تم تغيير اللغة إلى {lang_name}",
            reply_markup=main_menu(code),
        )

    # ---- الإعدادات المتقدمة ----
    elif data == "advanced_settings":
        reciter_name = user_data["reciter"]
        for r in RECITERS:
            if r["id"] == user_data["reciter"]:
                reciter_name = r["name"]
                break
        
        msg = (
            "⚙️ *الإعدادات المتقدمة*\n\n"
            f"🎙️ القارئ الحالي: `{reciter_name}`\n"
            f"📖 القراءة الحالية: `{user_data['qiraa']}`\n\n"
            "اختر الإعداد الذي تريد تعديله:"
        )
        await query.edit_message_text(
            msg,
            reply_markup=advanced_settings_keyboard(),
            parse_mode="Markdown",
        )

    # ---- اختيار القارئ ----
    elif data == "choose_reciter":
        await query.edit_message_text(
            "🎙️ *اختر القارئ:*\n"
            "اختر من بين أكثر من 60 قارئاً:\n"
            "✅ = القارئ المختار حالياً",
            reply_markup=reciters_keyboard(0, user_data["reciter"]),
            parse_mode="Markdown",
        )

    # ---- تصفح القراء ----
    elif data.startswith("reciter_page_"):
        page = int(data.split("_")[2])
        await query.edit_message_text(
            "🎙️ اختر القارئ:",
            reply_markup=reciters_keyboard(page, user_data["reciter"]),
        )

    # ---- اختيار قارئ ----
    elif data.startswith("reciter_"):
        reciter_id = data.split("_", 1)[1]  # reciter_XXXXX
        user_data["reciter"] = reciter_id
        
        # البحث عن اسم القارئ
        reciter_name = reciter_id
        for r in RECITERS:
            if r["id"] == reciter_id:
                reciter_name = r["name"]
                break
        
        await query.edit_message_text(
            f"✅ تم اختيار القارئ:\n{reciter_name}\n\n"
            "يمكنك الآن العودة واختيار سورة للاستماع.",
            reply_markup=advanced_settings_keyboard(),
        )

    # ---- اختيار القراءات العشر ----
    elif data == "choose_qiraat":
        await query.edit_message_text(
            "📖 *القراءات العشر:*\n"
            "اختر رواية القرآن:\n"
            "✅ = المختار حالياً",
            reply_markup=qiraat_keyboard(user_data["qiraa"]),
            parse_mode="Markdown",
        )

    # ---- اختيار رواية ----
    elif data.startswith("qiraa_"):
        qiraa_id = data.split("_", 1)[1]
        user_data["qiraa"] = qiraa_id
        
        qiraa_name = qiraa_id
        for q in QIRAAT:
            if q["id"] == qiraa_id:
                qiraa_name = q["name"]
                break
        
        await query.edit_message_text(
            f"✅ تم اختيار: {qiraa_name}",
            reply_markup=advanced_settings_keyboard(),
        )

    # ---- أذكار الصباح ----
    elif data == "morning_adhkar":
        total = len(MORNING_ADHKAR)
        await query.edit_message_text(
            f"📿 *أذكار الصباح*\n"
            f"إجمالي {total} ذكراً\n\n"
            "اختر الذكر لقراءته 👇",
            reply_markup=adhkar_keyboard(0),
            parse_mode="Markdown",
        )

    # ---- تصفح الأذكار ----
    elif data.startswith("adhkar_page_"):
        page = int(data.split("_")[2])
        await query.edit_message_text(
            "📿 أذكار الصباح:",
            reply_markup=adhkar_keyboard(page),
        )

    # ---- اختيار ذكر معين ----
    elif data.startswith("dhikr_"):
        idx = int(data.split("_")[1])
        if 0 <= idx < len(MORNING_ADHKAR):
            dhikr = MORNING_ADHKAR[idx]
            text = f"📿 *الذكر:*\n\n{dhikr['text']}\n\n📖 *المصدر:* {dhikr['reference']}"
            
            keyboard = [[InlineKeyboardButton("🔙 رجوع للأذكار", callback_data="morning_adhkar")]]
            
            # إذا وجد رابط صوتي
            if dhikr.get("audio_url"):
                keyboard.insert(0, [
                    InlineKeyboardButton("🎧 استماع", url=dhikr["audio_url"])
                ])
            
            keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
            
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

    # ---- فضل قراءة القرآن ----
    elif data == "virtues":
        await query.edit_message_text(
            "✨ *فضل قراءة القرآن الكريم:*\n\n"
            f"{VIRTUES[0]['text']}",
            reply_markup=virtues_keyboard(0),
            parse_mode="Markdown",
        )

    # ---- تصفح الفضائل ----
    elif data.startswith("virtue_page_"):
        page = int(data.split("_")[2])
        if 0 <= page < len(VIRTUES):
            virtue = VIRTUES[page]
            await query.edit_message_text(
                f"✨ *{virtue['title']}:*\n\n{virtue['text']}",
                reply_markup=virtues_keyboard(page),
                parse_mode="Markdown",
            )

    # ---- زر غير معروف ----
    elif data == "noop":
        pass  # زر وهمي

    else:
        await query.edit_message_text(
            "❌ أمر غير معروف. الرجاء استخدام القائمة.",
            reply_markup=main_menu(lang),
        )
#!/usr/bin/env python3
"""
🕌 بوت القرآن الكريم - Quran Bot
Telegram Bot for Quran recitation, reading, Adhkar, and more.
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN
from handlers import start_command, handle_callback, handle_message

# =============== إعدادات السجلات ===============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """تشغيل البوت"""
    if not BOT_TOKEN:
        logger.error("❌ لم يتم العثور على BOT_TOKEN. تأكد من ملف .env")
        return

    logger.info("🚀 جاري تشغيل البوت...")

    # إنشاء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()

    # إضافة المعالجات
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تشغيل البوت
    logger.info("✅ البوت يعمل الآن!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    from telegram import Update
    main()
