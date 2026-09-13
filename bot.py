#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🕌 بوت القرآن الكريم - النسخة الكاملة النهائية
- إصلاح جميع الأخطاء
- دعم السور الطويلة (البقرة، آل عمران...)
- إرسال كـ audio أو document تلقائياً
- خطة بديلة بروابط مباشرة عند فشل الإرسال
"""

import os
import random
import logging
from typing import Optional, Dict, Any, List

import httpx
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ============================================================
#                         الإعدادات
# ============================================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN غير موجود في ملف .env")

CHANNEL_USERNAME = "@x7oly"
CHANNEL_LINK = "https://t.me/x7oly"

DEFAULT_LANGUAGE = "ar"

LANGUAGES = {
    "ar": "🇸🇦 العربية",
    "en": "🇬🇧 English",
    "fr": "🇫🇷 Français",
    "tr": "🇹🇷 Türkçe",
    "ur": "🇵🇰 اردو",
    "id": "🇮🇩 Indonesia",
}

BASE_URL = "https://api.alquran.cloud/v1"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ============================================================
#                        البيانات
# ============================================================

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

# قائمة القراء (21 قارئ فعلي مدعوم في api.alquran.cloud)
RECITERS: List[Dict[str, str]] = [
    {"id": "ar.alafasy",              "name": "مشاري العفاسي"},
    {"id": "ar.abdulbasitmurattal",   "name": "عبد الباسط عبد الصمد (مرتل)"},
    {"id": "ar.abdurrahmaansudais",   "name": "عبد الرحمن السديس"},
    {"id": "ar.saoodshuraym",         "name": "سعود الشريم"},
    {"id": "ar.mahermuaiqly",         "name": "ماهر المعيقلي"},
    {"id": "ar.husary",               "name": "محمود خليل الحصري"},
    {"id": "ar.husarymujawwad",       "name": "محمود خليل الحصري (مجود)"},
    {"id": "ar.minshawi",             "name": "محمد صديق المنشاوي"},
    {"id": "ar.minshawimujawwad",     "name": "محمد صديق المنشاوي (مجود)"},
    {"id": "ar.hudhaify",             "name": "علي الحذيفي"},
    {"id": "ar.muhammadayyoub",       "name": "محمد أيوب"},
    {"id": "ar.muhammadjibreel",      "name": "محمد جبريل"},
    {"id": "ar.ahmedajamy",           "name": "أحمد بن علي العجمي"},
    {"id": "ar.hanirifai",            "name": "هاني الرفاعي"},
    {"id": "ar.qatami",               "name": "ناصر القطامي"},
    {"id": "ar.abdullahbasfar",       "name": "عبد الله باسفر"},
    {"id": "ar.ibrahimakhbar",        "name": "إبراهيم الأخضر"},
    {"id": "ar.aymanswoaid",          "name": "أيمن سويد"},
    {"id": "ar.abdulsamad",           "name": "عبد الباسط (مجود)"},
    {"id": "ar.shaatree",             "name": "أبو بكر الشاطري"},
    {"id": "ar.parhizgar",            "name": "پرهيزگار"},
]

# ربط القارئ بـ CDN لتشغيل السورة كاملة (mp3quran.net)
RECITER_CDN: Dict[str, str] = {
    "ar.alafasy":            "https://server8.mp3quran.net/afs/",
    "ar.abdulbasitmurattal": "https://server7.mp3quran.net/basit/",
    "ar.abdurrahmaansudais": "https://server11.mp3quran.net/sds/",
    "ar.saoodshuraym":       "https://server7.mp3quran.net/shur/",
    "ar.mahermuaiqly":       "https://server12.mp3quran.net/maher/",
    "ar.husary":             "https://server13.mp3quran.net/husr/",
    "ar.minshawi":           "https://server10.mp3quran.net/minsh/",
    "ar.hudhaify":           "https://server9.mp3quran.net/hthfi/",
    "ar.muhammadayyoub":     "https://server8.mp3quran.net/ayyub/",
    "ar.muhammadjibreel":    "https://server8.mp3quran.net/jbrl/",
    "ar.ahmedajamy":         "https://server10.mp3quran.net/ajm/",
    "ar.hanirifai":          "https://server8.mp3quran.net/rifai/",
    "ar.qatami":             "https://server6.mp3quran.net/qtm/",
    "ar.abdullahbasfar":     "https://server6.mp3quran.net/bsfr/",
    "ar.aymanswoaid":        "https://server8.mp3quran.net/swoaid/",
}

# السور الطويلة التي نرسلها كـ document تجنّباً لمشكلة حجم الـ audio
LONG_SURAHS = {
    2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 20, 23,
    26, 27, 28, 29, 30, 31, 33, 34, 35, 36, 37, 38, 39, 40,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
    56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
    71, 72, 73, 74, 75, 76, 77, 78, 79,
}

# أذكار الصباح
MORNING_ADHKAR: List[Dict[str, str]] = [
    {"text": "اللَّهُ لاَ إِلَهَ إِلاَّ هُوَ الْحَيُّ الْقَيُّومُ... آية الكرسي",
     "reference": "سورة البقرة - الآية 255"},
    {"text": "أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ",
     "reference": "قراءة المعوذات (الإخلاص - الفلق - الناس) 3 مرات"},
    {"text": "أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ وَالْحَمْدُ لِلَّهِ لاَ إِلَهَ إِلاَّ اللَّهُ وَحْدَهُ لاَ شَرِيكَ لَهُ",
     "reference": "أذكار الصباح"},
    {"text": "اللَّهُمَّ بِكَ أَصْبَحْنَا وَبِكَ أَمْسَيْنَا وَبِكَ نَحْيَا وَبِكَ نَمُوتُ وَإِلَيْكَ الْمَصِيرُ",
     "reference": "أذكار الصباح"},
    {"text": "اللَّهُمَّ أَنْتَ رَبِّي لاَ إِلَهَ إِلاَّ أَنْتَ خَلَقْتَنِي وَأَنَا عَبْدُكَ...",
     "reference": "سيد الاستغفار"},
    {"text": "اللَّهُمَّ إِنِّي أَصْبَحْتُ أُشْهِدُكَ وَأُشْهِدُ حَمَلَةَ عَرْشِكَ وَمَلاَئِكَتَكَ وَجَمِيعَ خَلْقِكَ أَنَّكَ أَنْتَ اللَّهُ لاَ إِلَهَ إِلاَّ أَنْتَ وَأَنَّ مُحَمَّدًا عَبْدُكَ وَرَسُولُكَ",
     "reference": "أذكار الصباح (4 مرات)"},
    {"text": "اللَّهُمَّ مَا أَصْبَحَ بِي مِنْ نِعْمَةٍ أَوْ بِأَحَدٍ مِنْ خَلْقِكَ فَمِنْكَ وَحْدَكَ لاَ شَرِيكَ لَكَ فَلَكَ الْحَمْدُ وَلَكَ الشُّكْرُ",
     "reference": "أذكار الصباح"},
    {"text": "اللَّهُمَّ عَافِنِي فِي بَدَنِي، اللَّهُمَّ عَافِنِي فِي سَمْعِي، اللَّهُمَّ عَافِنِي فِي بَصَرِي، لاَ إِلَهَ إِلاَّ أَنْتَ",
     "reference": "أذكار الصباح (3 مرات)"},
    {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ وَعَذَابِ الْقَبْرِ",
     "reference": "أذكار الصباح"},
    {"text": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ: عَدَدَ خَلْقِهِ وَرِضَا نَفْسِهِ وَزِنَةَ عَرْشِهِ وَمِدَادَ كَلِمَاتِهِ",
     "reference": "أذكار الصباح (3 مرات)"},
    {"text": "سُبْحَانَ اللَّهِ الْعَظِيمِ وَبِحَمْدِهِ",
     "reference": "أذكار الصباح (100 مرة)"},
    {"text": "لَا إِلَهَ إِلَّا اللَّهُ وَحْدَهُ لَا شَرِيكَ لَهُ، لَهُ الْمُلْكُ وَلَهُ الْحَمْدُ وَهُوَ عَلَى كُلِّ شَيْءٍ قَدِيرٌ",
     "reference": "أذكار الصباح (10 مرات)"},
    {"text": "بِسْمِ اللَّهِ الَّذِي لاَ يَضُرُّ مَعَ اسْمِهِ شَيْءٌ فِي الأَرْضِ وَلاَ فِي السَّمَاءِ وَهُوَ السَّمِيعُ الْعَلِيمُ",
     "reference": "أذكار الصباح (3 مرات)"},
    {"text": "رَضِيتُ بِاللَّهِ رَبًّا، وَبِالإِسْلاَمِ دِينًا، وَبِمُحَمَّدٍ ﷺ نَبِيًّا",
     "reference": "أذكار الصباح (3 مرات)"},
    {"text": "يَا حَيُّ يَا قَيُّومُ بِرَحْمَتِكَ أَسْتَغِيثُ أَصْلِحْ لِي شَأْنِي كُلَّهُ وَلاَ تَكِلْنِي إِلَى نَفْسِي طَرْفَةَ عَيْنٍ",
     "reference": "أذكار الصباح"},
    {"text": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ وَالْعَجْزِ وَالْكَسَلِ وَالْجُبْنِ وَالْبُخْلِ وَضَلَعِ الدَّيْنِ وَغَلَبَةِ الرِّجَالِ",
     "reference": "أذكار الصباح"},
]

VIRTUES: List[Dict[str, str]] = [
    {"title": "✨ فضل قراءة القرآن",
     "text": "قال الله تعالى:\n﴿إِنَّ الَّذِينَ يَتْلُونَ كِتَابَ اللَّهِ وَأَقَامُوا الصَّلَاةَ وَأَنفَقُوا مِمَّا رَزَقْنَاهُمْ سِرًّا وَعَلَانِيَةً يَرْجُونَ تِجَارَةً لَّن تَبُورَ﴾\n[فاطر: 29]"},
    {"title": "🌙 حديث شريف",
     "text": "قال رسول الله ﷺ:\n«اقْرَؤُوا الْقُرْآنَ فَإِنَّهُ يَأْتِي يَوْمَ الْقِيَامَةِ شَفِيعًا لِأَصْحَابِهِ»\n[رواه مسلم]"},
    {"title": "📖 حديث شريف",
     "text": "قال رسول الله ﷺ:\n«خَيْرُكُمْ مَنْ تَعَلَّمَ الْقُرْآنَ وَعَلَّمَهُ»\n[رواه البخاري]"},
    {"title": "💎 حديث شريف",
     "text": "قال رسول الله ﷺ:\n«مَنْ قَرَأَ حَرْفًا مِنْ كِتَابِ اللَّهِ فَلَهُ بِهِ حَسَنَةٌ، وَالْحَسَنَةُ بِعَشْرِ أَمْثَالِهَا، لَا أَقُولُ الم حَرْفٌ، وَلَكِنْ أَلِفٌ حَرْفٌ وَلَامٌ حَرْفٌ وَمِيمٌ حَرْفٌ»\n[رواه الترمذي]"},
    {"title": "🌟 حديث شريف",
     "text": "قال رسول الله ﷺ:\n«يُقَالُ لِصَاحِبِ الْقُرْآنِ: اقْرَأْ وَارْتَقِ وَرَتِّلْ كَمَا كُنْتَ تُرَتِّلُ فِي الدُّنْيَا، فَإِنَّ مَنْزِلَكَ عِنْدَ آخِرِ آيَةٍ تَقْرَؤُهَا»\n[رواه أبو داود والترمذي]"},
    {"title": "🌿 حديث شريف",
     "text": "قال رسول الله ﷺ:\n«مَثَلُ الْمُؤْمِنِ الَّذِي يَقْرَأُ الْقُرْآنَ مَثَلُ الْأُتْرُجَّةِ، رِيحُهَا طَيِّبٌ وَطَعْمُهَا طَيِّبٌ»\n[رواه البخاري ومسلم]"},
    {"title": "🤲 دعاء ختم القرآن",
     "text": "اللَّهُمَّ ارْحَمْنِي بِالْقُرْآنِ الْعَظِيمِ، وَاجْعَلْهُ لِي إِمَامًا وَنُورًا وَهُدًى وَرَحْمَةً، اللَّهُمَّ ذَكِّرْنِي مِنْهُ مَا نَسِيتُ وَعَلِّمْنِي مِنْهُ مَا جَهِلْتُ وَارْزُقْنِي تِلَاوَتَهُ آنَاءَ اللَّيْلِ وَأَطْرَافَ النَّهَارِ، وَاجْعَلْهُ لِي حُجَّةً يَا رَبَّ الْعَالَمِينَ"},
]

# ============================================================
#                     عميل الـ API + Cache
# ============================================================

_surah_cache: Dict[int, Dict[str, Any]] = {}


async def _fetch_surah_raw(surah_number: int) -> Optional[Dict[str, Any]]:
    """جلب بيانات السورة كاملة من API مع cache."""
    if surah_number in _surah_cache:
        return _surah_cache[surah_number]

    url = f"{BASE_URL}/surah/{surah_number}"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("code") != 200:
                return None
            _surah_cache[surah_number] = data["data"]
            return data["data"]
    except (httpx.TimeoutException, httpx.RequestError) as e:
        logger.warning(f"⚠️ فشل الاتصال بـ API: {e}")
        return None


async def fetch_surah_info(surah_number: int) -> Optional[Dict[str, Any]]:
    surah = await _fetch_surah_raw(surah_number)
    if not surah:
        return None
    return {
        "number": surah["number"],
        "name": surah["name"],
        "englishName": surah["englishName"],
        "revelationType": surah["revelationType"],
        "numberOfAyahs": surah["numberOfAyahs"],
    }


async def fetch_ayahs_paginated(
    surah_number: int, page: int = 0, page_size: int = 10
) -> Optional[Dict[str, Any]]:
    surah = await _fetch_surah_raw(surah_number)
    if not surah:
        return None

    ayahs = surah.get("ayahs", [])
    total = len(ayahs)
    start = page * page_size
    end = min(start + page_size, total)

    verses = []
    for i in range(start, end):
        a = ayahs[i]
        verses.append({
            "number": i + 1,
            "text": a.get("text", ""),
        })

    return {
        "verses": verses,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


def get_surah_audio_url(surah_number: int, reciter_id: str) -> Optional[str]:
    """رابط صوت السورة كاملة من mp3quran CDN."""
    base = RECITER_CDN.get(reciter_id)
    if not base:
        return None
    return f"{base}{surah_number:03d}.mp3"


# ============================================================
#                    تخزين بيانات المستخدم
# ============================================================

user_data_store: Dict[int, Dict[str, Any]] = {}


def get_user_data(user_id: int) -> Dict[str, Any]:
    if user_id not in user_data_store:
        user_data_store[user_id] = {
            "lang": DEFAULT_LANGUAGE,
            "reciter": RECITERS[0]["id"],
        }
    return user_data_store[user_id]


# ============================================================
#                         الكيبوردات
# ============================================================

def main_menu(lang: str = "ar") -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📖 المصحف للقراءة", callback_data="read_quran")],
        [InlineKeyboardButton("🎲 سورة عشوائية", callback_data="random_surah")],
        [InlineKeyboardButton("🌐 تغيير اللغة", callback_data="change_lang")],
        [InlineKeyboardButton("🎙️ اختيار القارئ", callback_data="choose_reciter")],
        [InlineKeyboardButton("📿 أذكار الصباح", callback_data="morning_adhkar")],
        [InlineKeyboardButton("✨ فضل قراءة القرآن", callback_data="virtues")],
        [InlineKeyboardButton("📢 قناة البوت", url=CHANNEL_LINK)],
    ]
    return InlineKeyboardMarkup(keyboard)


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
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"slist_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"slist_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def surah_action_keyboard(surah_number: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📖 قراءة النص", callback_data=f"read_{surah_number}_0")],
        [InlineKeyboardButton("🎧 استماع", callback_data=f"play_{surah_number}")],
        [InlineKeyboardButton("⬇️ تحميل MP3", callback_data=f"dl_{surah_number}")],
        [InlineKeyboardButton("🔙 رجوع للسور", callback_data="read_quran")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def reciters_keyboard(page: int = 0, selected: str = "") -> InlineKeyboardMarkup:
    page_size = 8
    start = page * page_size
    end = min(start + page_size, len(RECITERS))

    keyboard = []
    for i in range(start, end):
        reciter = RECITERS[i]
        mark = "✅ " if reciter["id"] == selected else ""
        keyboard.append([
            InlineKeyboardButton(
                f"{mark}{reciter['name']}",
                callback_data=f"setrec_{reciter['id']}",
            )
        ])

    nav_buttons = []
    total_pages = (len(RECITERS) + page_size - 1) // page_size
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"rlist_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"rlist_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def lang_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for code, name in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"lang_{code}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def adhkar_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    page_size = 5
    total = len(MORNING_ADHKAR)
    total_pages = (total + page_size - 1) // page_size

    keyboard = []
    start = page * page_size
    end = min(start + page_size, total)

    for i in range(start, end):
        dhikr = MORNING_ADHKAR[i]
        preview = dhikr["text"][:28] + "..." if len(dhikr["text"]) > 28 else dhikr["text"]
        keyboard.append([
            InlineKeyboardButton(f"📿 {preview}", callback_data=f"dhikr_{i}")
        ])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"alist_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"alist_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def virtues_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    total = len(VIRTUES)
    keyboard = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"vlist_{page-1}"))
    if page < total - 1:
        nav_buttons.append(InlineKeyboardButton("التالي ➡️", callback_data=f"vlist_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def reading_pagination_keyboard(
    surah_number: int, page: int, total_pages: int
) -> InlineKeyboardMarkup:
    keyboard = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"read_{surah_number}_{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"read_{surah_number}_{page+1}"))
    keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🎧 استماع", callback_data=f"play_{surah_number}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع للسور", callback_data="read_quran")])
    keyboard.append([InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)


def audio_fallback_keyboard(surah_number: int, audio_url: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⬇️ تحميل السورة (رابط مباشر)", url=audio_url)],
        [InlineKeyboardButton("🎙️ تغيير القارئ", callback_data="choose_reciter")],
        [InlineKeyboardButton("🔙 رجوع للسور", callback_data="read_quran")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ============================================================
#                        المعالجات
# ============================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = get_user_data(user.id)

    welcome_text = (
        f"🌙 *بسم الله الرحمن الرحيم*\n\n"
        f"أهلاً بك يا {user.first_name} في بوت القرآن الكريم 🕌\n\n"
        f"هذا البوت مخصص لتلاوة وقراءة القرآن الكريم، والأذكار، والفضائل.\n"
        f"اختر ما تريد من القائمة أدناه 👇\n\n"
        f"📢 قناة البوت: {CHANNEL_LINK}"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=main_menu(user_data["lang"]),
        parse_mode=ParseMode.MARKDOWN,
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = get_user_data(update.effective_user.id)
    await update.message.reply_text(
        "🕌 استخدم الأزرار للتنقل في القائمة.",
        reply_markup=main_menu(user_data["lang"]),
    )


async def send_audio_smart(query, surah_number: int, user_data: Dict[str, Any]):
    """
    إرسال الصوت بطريقة ذكية:
    - السور الطويلة → document (يدعم حتى 2GB)
    - السور القصيرة → audio عادي
    - عند الفشل → رابط تحميل مباشر
    """
    reciter_id = user_data["reciter"]
    reciter_name = reciter_id
    for r in RECITERS:
        if r["id"] == reciter_id:
            reciter_name = r["name"]
            break

    audio_url = get_surah_audio_url(surah_number, reciter_id)
    surah_name = SURAH_NAMES["ar"][surah_number - 1]

    if not audio_url:
        await query.edit_message_text(
            f"❌ القارئ *{reciter_name}* غير متوفر للاستماع حالياً.\n"
            f"جرّب قارئاً آخر من قائمة القراء.",
            reply_markup=surah_action_keyboard(surah_number),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    await query.edit_message_text
