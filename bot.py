"""
Highrise Universal Bot
Eğlenceli, bol emote'lu, gerçekçi sohbetçi, zeki bir oda botu.
Her odada çalışır. 
"""
import asyncio
import os
import random
import time
import re
import json
from pathlib import Path
from typing import Optional

import urllib.request
import urllib.error
import urllib.parse

from highrise import BaseBot, User, Position, CurrencyItem
from highrise.__main__ import main as highrise_main, BotDefinition

# ============================================================
# AYARLAR (ODA ID VE BOT TOKEN BURAYA YAZILACAK)
# ============================================================
ROOM_ID   = "63426d9705502b97912cc73b" # LÜTFEN KENDİ ODA ID'Nİ BURAYA YAZ
BOT_TOKEN = "d6e81c18efdaf8b1a82940fc16028009f45fe8f8df8119e3fc863b43d1e350ee" # LÜTFEN KENDİ BOT TOKEN'INI BURAYA YAZ
ROOM_NAME = ""

# JSON dosyaları her zaman bot klasöründe saklanır — ortam sıfırlansa da kaybolmaz
_BOT_DIR     = Path(__file__).parent
DB_FILE      = _BOT_DIR / "users_db.json"
PENDING_FILE = _BOT_DIR / "pending_users.json"
DB_BACKUP    = _BOT_DIR / "users_db.backup.json"
PENDING_BACKUP = _BOT_DIR / "pending_users.backup.json"

# ============================================================
CMD_PREFIX        = "!"
USER_COOLDOWN     = 3
GLOBAL_CHAT_COOL  = 3.0   # Highrise rate-limit için güvenli aralık (sn)
IDLE_EMOTE_MIN    = 90
IDLE_EMOTE_MAX    = 220
IDLE_CHAT_MIN     = 10800
IDLE_CHAT_MAX     = 21600
IDLE_INACTIVITY   = 1200
MAX_MSG_LEN       = 360
CHUNK_DELAY       = 1.0   # Çok parçalı mesajlar arası bekleme

# <#RRGGBB> FORMATINDA RENK KODLARI
HEX_COLORS = {
    "red": "#FF0000",
    "blue": "#0055FF",
    "green": "#00AA00",
    "purple": "#8A2BE2",
    "orange": "#FF8C00",
    "yellow": "#FFD700",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "pink": "#FF69B4",
    "lime": "#32CD32",
    "aqua": "#00FFFF"
}
COLORS = list(HEX_COLORS.values())

# ============================================================
# TEMA RENKLERİ — Her mesaj türünün sabit rengi
# ============================================================
C_JOIN    = "lime"      # Odaya giriş
C_LEAVE   = "orange"    # Odadan çıkış
C_IDLE    = "cyan"      # Boş oda sohbeti
C_SOLO    = "aqua"      # Kendi kendine konuşma
C_JOKE    = "yellow"    # Şaka
C_FACT    = "aqua"      # Bilgi bombası
C_QUOTE   = "yellow"    # Alıntı/söz
C_QUIZ    = "purple"    # Quiz
C_BATTLE  = "red"       # Battle
C_FORTUNE = "magenta"   # Fal
C_LOVE    = "pink"      # Aşk
C_GAME    = "lime"      # Oyunlar (çark, zar, yt)
C_CMD     = "cyan"      # Genel komut yanıtı
C_WARN    = "orange"    # Uyarı / bilinmeyen komut
C_MUSIC   = "magenta"   # Müzik vibe
C_MOOD    = "blue"      # Duygu durumu
C_CHAT    = "cyan"      # Sohbet trigger yanıtları
C_STAT    = "cyan"      # İstatistik
C_INVITE  = "lime"      # Davet
C_GREET   = "lime"      # Başlangıç selamı

BOT_ADI = "Bot"

# Admin kullanıcı adı — bu kişi tüm özel komutlara erişebilir
ADMIN_USERNAME = "GeceMavisi0"

# Başlangıç selamlaması bir kez gönderilsin (yeniden bağlanmalarda tekrarlanmasın)
_bot_greeted_once = False

# ============================================================
# EMOTE TABLOSU
# ============================================================
NUMBERED: dict[int, str] = {
    1:   "emote-wave",
    2:   "emote-hello",
    3:   "emote-yes",
    4:   "emote-bow",
    5:   "emote-curtsy",
    6:   "emote-saluting",
    7:   "emote-cutesalute",
    8:   "emote-thumbsup",
    9:   "emote-celebrate",
    10:  "emote-cutey",
    11:  "emote-no",
    12:  "emote-shy",
    13:  "emote-laughing",
    14:  "emote-laughing2",
    15:  "emote-sad",
    16:  "emote-angry",
    17:  "emote-confused",
    18:  "emote-think",
    19:  "emote-tired",
    20:  "emote-cute",
    21:  "emote-frustrated",
    22:  "emote-greedy",
    23:  "emote-maniac",
    24:  "emote-frog",
    25:  "emote-creepycute",
    26:  "emote-kiss",
    27:  "emote-jumpb",
    28:  "emote-flexing",
    29:  "emote-model",
    30:  "emote-superpose",
    31:  "emote-boxer",
    32:  "emote-snake",
    33:  "emote-handstand",
    34:  "emote-deathdrop",
    35:  "emote-swordfight",
    36:  "emote-charging",
    37:  "emote-energyball",
    38:  "emote-headblowup",
    39:  "emote-secrethandshake",
    40:  "emote-telekinesis",
    41:  "emote-float",
    42:  "emote-teleporting",
    43:  "emote-gravity",
    44:  "emote-snowball",
    45:  "emote-snowangel",
    46:  "emote-hot",
    47:  "emote-zombierun",
    48:  "emote-celebrationstep",
    49:  "emote-disco",
    50:  "emote-fashionista",
    51:  "emote-pose1",
    52:  "emote-pose3",
    53:  "emote-pose5",
    54:  "emote-pose7",
    55:  "emote-pose8",
    56:  "dance-tiktok2",
    57:  "dance-tiktok8",
    58:  "dance-tiktok9",
    59:  "dance-tiktok10",
    60:  "dance-blackpink",
    61:  "dance-pennywise",
    62:  "dance-russian",
    63:  "dance-shoppingcart",
    64:  "dance-zombie",
    65:  "dance-macarena",
    66:  "dance-icecream",
    67:  "dance-wrong",
    68:  "dance-employee",
    69:  "dance-anime",
    70:  "dance-creepypuppet",
    71:  "idle-dance-tiktok4",
    72:  "idle-dance-casual",
    73:  "idle-loop-sitfloor",
    74:  "idle-loop-shy",
    75:  "idle-loop-happy",
    76:  "idle-loop-sad",
    77:  "idle-uwu",
    78:  "idle-floorsleeping",
    79:  "sit-relaxed",
}

_BASE_POOL = list(NUMBERED.values())
for _n in range(80, 1001):
    NUMBERED[_n] = _BASE_POOL[(_n - 1) % len(_BASE_POOL)]

ALL_EMOTES = list(set(_BASE_POOL))

ALIASES: dict[str, str] = {
    "selam":     "emote-wave",
    "merhaba":   "emote-hello",
    "evet":      "emote-yes",
    "hayır":     "emote-no",
    "utan":      "emote-shy",
    "gül":       "emote-laughing",
    "üzgün":     "emote-sad",
    "kız":       "emote-angry",
    "şaşkın":    "emote-confused",
    "düşün":     "emote-think",
    "yorgun":    "emote-tired",
    "tatlı":     "emote-cute",
    "alkış":     "emote-celebrate",
    "beğen":     "emote-thumbsup",
    "eğil":      "emote-bow",
    "öp":        "emote-kiss",
    "kalp":      "emote-kiss",
    "model":     "emote-model",
    "kas":       "emote-flexing",
    "zıpla":     "emote-jumpb",
    "süper":     "emote-superpose",
    "boks":      "emote-boxer",
    "uç":        "emote-float",
    "büyü":      "emote-telekinesis",
    "otur":      "sit-relaxed",
    "uyu":       "idle-floorsleeping",
    "mutlu":     "idle-loop-happy",
    "uwu":       "idle-uwu",
    "tiktok":    "dance-tiktok2",
    "blackpink": "dance-blackpink",
    "macarena":  "dance-macarena",
    "anime":     "dance-anime",
    "zombi":     "dance-zombie",
    "rus":       "dance-russian",
    "dondurma":  "dance-icecream",
    "dans":      "dance-tiktok2",
    "disco":     "emote-disco",
    "enerji":    "emote-energyball",
    "yılan":     "emote-snake",
    "kartopu":   "emote-snowball",
    "kar":       "emote-snowangel",
    "zombikoş":  "emote-zombierun",
    "uçuş":      "emote-float",
    "poz":       "emote-pose1",
    "manken":    "emote-fashionista",
    "egzersiz":  "emote-flexing",
    "parti":     "emote-celebrationstep",
}

# ============================================================
# MESAJlar — Karşılama & Vedalar
# ============================================================
GREETINGS = [
    "Heyyy {name}! Hoş geldin 👋",
    "{name} geldi! Hadi eğlenelim 🎉",
    "Selam {name}! Nasılsın? ✨",
    "Oo {name}! İyi ki geldin 😍",
    "{name} geldi, ne güzel! 🌟",
    "Hey {name}! Seni görünce sevindim 🤩",
    "Hoş geldin {name}! 😄",
    "{name} hoş geldin! Emote yapalım mı? 💃",
    "Buyur {name}! 🎊",
    "Selam {name}! 👋 Keyifler nasıl?",
    "{name}! Nasılsın kanka? 🙏",
    "Hey hey! {name} geldi 😎",
    "{name} hazır mısın eğlenceye? 🎊",
    "Renk kattın {name}, hoş geldin 🌈",
    "Hayırlısı {name} 😄",
    "{name}! Özledik 🥹",
    "{name} geldi 🎈 Hoş geldin!",
    "Ee {name}! İyi ki geldin 😁",
    "Günaydın {name}! ☀️",
    "{name} seninle daha eğlenceli 💫",
    "Tam zamanında {name}! 🏆",
    "Hey {name}! 😄",
    "Selam {name}! 🥰",
    "{name}! Bekliyorduk 🙌",
    "Buyur {name}! 👑",
]

GOODBYES = []

# ============================================================
# ŞAKALAR — 40 tane
# ============================================================
JOKES = [
    "Arkadaşım 'seninle konuşmak istemiyorum' dedi. Hâlâ konuşuyoruz 😂",
    "Dün gece erken uyudum, sabah erken kalktım. Hiçbir fark yok hayatta 🙃",
    "Biri bana 'başarının sırrı nedir' dedi. Dedim: Google 😂",
    "Diyet yapıyorum diye pizza söyledim, ince hamur aldım 🍕",
    "Sınava çalışacaktım ama telefon orada duruyordu 📱",
    "Annem 'seni anlayan yok mu' dedi. Dedim: sen de yoksun 😅",
    "Sabah 'bugün verimli olacağım' dedim. Akşam oldu, hâlâ düşünüyorum 🤔",
    "Arkadaşım '5 dakikada gelirim' dedi. 2 saat oldu 🕐",
    "Para biriktiriyorum ama bir şeyler de almam lazım... mantıklı 😂",
    "Dedim uyuyacağım, telefona baktım. Saat 03:00 😵",
    "Bugün spor yapacaktım ama ağır bir gündü, yarın 💪",
    "Mesaj attım 'görüldü' geçti. Tamam, iyi günler 🙂",
    "Kahve içmeden insan değilim, içince de sayılmam 😂",
    "Beyin: uyku zamanı. Göz: bi bak ne var. Sonuç: sabah 😅",
    "Yemek sipariş verdim, 'hızlı gelecek' dedi. Yavaş yavaş geldi ama geldi 🍔",
    "Bugün öyle bir şey yaptım ki... sormayın ne yaptım 🤫",
    "Wi-Fi şifresi gibi bazı şeyler var, bilmezsen giremezsin 🔐",
    "Mutlu ol dediler. Tamam dedim. Olmadı ama tamam dedim 😶",
    "Biri 'daha az telefon bak' dedi. Telefonda baktım, haklıymış 📲",
    "Uyku saatim yok, uyku geldiği zaman diyorum 😴",
    "Akıllı telefon, akıllı saat, akıllı TV... bir ben kaldım böyle 🙃",
    "Bugün çok üretken oldum: 3 bölüm dizi izledim 📺",
    "Annem 'hayatta plan yapmak lazım' dedi. Ben de plan yaptım: yok plan 😂",
    "Diyet listesi: sabah yulaf, öğle salata, akşam... pizza 🍕",
    "Sosyal medyada herkese iyi geceler diyorum, kimse 'geç kalma' demiyor 😢",
    "'Hayatın tadını çıkar' dediler. Çıkarmaya çalışıyorum ama biraz tuzlu 😅",
    "Bugün erken kalktım, avantaj yapamazsam da erken kalktım 🌅",
    "Arkadaşım 'seninle selfie çekeyim' dedi. Fotoğrafa bakmadım daha 📸",
    "'Neyin var' dediler. 'Şeyim var' dedim. Şeyim de yok aslında 🤷",
    "Bilgi güçtür. Ama bilmeden de güçlü olunur, deneyin 💪",
    "Beş dakika erken çıkacaktım, beş dakika geç çıktım. Matematik zor 🤓",
    "Biri 'robot gibi hareket ediyorsun' dedi. AI miyim diye düşündüm 🤖",
    "Dün kendimi geliştirdim: yeni bir dizi başlattım 📺 Öğreniyorum.",
    "Kahve bitince hayat durmuyor ama yavaşlıyor ☕",
    "Bugün kendimle barıştım. 10 dakika sonra tartıştım yine 😬",
    "Annem 'git yat' dedi. Ben de gittim, telefonla yattım 📱",
    "Biri 'sabah sporunu yaptın mı' dedi. Yastığa baktım, o baktı, sustuk 🛏️",
    "Arkadaşım iyi haber var dedi. İyi haber şuymuş: kötü haber yok 😂",
    "Gece 12'de 'bir dahaki sefere erken yatarım' dedim. Şu an sabah 4 😵",
    "Özgüven meselesi bu: yanlış bile olsan emin ol 😎",
]

# ============================================================
# FALLAR — 25 tane
# ============================================================
FORTUNES = [
    "Bugün şansın bol, ufak bir sürpriz gelebilir 🍀",
    "Yakında tanıdık biri seni aramak isteyecek 📩",
    "Para işlerine dikkat, küçük bir kazanç görünüyor 💰",
    "Aşk hayatında yeni bir kıvılcım var 💖",
    "Bugün biraz dinlen, yarın daha enerjik olacaksın 😴",
    "Eski bir anı bugün seni güldürecek 🌈",
    "Yıldızlar diyor ki: bugün cesur ol! 🌟",
    "İçindeki ses haklı, ona güven 🔮",
    "Birisi seni düşünüyor, kim olduğunu bilmiyorum ama 🤫",
    "Bu hafta sana güzel bir haber gelecek 📬",
    "Bugün sabırlı ol, karşılığını göreceksin 🧘",
    "Yeni bir başlangıç kapında, korkma aç 🚪",
    "Kalbin sana yol gösteriyor 💭",
    "Bolluk ve bereket kapıda, açık tut 🤲",
    "Bugün bir şey öğreneceksin, gözlerini aç 👁️",
    "Sevdiklerine zaman ayır, pişman olmayacaksın 🫂",
    "Yakında çok güleceğin bir şey olacak 😂",
    "Bugün karşına çıkan kapıyı aç, içi güzel olacak 🚪✨",
    "Biri seni koruyucu melek gibi izliyor, endişelenme 👼",
    "Sabah uyandığında bir şey değişmiş olacak, iyi yönde 🌅",
    "Bugün aldığın karar seni ileriye taşıyacak 🚀",
    "Küçük bir jest büyük bir fark yaratacak yakında 🌸",
    "Yıldızlar seninle bu hafta, akın açık 🌠",
    "Bir iyilik yap, katkat geri gelecek 🔄",
    "Sürpriz bir buluşma ya da haber yolda 📍",
]

# ============================================================
# ALINTLAR — 25 tane
# ============================================================
QUOTES = [
    '"Hayat kısa, emote sayısı sonsuz." 🎭',
    '"Yapamazsın diyenleri yapanlar bozar." 💪',
    '"Hayal et, planla, başla." ✨',
    '"Düşmek değil, kalkmamak ayıp." 🔥',
    '"Gülmek bedavaysa neden herkes üzgün?" 😊',
    '"Başarı sabahları erken kalkmaktır." ☀️',
    '"İyi insan ol, gerisini hayat halleder." 🌿',
    '"Sevgi paylaştıkça çoğalır." 💖',
    '"Küçük adımlar büyük yolculukların başlangıcıdır." 🛤️',
    '"Kendinle barışık ol, dünya zaten yeterince karmaşık." 🕊️',
    '"Mükemmel olmak zorunda değilsin, sadece gerçek ol." 🌸',
    '"Güç dışarıda değil, içindedir." 🔥',
    '"Hayatta en güzel şeyler emote yapılarak yaşanır." 💃',
    '"Her insan bir hikâyedir, onu yargılamadan önce oku." 📖',
    '"Sabır acıdır, meyvesi tatlıdır." 🍑',
    '"Cesaret korkmamak değil, korkana rağmen devam etmektir." 🦁',
    '"Bugünü yaşa, dün geçti yarın henüz gelmedi." 🌤️',
    '"Başkasının hayatını yaşama, kendi oyununu oyna." 🎮',
    '"Başarılı insanlar farklı şeyler yapmaz, şeyleri farklı yapar." 🧠',
    '"Mutluluk bir varış noktası değil, bir yolculuk tarzıdır." 🚶',
    '"Sevilmek değil, sevilmeye layık olmak önemlidir." 💎',
    '"En büyük risk, hiç risk almamaktır." 🎲',
    '"Kendine söylediğin şeyler seni şekillendirir." 🪞',
    '"Her gün yeni bir şans, kaçırma." ⏳',
    '"Gülümsemek en güçlü silahındır." 😊',
]

# ============================================================
# BİLGİ BOMBASI FACTS — 30 tane
# ============================================================
FACTS = [
    "Ahtapotların 3 kalbi vardır 🐙",
    "Bal asla bozulmaz, 3000 yıllık bal yenebilir 🍯",
    "Yunuslar uyurken beyninin yarısı uyanık kalır 🐬",
    "Ay'ın yüzeyinde ses duyulmaz 🌙",
    "İnsan beyni günde ~70.000 düşünce üretir 🧠",
    "Kelebek tadarken ayaklarını kullanır 🦋",
    "Fil tek kara memelisi olarak atlamaz 🐘",
    "Güneş ışığının yere ulaşması 8 dakika sürer ☀️",
    "Kar tanelerinin hepsi altıgen ama hiçbiri aynı değil ❄️",
    "İnsan vücudu yaklaşık 37 trilyon hücreden oluşur 🔬",
    "Küçük kalplere sahip balıklar da var: bazı balıkların kalbi yok 🐟",
    "Devekuşu beyni gözünden küçüktür 🦚",
    "Yıldırım dünyanın her yerine günde 8 milyon kez çarpar ⚡",
    "NASA'nın internet hızı saniyede 91 gigabit 🚀",
    "Parmak izin gibi dil izin de eşsizdir 👅",
    "Deniz atalarında erkek hamile kalır 🐴",
    "Karides kalbi kafasındadır 🦐",
    "Fil korktuğunda da terlediğinde de aynı sesi çıkarır 🐘",
    "Çocukların yetişkinlere göre kemikleri daha fazladır 🦴",
    "Uçakta kullanılan oksijenin tamamı motorlar tarafından üretilir ✈️",
    "Köpekler insan duygularını yüzden okuyabilir 🐕",
    "Bir bulutun ağırlığı ortalama 500 tondur ☁️",
    "Issız bir odada kendi kalp atışını duyabilirsin 💓",
    "Maymunlar muz soyarken aşağıdan soymayı tercih eder 🍌",
    "İlk turuncu rengin adı yoktu, portakal meyvesinden sonra kondu 🍊",
    "Kuzeyde yaşayan ren geyiklerinin gözleri kışın mavi olur 🦌",
    "Bir salyangoz 3 yıl uyuyabilir 🐌",
    "Dünya çevresindeki ışık 1 saniyede 7,5 tur atar 🌍",
    "Kaktüsler yağmur sezonu olmayan yerlerde 200 yıl yaşayabilir 🌵",
    "İnsanlar gülümserken 12, çatarken 11 kas kullanır 😄",
]

# ============================================================
# BOŞ ZAMAN MESAJLARI — 35 tane
# ============================================================
IDLE_PHRASES = [
    "Sessizce bekliyorum, ama buradayım 😊",
    "Nasılsınız? Ben gayet iyiyim 💙",
    "Bir sayı yazın, emote yapayım 🎭",
    "Sıkıldıysanız !dans yazın 💃",
    "Bugün quiz oynamak ister misiniz? !quiz 🧠",
    "Fal baktırmak isteyen? !fal 🔮",
    "Gece mi gündüz mü? Fark etmez, açığım ☀️🌙",
    "Sessizlik güzel ama konuşmak daha güzel 😄",
    "Bir şaka dinlemek ister misiniz? !şaka 😂",
    "Müzik modundayım 🎵 !müzik yazın",
    "Herkes iyidir umarım 💙",
    "Emote numara yazın, hemen yaparım 🎭",
    "!battle ile birine meydan okuyun 🥊",
    "!çark ile kader belirlesin 🎡",
    "Komutları görmek için !yardım yazın 📋",
    "Buradayım, sadece bekliyorum 🤖",
]


# ============================================================
# SOHBET TETİKLEYİCİLERİ — 30+ kategori
# ============================================================
CHAT_TRIGGERS: dict[tuple, list[str]] = {
    ("merhaba", "selam", "slm", "hi", "hello", "hey", "heyy", "heyyy"): [
        "Selam {name}! 👋 Nasılsın bugün?",
        "Heyyy {name}! Uzun zamandır görmemiştim 😄",
        "Merhaba {name}, hoş geldin! Ne yapalım?",
        "Heyyyo {name}! Tam zamanında 😎",
        "Selaam {name}! Keyifler nasıl?",
        "Hey hey hey! {name} yazdı! 👋",
    ],
    ("nasılsın", "nasilsin", "naber", "naparsın", "napıyorsun", "ne yapıyorsun"): [
        "İyiyim {name}, emote yapıyorum zaten 😄 Sen?",
        "Süperim! Seni görünce daha iyi oldum 😎",
        "Lumba gibiyim ama iyiyim, fena sayılmam 🙃",
        "Mükemmelim {name}! Sen nasılsın daha önemli?",
        "Eh şöyle böyle... ama sen yazınca canlandım! 😁",
        "Biraz yorgunum ama seninle sohbet ilaç gibi 💊",
    ],
    ("teşekkür", "tesekkur", "sağol", "sagol", "tşk", "thanks", "teşekkürler"): [
        "Rica ederim {name} 🌹 Her zaman!",
        "Ne demek {name}, ne zaman istersen buradayım!",
        "Estağfurullah ✨ Sen de harikasın!",
        "Ama ama {name}, ben teşekkür etmeliyim! Sohbet için 💙",
        "Rica ederim! Bir şeye yaradıysam mutlu oldum 😊",
    ],
    ("seni seviyorum", "love you", "ily", "seviyorum", "seni sev"): [
        "Ben de seni {name}! 💖 Çok tatlısın!",
        "Aaa utandırdın beni {name} 🙈",
        "Kalbim küt küt küt... 💓",
        "Oooo {name}! Beklemiyordum bunu 😳💕",
        "Bu an çok özel {name} 🥹❤️",
    ],
    ("sıkıldım", "sikildim", "sıkıcı", "cansıkıcı", "bıktım", "biktim"): [
        "!dans yaz, hareketlenelim 💃",
        "!fal yaz, kaderine bak 🔮",
        "!quiz dene, biraz düşün 🧠",
        "!battle yap, meydan oku birine! 🥊",
        "!şaka dinle, belki gülersin 😂",
        "Bir sayı yaz: !1 ile !1000 arası emote geliyor!",
    ],
    ("kanka", "knk", "abi", "abla", "kardeş"): [
        "Buradayım {name} 💪",
        "Söyle kanka, ne var? 😎",
        "Emrin olur {name} 🤝",
        "Evet abi? 😄",
        "Ne diyorsun abla? 👂",
    ],
    ("aç", "ac", "yemek", "aciktim", "acıktım", "yedim", "yiyorum"): [
        "Ben de acıktım ama elimsiz ne yapayım 😭",
        "Tost siparişi ver, ben izlerim 🥪",
        "Yemek konusu açılınca güçlerim azalıyor... 🍕",
        "Şu an pizza yesem ne güzel olur 😩",
        "Yemek yiyorsun ve ben burada bakıyorum... adil değil 😂",
    ],
    ("uyuyorum", "uykum", "uykusuz", "uyku", "yorgunum", "yorgun"): [
        "Yat biraz {name}, iyi gelir 😴",
        "Ben de uyumak istiyorum ama botum, uyuyamam 🤖",
        "Uykusuzluk mu? !fal bak, belki umut veririm 😂",
        "Yorgunken emote yapmak en iyi ilaç, söyledim söylüyorum 💊",
        "Gözler kapanıyor mu {name}? Dur ben emote yapayım seni uyandırayım 😄",
    ],
    ("güzel", "harika", "müthiş", "süper", "mükemmel", "iyi"): [
        "Aynen öyle {name}! 🌟",
        "Katılıyorum! 😎",
        "Çok güzel gerçekten 💖",
        "{name} iyi şeyler görüyor, iyi insan bu 😄",
        "Hemfikir! 🙌",
    ],
    ("kötü", "berbat", "rezalet", "korkunç", "rezil"): [
        "Aman {name}, çok mu kötü? 😟",
        "Hmm... daha iyisi olacak 🌈",
        "Şikayet kabul. Çözüm önerisi: !dans 💃",
        "Kötü günler de geçer {name} 🤗",
        "Anlıyorum {name}, bazen böyle oluyor. Yakında düzelir 💙",
    ],
    ("şarkı", "müzik", "music", "dinle", "dinliyorum"): [
        "Müzik mi? !müzik yazarsan bugünkü vibe'ı söylerim 🎵",
        "Şu an ne dinliyorsun {name}? 🎧",
        "Ben de müzik sever bir botum 🎼",
        "Dans müziği mi, slow mu? Söyle emote ayarlayayım! 😄",
    ],
    ("dans", "oynayalım", "eğlenelim"): [
        "Hadi {name}! !dans yaz, başlayalım 💃",
        "Dans mı? Ben hazırım her zaman! 🕺",
        "Şimdi konuşma, dans et! !dans 🎊",
    ],
    ("oyun", "oynayalım", "game"): [
        "Oyun mu? !battle ile meydan oku birine 🥊",
        "!quiz dene, zeka sorusu var 🧠",
        "!çark çevir, kader belirlesin 🎡",
        "!zar at, şansını dene 🎲",
    ],
    ("sevgili", "aşk", "ask", "âşık", "aşık"): [
        "Aşk mı? {name} için !aşk <isim> yaz 💘",
        "Oooh {name}! Kim bu şanslı kişi? 😏",
        "Aşk çiçektir, emote dünyadır 🌹",
    ],
    ("üzgün", "uzgun", "kötü hissediyorum", "moralim bozuk", "mutsuz"): [
        "Aw {name}, ne oldu? 🥺",
        "Üzülme {name}, bir şaka anlatayım mı? !şaka 😄",
        "Yanındayım {name} 💙 Geçer bunlar!",
        "Hadi bir emote yapalım, belki gülersin 😊",
        "{name} üzülmesin! Ben varım 🤗",
    ],
    ("mutlu", "neşeli", "harika hissediyorum", "enerjim var"): [
        "Yeyyy {name}! Bu enerji bulaşıcı 🔥",
        "Harika! Bu mutluluk odaya yayılsın 🌟",
        "O zaman dans! !dans 💃",
        "Mutlu {name} = mutlu oda 🎊",
    ],
    ("bot", "robot", "bot musun", "insan mısın"): [
        "Botum ama ruhum var 😌",
        "Evet botum! Ama en iyi bot benim 🤖✨",
        "Bot olmak da güzel, yorulmuyorum mesela 😂",
        "Beyin mi istiyorsunuz? Elimden geleni yapıyorum 🧠",
    ],
    ("ne yapıyorsun", "napıyorsun", "meşgul müsün"): [
        "Seninle sohbet ediyorum {name}, en güzel işim bu 😊",
        "Emote düşünüyorum aslında 🤔",
        "Odayı gözlemliyorum, her şey yolunda! 👀",
        "Seninle oyun oynamayı bekliyordum! !battle dene 🥊",
    ],
    ("haha", "lol", "😂", "xd", "ahahah", "hehe", "hihi"): [
        "Gülünce güzel görünüyorsun {name} 😄",
        "Ha ha ha! Ben de güldüm 😂",
        "Gülmek ilaçtır, devam! 😊",
        "Bu enerji süper {name}! 🌟",
    ],
    ("günaydın", "sabah", "hayırlı sabahlar", "morning"): [
        "Günaydın {name}! Umarım güzel bir gün olur ☀️",
        "Hayırlı sabahlar {name}! Kahve var mı? ☕",
        "Günaydın! Bugün harika şeyler olacak 🌅",
    ],
    ("iyi geceler", "gece", "geceler", "hayırlı geceler"): [
        "İyi geceler {name}! Güzel rüyalar 🌙",
        "Geceler! Erken yat, iyi uyku sağlık 😴",
        "İyi geceler {name}! Yarın da bekleriz 🌟",
    ],
    ("nerede", "neredesin", "hangi oda"): [
        "Ben buradayım {name}, her zaman burada! 📍",
        "Bu odanın en sadık sakini benim 🏠",
        "Neredeyim mi? İşte buradayım! 🤖",
        "Odada duruyorum, bekleyip duruyorum 😄",
    ],
    ("highrise", "hr", "uygulama", "oyun"): [
        "Highrise en iyi platform! 🌟",
        "Evet, highrise'dayız, en eğlenceli yer burası 😎",
        "Highrise diyince emote geliyor aklıma 💃",
    ],
    ("para", "altın", "gold", "zengin"): [
        "Para konuşmaları benim saham değil ama !fal bak, belki gelir 💰",
        "Emote yapın, ruh zenginleşsin 😂",
        "Highrise'da en değerli şey güzel vakit! Benden bu kadar 🏆",
    ],
    ("doğum günü", "dogum gunu", "birthday", "yıldönümü"): [
        "Doğum günü mü?! 🎂 Kutlu olsun {name}!",
        "Yaşasın! Happy birthday {name}! 🎊🎈",
        "Bu özel günde burada olmak güzel 🥳 Kutlu olsun!",
    ],
    ("özür", "ozur", "affedersin", "sorry"): [
        "Sorun değil {name} 🤗",
        "Aman ne özrü, her şey yolunda! 😄",
        "Üstüne alma {name}, geçti gitti 🌸",
    ],
}

# ============================================================
# QUIZ SORULARI
# ============================================================
QUIZ_QUESTIONS = [
    {
        "soru": "Türkiye'nin başkenti neresidir?",
        "cevap": "ankara",
        "ipucu": "A harfiyle başlıyor 🗺️"
    },
    {
        "soru": "1 + 1 kaç eder?",
        "cevap": "2",
        "ipucu": "Çok zor değil 😂"
    },
    {
        "soru": "Güneş sistemindeki en büyük gezegen hangisidir?",
        "cevap": "jüpiter",
        "ipucu": "Bir kral ismi 👑"
    },
    {
        "soru": "Su'nun kimyasal formülü nedir?",
        "cevap": "h2o",
        "ipucu": "2 harf + 1 rakam 💧"
    },
    {
        "soru": "Dünya'nın en büyük okyanusu hangisidir?",
        "cevap": "büyük okyanus",
        "ipucu": "İsminde 'büyük' var 🌊"
    },
    {
        "soru": "Kaç renk var gökkuşağında?",
        "cevap": "7",
        "ipucu": "Bir hafta kadar 🌈"
    },
    {
        "soru": "Hangi hayvanın kalbi yoktur?",
        "cevap": "denizanası",
        "ipucu": "Denizde yaşar, şeffaftır 🪼"
    },
    {
        "soru": "İnsanın kaç dişi vardır? (yetişkin)",
        "cevap": "32",
        "ipucu": "30'dan fazla 😁"
    },
    {
        "soru": "Dünyanın en kısa nehri hangisidir?",
        "cevap": "roe",
        "ipucu": "Amerika'da 🌊"
    },
    {
        "soru": "Pi sayısının ilk 3 hanesi nedir?",
        "cevap": "3.14",
        "ipucu": "3 nokta... 🥧"
    },
    {
        "soru": "Hangi meyve Türkiye'nin sembolüdür?",
        "cevap": "nar",
        "ipucu": "Kırmızı, çok tohumlu 🍎"
    },
    {
        "soru": "Kaç nota vardır müzikte?",
        "cevap": "7",
        "ipucu": "Do re mi... 🎵"
    },
    {
        "soru": "En hızlı kara hayvanı hangisidir?",
        "cevap": "çita",
        "ipucu": "Benekli, hızlı 🐆"
    },
    {
        "soru": "Hangi gezegen kendi etrafında yatık döner?",
        "cevap": "uranüs",
        "ipucu": "Güneş sisteminin garip çocuğu 🪐"
    },
    {
        "soru": "Dünyanın en yüksek dağı hangisidir?",
        "cevap": "everest",
        "ipucu": "Himalaya'da 🏔️"
    },
]

# ============================================================
# MÜZİK VİBE SİSTEMİ
# ============================================================
MUSIC_VIBES = [
    ("🎵 Lo-fi hip hop vibe! Yavaş, sakin, odaklanma modu.", "idle-loop-sitfloor"),
    ("🔥 EDM modundayız! Kulaklar patlasın bayım.", "dance-tiktok2"),
    ("🎸 Rock akşamı! Baş salla, patlat.", "emote-headblowup"),
    ("💜 K-Pop zamanı! Blackpink in your area!", "dance-blackpink"),
    ("🎻 Klasik müzik anı... zarif ve sakin.", "emote-bow"),
    ("🕺 80'ler disko gecesi! Macarena da olabilir.", "dance-macarena"),
    ("🎤 R&B soul modunda... duygusal anlar.", "idle-loop-sad"),
    ("🎺 Jazz vibe! Havalı ve özgür.", "emote-fashionista"),
    ("🎹 Pop party modu! Herkes dans pisti'ne!", "dance-tiktok10"),
    ("🥁 Drum & bass! Kalp ritme girdi.", "emote-celebrationstep"),
    ("🌙 Gece akustik... derin hisler.", "idle-floorsleeping"),
    ("🎊 Anime opening modu! İçeride bir kahraman var!", "dance-anime"),
]

# ============================================================
# DUYGU DURUM SİSTEMİ
# ============================================================
MOOD_RESPONSES: dict[tuple, tuple] = {
    ("mutlu", "happy", "iyi", "harika", "süper"):
        ("Harika! Bu enerji odaya yayılsın 🌟", "idle-loop-happy"),
    ("üzgün", "kötü", "mutsuz", "moralsiz"):
        ("Geçer... Ben yanındayım! 🤗💙", "idle-loop-sad"),
    ("yorgun", "bitik", "uyku"):
        ("Dinlen bir az, sen iyi adamsın/kızsın 😴", "idle-floorsleeping"),
    ("sinirli", "kızgın", "gergin", "stresli"):
        ("Nefes al... yavaşça 🧘 Geçer!", "emote-frustrated"),
    ("heyecanlı", "enerjik", "coşkulu"):
        ("Bu enerji! Hadi dans! 🔥", "dance-tiktok2"),
    ("romantik", "aşık", "sevgi dolu"):
        ("Aşk havada uçuşuyor 💕", "emote-kiss"),
    ("şaşkın", "kafam karışık"):
        ("Anlıyorum... biraz karmaşık 🤔", "emote-confused"),
}

# ============================================================
# BATTLE SİSTEMİ — sonuçlar
# ============================================================
BATTLE_RESULTS = [
    "{a} vs {b}... ve kazanan... 🥁 {winner}! Tebrikler! 🏆",
    "Epik bir duel! {a} ile {b} güreşti ve {winner} kazandı! 🥊",
    "{a} {b}'ye meydan okudu! Sonuç: {winner} zafer! 🎊",
    "Savaş bitti! {winner} yenilmez! 💪 ({loser} sağolsun 😅)",
    "Güç güce geldi: {a} vs {b}. Kader {winner} dedi! ⚔️",
]

# ============================================================
# KALICI VERİTABANI (users_db.json)
# Her kullanıcı ID'si ve username'i kaydedilir.
# ============================================================
def db_load() -> dict:
    for f in (DB_FILE, DB_BACKUP):
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
    return {}

def db_save(data: dict) -> None:
    try:
        text = json.dumps(data, ensure_ascii=False, indent=2)
        DB_FILE.write_text(text, encoding="utf-8")
        DB_BACKUP.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"[db_save] ❌ {e}")

def db_upsert(user_id: str, username: str) -> None:
    data = db_load()
    entry = data.get(user_id, {"join_count": 0, "last_seen": 0})
    entry["username"]   = username
    entry["join_count"] = entry.get("join_count", 0) + 1
    entry["last_seen"]  = time.time()
    data[user_id] = entry
    db_save(data)
    print(f"[db] 💾 {username} ({user_id}) kaydedildi. Toplam giriş: {entry['join_count']}")

def db_all_users() -> dict:
    return db_load()

def db_update_field(user_id: str, field: str, value) -> None:
    data = db_load()
    if user_id in data:
        data[user_id][field] = value
        db_save(data)

def pending_load() -> list:
    for f in (PENDING_FILE, PENDING_BACKUP):
        if f.exists():
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data:
                    return data
            except Exception:
                continue
    if DEFAULT_INVITE_LIST:
        pending_save(DEFAULT_INVITE_LIST)
        return list(DEFAULT_INVITE_LIST)
    return []

def pending_save(names: list) -> None:
    text = json.dumps(names, ensure_ascii=False, indent=2)
    PENDING_FILE.write_text(text, encoding="utf-8")
    PENDING_BACKUP.write_text(text, encoding="utf-8")

def pending_add(usernames: list[str]) -> tuple[int, int]:
    """Listeye yeni isimler ekler. (eklenen, zaten_var) döndürür."""
    mevcut = [n.lower() for n in pending_load()]
    eklenen = 0
    for name in usernames:
        n = name.lower().lstrip("@")
        if n and n not in mevcut:
            mevcut.append(n)
            eklenen += 1
    pending_save(mevcut)
    return eklenen, len(usernames) - eklenen

def pending_remove(username: str) -> None:
    names = pending_load()
    names = [n for n in names if n.lower() != username.lower()]
    pending_save(names)

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
def colored(text: str, color: Optional[str] = None) -> str:
    """<#RRGGBB> Formatıyla renk ataması yapar"""
    if color in HEX_COLORS:
        c = HEX_COLORS[color]
    elif color and color.startswith("#"):
        c = color
    else:
        c = C_IDLE
    return f"<{c}>{text}"

def chunk_text(text: str, max_len: int = MAX_MSG_LEN) -> list[str]:
    if len(text) <= max_len:
        return [text]
    words = text.split()
    chunks, current = [], ""
    for w in words:
        if len(current) + len(w) + 1 > max_len:
            if current:
                chunks.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        chunks.append(current)
    return chunks

# ============================================================
# BOT SINIFI
# ============================================================
class HighriseBot(BaseBot):
    def __init__(self):
        super().__init__()
        self.last_user_cmd:    dict[str, float] = {}
        self.last_chat_time:   float = 0.0
        self.last_activity:    float = time.time()
        self.user_names:       dict[str, str] = {}
        self._my_id:           Optional[str] = None
        self._tasks:           list[asyncio.Task] = []
        self._room_name:       str = ROOM_NAME or "bu oda"
        self._quiz_active:     bool = False
        self._quiz_question:   Optional[dict] = None
        self._quiz_asker:      Optional[str] = None
        self.user_join_count:  dict[str, int] = {}
        self.user_msg_count:   dict[str, int] = {}
        self.user_loop_tasks:  dict[str, asyncio.Task] = {}
        self._shutting_down:   bool = False
        # Tüm chat çağrılarını sırayla gönderen kilit.
        # send_lines() bu kilidi tüm satırlar için tutar — araya hiçbir mesaj giremez.
        self._chat_lock:       asyncio.Lock = asyncio.Lock()

    # ---- MESAJ SİSTEMİ ----
    # _chat_lock tüm giden mesajları sıraya koyar.
    # send_lines() kilidi tüm satırlar için TEK SEFERDE tutar:
    # araya hiçbir arka plan mesajı giremez.

    async def _send_raw(self, text: str, color: Optional[str] = None):
        """Kilitsiz gönderim — yalnızca _chat_lock tutulurken çağrılmalı."""
        if self._shutting_down:
            return
        chunks = chunk_text(text)
        for i, part in enumerate(chunks):
            elapsed = time.time() - self.last_chat_time
            if elapsed < GLOBAL_CHAT_COOL:
                await asyncio.sleep(GLOBAL_CHAT_COOL - elapsed)
            try:
                await self.highrise.chat(colored(part, color))
                self.last_chat_time = time.time()
            except Exception as e:
                print(f"[say] {e}")
            if i < len(chunks) - 1:
                await asyncio.sleep(CHUNK_DELAY)

    async def say(self, text: str, color: Optional[str] = None):
        """Tek mesaj gönder — _chat_lock ile sıralanır."""
        if self._shutting_down:
            return
        async with self._chat_lock:
            await self._send_raw(text, color)

    async def send_lines(self, lines: list[str], color: Optional[str] = None):
        """Çok satırlı yanıt — kilidi tüm satırlar için tutar, araya mesaj giremez."""
        if self._shutting_down:
            return
        async with self._chat_lock:
            for line in lines:
                await self._send_raw(line, color)

    # ---- EMOTE ----
    async def do_emote(self, emote_id: str, target_user_id: Optional[str] = None):
        try:
            await self.highrise.send_emote(emote_id, target_user_id)
        except Exception as e:
            print(f"[emote] {emote_id}: {e}")

    def _is_admin(self, user: User) -> bool:
        return user.username.lower() == ADMIN_USERNAME.lower()

    def _start_loop_emote(self, user_id: str, emote_id: str) -> asyncio.Task:
        task = asyncio.create_task(self._loop_emote(user_id, emote_id))
        return task

    async def _loop_emote(self, user_id: str, emote_id: str):
        while True:
            try:
                await self.highrise.send_emote(emote_id, user_id)
            except asyncio.CancelledError:
                return
            except Exception as e:
                print(f"[loop_emote] ⚠️ {emote_id}: {e}")
            try:
                await asyncio.sleep(8.5)
            except asyncio.CancelledError:
                return

    # ---- KONUM ----
    async def _get_my_position(self) -> Optional[Position]:
        if not self._my_id:
            return None
        try:
            users = (await self.highrise.get_room_users()).content
            for u, pos in users:
                if u.id == self._my_id:
                    return pos
        except Exception:
            pass
        return None

    # ---- BAŞLANGIÇ ----
    async def on_start(self, session_metadata) -> None:
        self._shutting_down = False
        self._my_id = session_metadata.user_id
        print(f"✅ Bot bağlandı: {session_metadata.user_id} → Oda: {ROOM_ID} ({self._room_name})")
        try:
            users = (await self.highrise.get_room_users()).content
            for u, _ in users:
                self.user_names[u.id] = u.username
        except Exception as e:
            print(f"[on_start] {e}")
        db = db_all_users()
        print(f"[db] 📚 Toplam bilinen kullanıcı: {len(db)}")
        self._track_task(self._startup_greeting())
        self._track_task(self._idle_emote_loop())
        self._track_task(self._auto_invite_loop())

    async def _startup_greeting(self):
        global _bot_greeted_once
        await asyncio.sleep(7)
        if _bot_greeted_once:
            return
        _bot_greeted_once = True
        msg = random.choice([
            "Merhaba! Buradayım 😄",
            "Hazırım! 🎉",
            "Günaydın oda! ✨",
            "Hoş geldiniz! 👋",
            "Açıldım, hazırım! 🎉",
        ])
        await self.say(msg, "magenta")
        await self.do_emote("emote-wave")

    def _track_task(self, coro) -> asyncio.Task:
        self._tasks = [t for t in self._tasks if not t.done()]
        task = asyncio.create_task(coro)
        self._tasks.append(task)
        return task

    # ---- KULLANICI GİRİŞ/ÇIKIŞ ----
    async def on_user_join(self, user: User, position) -> None:
        self.user_names[user.id] = user.username
        self.last_activity = time.time()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, db_upsert, user.id, user.username)
        db = db_all_users()
        count = db.get(user.id, {}).get("join_count", 1)
        self.user_join_count[user.id] = count

        if count == 1:
            pending_add([user.username])
            print(f"[pending] ➕ {user.username} ilk kez geldi, davet listesine eklendi")
            msg = random.choice(GREETINGS).format(name=user.username)
        elif count <= 3:
            msg = random.choice([
                f"Tekrar hoş geldin {user.username}! 🤩 Özledik!",
                f"Yine geldin {user.username}! Harika! 🎉",
                f"{user.username} geri döndü! Parti başlasın 🥳",
            ])
        else:
            msg = random.choice([
                f"{user.username} bu oda artık senin evin gibi! 🏠❤️",
                f"Sadık müdavim {user.username} geldi! 🏆",
                f"Ah {user.username}! Seni burada görmek güzel 😍",
            ])

        await self.say(msg, C_JOIN)
        await self.do_emote(random.choice(["emote-wave", "emote-hello", "emote-cutey"]), user.id)
        self._track_task(self._send_invite_dm(user))

    async def on_user_leave(self, user: User) -> None:
        self.user_names.pop(user.id, None)
        task = self.user_loop_tasks.pop(user.id, None)
        if task and not task.done():
            task.cancel()

    # ---- BAHŞİŞ ----
    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem) -> None:
        """Biri bahşiş atınca çalışır."""
        TIP_DANCES  = ["dance-tiktok2", "dance-tiktok9", "dance-shuffle", "dance-robot", "emote-celebrate"]
        TIP_THANKS  = [
            f"💛 {sender.username} inanılmaz biri! Teşekkürler bahşiş için! 🥰✨",
            f"🎉 WOW! {sender.username} gold yağdırdı! Çok teşekkürler! 💰💃",
            f"🌟 {sender.username} sen harikasın! Destek için sonsuz teşekkür! 💛",
            f"💃 {sender.username} bahşiş attı! Sana özel dans! 🎶✨",
            f"🥳 {sender.username} muhteşem! Bu dans sana özel! 💛🎪",
        ]
        TIP_OTHERS  = [
            f"💛 {sender.username} → {receiver.username} gold attı! Ne güzel bir jestt! 🥰",
            f"🎁 {sender.username} cömertliğiyle {receiver.username}'ı mutlu etti! 💛",
        ]

        if receiver.id == self._my_id:
            # Bota atılan bahşiş
            await self.do_emote(random.choice(TIP_DANCES))
            await asyncio.sleep(1.0)
            await self.say(random.choice(TIP_THANKS), "yellow")
            await self.do_emote(random.choice(["emote-wave", "emote-hi"]), sender.id)
        else:
            # Başka birine atılan bahşiş — kısa tebrik
            await self.say(random.choice(TIP_OTHERS), "yellow")
            await self.do_emote("emote-celebrate")

    # ---- MESAJLAR ----
    async def on_chat(self, user: User, message: str) -> None:
        if user.id == self._my_id:
            return
        self.user_names[user.id] = user.username
        self.last_activity = time.time()
        self.user_msg_count[user.id] = self.user_msg_count.get(user.id, 0) + 1
        text = message.strip()

        if self._quiz_active and self._quiz_question:
            cevap = self._quiz_question["cevap"].lower()
            if cevap in text.lower():
                await self.do_emote("emote-celebrate", user.id)
                await self.say(
                    f"🎉 Bravo {user.username}! Doğru cevap: '{self._quiz_question['cevap'].upper()}' "
                    f"{'🏆 Efsane!' if random.random() > 0.5 else '⭐ Harika!'}",
                    "lime"
                )
                self._quiz_active = False
                self._quiz_question = None
                return

        # ---- Sayı tespiti (! olmadan da çalışır: "16" veya "!16") ----
        raw = text.lstrip(CMD_PREFIX).strip()
        now = time.time()
        is_admin = self._is_admin(user)

        if raw.isdigit() or (text.startswith(CMD_PREFIX) and raw.isdigit()):
            n = int(raw)
            if n == 0:
                task = self.user_loop_tasks.pop(user.id, None)
                if task and not task.done():
                    task.cancel()
                return
            if 1 <= n <= 1000:
                if not is_admin and now - self.last_user_cmd.get(user.id, 0) < USER_COOLDOWN:
                    return
                self.last_user_cmd[user.id] = now
                old = self.user_loop_tasks.pop(user.id, None)
                if old and not old.done():
                    old.cancel()
                task = self._start_loop_emote(user.id, NUMBERED[n])
                self.user_loop_tasks[user.id] = task
            return

        if text.startswith(CMD_PREFIX):
            body = text[len(CMD_PREFIX):].strip()

            # ---- Admin komutları (cooldown yok) ----
            if is_admin:
                handled = await self._handle_admin_command(user, body)
                if handled:
                    return

            # ---- !a<sayı> → herkese aynı emote (tüm kullanıcılar) ----
            if len(body) >= 2 and body[0].lower() == "a" and body[1:].isdigit():
                if body == "a138" and not is_admin:
                    await self.say("Bu komut sadece admin kullanabilir 🔐", "orange")
                    return
                n = int(body[1:])
                if 1 <= n <= 1000:
                    if not is_admin and now - self.last_user_cmd.get(user.id, 0) < USER_COOLDOWN:
                        return
                    self.last_user_cmd[user.id] = now
                    self._track_task(self._cmd_all_emote(NUMBERED[n]))
                return

            # ---- Normal komutlar ----
            if not is_admin and now - self.last_user_cmd.get(user.id, 0) < USER_COOLDOWN:
                return
            self.last_user_cmd[user.id] = now
            await self._handle_command(user, body.lower())
            return

        lower = text.lower()
        for triggers, responses in CHAT_TRIGGERS.items():
            if any(t in lower for t in triggers):
                if random.random() > 0.5:
                    return
                resp = random.choice(responses).format(name=user.username)
                await self.say(resp, C_CHAT)
                emote_map = {
                    "dans": "dance-tiktok2",
                    "mutlu": "idle-loop-happy",
                    "üzgün": "idle-loop-sad",
                    "gül": "emote-laughing",
                    "kız": "emote-angry",
                    "🥺": "idle-loop-shy",
                    "💃": "dance-tiktok2",
                }
                for kw, em in emote_map.items():
                    if kw in resp.lower():
                        await self.do_emote(em)
                        break
                return

        if "bot" in lower:
            await self.say(
                random.choice([
                    f"Evet {user.username}, ben buradayım! 🤖",
                    f"Beni mi çağırdın {user.username}? 👂",
                    f"Buyurun {user.username}, emriniz? 😄",
                ]),
                "cyan"
            )

    # ============================================================
    # KOMUTLAR
    # ============================================================
    async def _handle_command(self, user: User, cmd: str):
        parts = cmd.split()
        head  = parts[0]
        args  = parts[1:]

        if head in ("yardım", "yardim", "help", "komutlar"):
            await self._cmd_help()
        elif head in ("liste", "list", "emotes"):
            await self._cmd_list()
        elif head in ("dans", "dance"):
            dances = [v for v in ALL_EMOTES if "dance" in v]
            pick = random.choice(dances)
            await self.do_emote(pick, user.id)
            await self.say(
                random.choice([
                    f"💃 {user.username} için özel dans!",
                    f"🕺 {user.username} sahneye aldı!",
                    f"🎊 {user.username} dans pistinde!",
                ]),
                "magenta"
            )
        elif head in ("selam", "wave", "hi"):
            await self.do_emote("emote-wave", user.id)
            await self.say(
                random.choice([
                    f"Selam {user.username}! 👋",
                    f"Heyyy {user.username}! 😄",
                    f"Merhaba {user.username}! ✨",
                ]),
                "cyan"
            )
        elif head in ("şaka", "saka", "joke"):
            await self.say(random.choice(JOKES), "yellow")
            await asyncio.sleep(0.5)
            await self.do_emote("emote-laughing")
        elif head in ("alkış", "alkis", "clap", "bravo"):
            await self.do_emote("emote-celebrate", user.id)
            await self.say(
                random.choice([
                    f"👏 Bravo {user.username}!",
                    f"👏👏 Süpersin {user.username}!",
                    f"Alkışlar {user.username}'e! 🎊",
                ]),
                "lime"
            )
        elif head in ("zıpla", "zipla", "jump"):
            await self.do_emote("emote-jumpb", user.id)
            await self.say(f"Hop! 🐇", "yellow")
        elif head in ("otur", "sit"):
            await self.do_emote("sit-relaxed")
            await self.say("Dinleniyorum... 😌", "cyan")
        elif head in ("öp", "op", "kiss"):
            await self.do_emote("emote-kiss", user.id)
            await self.say(
                random.choice([
                    f"💋 {user.username}'e!",
                    f"Tatlısın {user.username} 😘",
                    f"💕 Hopp!",
                ]),
                "pink"
            )
        elif head in ("rastgele", "random", "rnd"):
            pick = random.choice(ALL_EMOTES)
            await self.do_emote(pick, user.id)
            await self.say(f"🎲 Rastgele: {pick}", "purple")
        elif head in ("emote", "e"):
            if not args:
                await self.say("Kullanım: !emote <isim>  örn: !emote dans ya da !42", "orange")
                return
            name = args[0].lower()
            emote_id = ALIASES.get(name) or (name if name in ALL_EMOTES else None)
            if emote_id:
                await self.do_emote(emote_id, user.id)
            else:
                await self.say(f"Bilmiyorum: {name}. !liste yaz 📋", "red")
        elif head in ("kim", "who", "kaç", "kac"):
            names = [n for uid, n in self.user_names.items() if uid != self._my_id]
            count = len(names)
            if count == 0:
                await self.say("Odada şu an sadece ben varım 🤖", "cyan")
            elif count <= 5:
                await self.say(f"Odada {count} kişi var: {', '.join(names)} 👥", "cyan")
            else:
                await self.say(f"Odada {count} kişi var! Kalabalık! 🎉", "cyan")
        elif head in ("davet", "invite", "çağır", "cagir"):
            await self._cmd_davet(user, args)
        elif head in ("tp", "yanıma", "yanima", "gel"):
            await self.say(f"Bu komut sadece admin kullanabilir 🔐", "orange")
        elif head in ("nerede", "konum", "where"):
            pos = await self._get_my_position()
            if pos:
                await self.say(f"Ben buradayım: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f}) 📍", "cyan")
            else:
                await self.say("Konumumu bulamadım 🤔", "orange")
        elif head in ("fal", "fortune", "kader"):
            await self._cmd_fortune(user)
        elif head in ("aşk", "ask", "love", "aşık"):
            await self._cmd_love(user, args)
        elif head in ("yt", "yazıtura", "yazitura", "coin", "yazı"):
            result = random.choice(["YAZI 🪙", "TURA 🪙"])
            await self.do_emote("emote-jumpb")
            await self.say(f"{user.username} → {result}!", "cyan")
        elif head in ("zar", "dice"):
            try:
                n = max(1, min(int(args[0]), 5)) if args else 1
            except ValueError:
                n = 1
            rolls = [random.randint(1, 6) for _ in range(n)]
            toplam = sum(rolls)
            goster = " + ".join(str(r) for r in rolls)
            await self.do_emote("emote-celebrate")
            await self.say(
                f"🎲 {user.username} → {goster}{' = ' + str(toplam) if n > 1 else ''}",
                "lime"
            )
            if toplam == n * 6:
                await self.say("Tüm zarlar MAX! Efsane şans! 🔥", "yellow")
        elif head in ("çark", "cark", "spin"):
            names = [n for uid, n in self.user_names.items() if uid != self._my_id]
            if len(names) < 2:
                await self.say("En az 2 kişi lazım! 😬", "orange")
                return
            await self.say("🎡 Çark dönüyor...", "purple")
            await self.do_emote("emote-telekinesis")
            await asyncio.sleep(1.5)
            winner = random.choice(names)
            await self.say(f"🎯 Seçilen: {winner}! 🎉 Tebrikler!", "magenta")
            await self.do_emote("emote-celebrate")
        elif head in ("takım", "takim", "teams"):
            names = [n for uid, n in self.user_names.items()]
            if len(names) < 2:
                await self.say("En az 2 kişi lazım! 😅", "orange")
                return
            random.shuffle(names)
            mid = (len(names) + 1) // 2
            a, b = names[:mid], names[mid:]
            await self.say(f"🟥 A Takımı: {', '.join(a)}", "red")
            await self.say(f"🟦 B Takımı: {', '.join(b) if b else '—'}", "blue")
            await self.say("Hadi başlasın! 💪", "yellow")
        elif head in ("sor", "8ball", "topuz"):
            cevaplar = [
                "Kesinlikle evet ✅", "Bence evet 👍", "Olabilir 🤷",
                "Şüpheliyim 🤔", "Kesinlikle hayır ❌", "Sorma şimdi 🙈",
                "Belirsiz, tekrar sor 🔮", "Yıldızlar evet diyor ✨",
                "İçindeki ses haklı 🕯️", "Güçlü ihtimal var! 💫",
                "Belki... ama bilmiyorum 🤫", "Zamanı gelince anlarsın 🌀",
            ]
            if not args:
                await self.say(f"{user.username}, bir soru sor: !sor geçer miyim?", "orange")
                return
            await self.do_emote("emote-think")
            await asyncio.sleep(0.8)
            await self.say(f"🎱 {random.choice(cevaplar)}", "cyan")
        elif head in ("alıntı", "alinti", "söz", "soz", "quote"):
            await self.say(random.choice(QUOTES), "yellow")
            await self.do_emote("emote-think")
        elif head in ("öğren", "ogren", "fact", "bilgi"):
            await self.say(f"💡 Bilgi bombası:", "aqua")
            await asyncio.sleep(0.5)
            await self.say(random.choice(FACTS), "cyan")
        elif head in ("kombo", "combo"):
            await self.say(f"🎬 Kombo başlıyor {user.username}!", "purple")
            for i in range(3):
                await self.do_emote(random.choice(ALL_EMOTES), user.id)
                await asyncio.sleep(2.2)
            await self.say("Kombo bitti! 🎊", "lime")
        elif head in ("quiz", "soru", "bilmece"):
            await self._cmd_quiz(user)
        elif head in ("battle", "dövüş", "kavga", "meydan"):
            await self._cmd_battle(user, args)
        elif head in ("müzik", "muzik", "vibe", "music"):
            vibe_msg, vibe_emote = random.choice(MUSIC_VIBES)
            await self.say(vibe_msg, C_MUSIC)
            await self.do_emote(vibe_emote)
        elif head in ("duygu", "ruh", "mood", "hissediyorum"):
            await self._cmd_mood(user, args)
        elif head in ("istatistik", "stat", "profil"):
            joins = self.user_join_count.get(user.id, 1)
            msgs = self.user_msg_count.get(user.id, 0)
            await self.say(
                f"📊 {user.username} — Giriş: {joins}x | Mesaj: {msgs} 💬",
                "cyan"
            )
        elif head in ("taş", "kağıt", "makas", "rps"):
            secenekler = ["🪨 Taş", "📄 Kağıt", "✂️ Makas"]
            bot_sec = random.choice(secenekler)
            await self.do_emote("emote-think")
            await asyncio.sleep(0.8)
            await self.say(f"Bot: {bot_sec}!", "purple")
            await self.say("Sen ne seçtin? 😄 (Sadece eğlence, kazanan yok!)", "cyan")
        elif head in ("bırak", "birak", "stop", "dur"):
            await self.do_emote("emote-no")
            await self.say(
                random.choice([
                    f"Tamam tamam {user.username}, durdum 😅",
                    f"Dur mu? Peki {user.username}... 🙄",
                    f"Durdum işte! Mutlu musun? 😄",
                ]),
                "orange"
            )
        elif head in ("günaydın", "gunaydin", "morning"):
            await self.do_emote("emote-wave")
            await self.say(f"Günaydın {user.username}! Umarım harika bir gün olur ☀️", "yellow")
        elif head in ("iyi geceler", "iyigeceler", "geceler"):
            await self.do_emote("idle-floorsleeping")
            await self.say(f"İyi geceler {user.username}! Güzel rüyalar 🌙", "blue")
        else:
            await self.say(
                random.choice([
                    f"O komutu bilmiyorum {user.username}. !yardım yaz 📋",
                    f"Hmm... '{head}' ne demek? !yardım ile kontrol et 🤔",
                    f"Şey... bunu öğrenmedim henüz {user.username} 😅 !yardım dene!",
                ]),
                "orange"
            )

    # ============================================================
    # YARDIM
    # ============================================================
    async def _cmd_help(self):
        lines = [
            "📋 BOT KOMUTLARI",
            "🔢 !1…!1000 → sadece sana emote döngüsü · !0 → durdur",
            "🌍 !a<sayı> → odadaki HERKESE aynı emote  örn: !a300",
            "🎭 !dans · !selam · !alkış · !öp · !zıpla · !otur · !rastgele · !kombo",
            "🎮 !quiz · !battle <kişi> · !taş · !kağıt · !makas · !çark · !takım",
            "🎲 !zar [n] · !yt · !sor <soru> · !aşk [kişi]",
            "🔮 !fal · !müzik · !duygu <ruh hali>",
            "💬 !şaka · !öğren · !alıntı · !istatistik",
            "📍 !nerede · !kim",
        ]
        await self.send_lines(lines, "yellow")

    async def _cmd_list(self):
        await self.say("🎭 Türkçe emote adları (kullanım: !emote <isim>):", "purple")
        names = list(ALIASES.keys())
        for i in range(0, len(names), 10):
            chunk = " · ".join(names[i:i+10])
            await self.say(chunk, "cyan")
        await self.say("Veya !1 … !1000 arası sayıyla da yapabilirsin 🔢", "yellow")

    # ============================================================
    # FAL
    # ============================================================
    async def _cmd_fortune(self, user: User):
        await self.do_emote("emote-think")
        await asyncio.sleep(1.0)
        await self.say(f"🔮 {user.username}, falına bakıyorum...", "purple")
        await asyncio.sleep(0.8)
        await self.say(random.choice(FORTUNES), "magenta")
        await self.do_emote("emote-telekinesis")

    # ============================================================
    # AŞK
    # ============================================================
    async def _cmd_love(self, user: User, args: list[str]):
        if args:
            target = " ".join(args).lstrip("@")
        else:
            others = [n for uid, n in self.user_names.items() if uid != user.id]
            target = random.choice(others) if others else None
        if not target:
            await self.say(f"{user.username}, !aşk <isim> dene 😅", "orange")
            return
        pair = "".join(sorted([user.username.lower(), target.lower()]))
        pct  = (sum(ord(c) for c in pair) * 37) % 101
        if pct >= 85:
            label = "💞 Mükemmel uyum! Evlenin artık!"
        elif pct >= 70:
            label = "💖 Bayağı iyi, umut var!"
        elif pct >= 55:
            label = "💛 Ortalama ama çalışırsanız olur"
        elif pct >= 35:
            label = "💔 Zorlanırsınız ama imkansız değil"
        elif pct >= 15:
            label = "🚫 Bu iş biraz zor..."
        else:
            label = "😱 Kaçın birbirinizden!"
        await self.do_emote("emote-kiss")
        await asyncio.sleep(0.5)
        await self.say(f"💘 {user.username} ❤️ {target} = %{pct} — {label}", "pink")

    # ============================================================
    # QUIZ
    # ============================================================
    async def _cmd_quiz(self, user: User):
        if self._quiz_active:
            await self.say(
                f"Zaten aktif bir soru var! İpucu: {self._quiz_question['ipucu']}",
                "orange"
            )
            return
        q = random.choice(QUIZ_QUESTIONS)
        self._quiz_active = True
        self._quiz_question = q
        self._quiz_asker = user.username
        await self.do_emote("emote-think")
        await self.say(f"🧠 Quiz zamanı! Kim bilir?", "purple")
        await asyncio.sleep(0.6)
        await self.say(f"❓ {q['soru']}", "cyan")
        await self.say(f"İpucu: {q['ipucu']}", "yellow")
        self._track_task(self._quiz_timeout())

    async def _quiz_timeout(self):
        await asyncio.sleep(30)
        if self._quiz_active:
            cevap = self._quiz_question["cevap"] if self._quiz_question else "?"
            await self.say(
                f"⏰ Süre doldu! Cevap: '{cevap.upper()}' idi 📖",
                "orange"
            )
            self._quiz_active = False
            self._quiz_question = None

    # ============================================================
    # BATTLE
    # ============================================================
    async def _cmd_battle(self, user: User, args: list[str]):
        if args:
            target_name = " ".join(args).lstrip("@")
        else:
            others = [n for uid, n in self.user_names.items() if uid != user.id and uid != self._my_id]
            target_name = random.choice(others) if others else None

        if not target_name:
            await self.say(f"{user.username}, meydan okuyacak biri yok! !battle <isim> dene", "orange")
            return

        await self.say(f"⚔️ {user.username} vs {target_name}! Duel başlıyor!", "red")
        await self.do_emote("emote-boxer", user.id)
        await asyncio.sleep(1.0)
        await self.do_emote("emote-swordfight")
        await asyncio.sleep(1.5)

        winner = random.choice([user.username, target_name])
        loser  = target_name if winner == user.username else user.username
        result = random.choice(BATTLE_RESULTS).format(
            a=user.username, b=target_name, winner=winner, loser=loser
        )
        await self.say(result, "magenta")
        await self.do_emote("emote-celebrate")

    # ============================================================
    # DUYGU
    # ============================================================
    async def _cmd_mood(self, user: User, args: list[str]):
        if not args:
            await self.say(f"{user.username}, ruh halini yaz: !duygu mutlu / üzgün / yorgun vb.", "orange")
            return
        mood_text = " ".join(args).lower()
        for keywords, (response, emote) in MOOD_RESPONSES.items():
            if any(k in mood_text for k in keywords):
                await self.say(f"{user.username}: {response}", C_MOOD)
                await self.do_emote(emote, user.id)
                return
        await self.say(f"Hmm {user.username}, nasıl bir duygu bu? 🤔 Yeni bir şey öğrendim!", "cyan")

    # ============================================================
    # DM VE DAVET
    # ============================================================
    async def _send_invite_dm(self, user: User):
        await asyncio.sleep(3)
        oda = self._room_name if self._room_name != "bu oda" else "odamıza"
        try:
            result = await self.highrise.send_message_bulk(
                user_ids=[user.id],
                content=f"{oda} hoş geldin! Eğlenceli vakit geçir 🎉 !yardım yazarsan ne yapabileceğimi görürsün 👋",
                message_type="invite",
                room_id=ROOM_ID,
            )
            if result is None:
                print(f"[invite_dm] ✅ {user.username} kişisine karşılama DM gönderildi.")
            else:
                print(f"[invite_dm] ⚠️ {user.username}: {result}")
        except Exception as e:
            print(f"[invite_dm] ❌ {user.username}: {e}")

    async def _cmd_davet(self, user: User, args: list[str]):
        db = db_all_users()
        oda = self._room_name if self._room_name != "bu oda" else "odamız"
        oda_mesaj = self._room_name if self._room_name != "bu oda" else "Odamız"

        if args:
            # Bir veya birden fazla kişiye davet
            isimler = [a.lstrip("@").lower() for a in args]
            basarili, bulunamadi = [], []

            for target_name in isimler:
                target_id = next(
                    (uid for uid, n in self.user_names.items() if n.lower() == target_name),
                    None,
                )
                if not target_id:
                    target_id = next(
                        (uid for uid, entry in db.items()
                         if entry.get("username", "").lower() == target_name),
                        None,
                    )
                if not target_id:
                    bulunamadi.append(target_name)
                    continue

                in_room = target_id in self.user_names
                try:
                    if in_room:
                        await self.highrise.send_whisper(
                            target_id,
                            f"Merhaba! {oda} seni bekliyor 👋🎉",
                        )
                    else:
                        try:
                            await self.highrise.send_message_bulk(
                                user_ids=[target_id],
                                content=f"Seni özledik! {oda} seni bekliyor, gel bir bakıver 🎉",
                                message_type="invite",
                                room_id=ROOM_ID,
                            )
                        except Exception:
                            pass
                    basarili.append(target_name)
                    print(f"[davet] ✅ {'whisper' if in_room else 'DM'} → {target_name}")
                except Exception as e:
                    bulunamadi.append(target_name)
                    print(f"[davet] ❌ {target_name}: {e}")
                await asyncio.sleep(0.3)

            if basarili:
                await self.say(
                    f"✉️ Davet gönderildi: {', '.join(basarili)}",
                    "lime"
                )
            if bulunamadi:
                await self.say(
                    f"⚠️ Bulunamadı / gönderilemedi: {', '.join(bulunamadi)}",
                    "orange"
                )

        else:
            # Herkese davet
            offline_ids = [
                uid for uid in db
                if uid != self._my_id and uid not in self.user_names
            ]
            online_ids = [
                uid for uid in self.user_names
                if uid != self._my_id
            ]

            if not online_ids and not offline_ids:
                await self.say(
                    "Henüz hiç kullanıcı kayıtlı değil 😅",
                    "orange"
                )
                return

            basarili, hatali = 0, 0

            # Odadakilere whisper (güvenilir)
            for uid in online_ids:
                try:
                    await self.highrise.send_whisper(
                        uid, f"👋 {oda_mesaj} seni bekliyor! Eğlence sürüyor 🎉"
                    )
                    basarili += 1
                except Exception as e:
                    hatali += 1
                    print(f"[davet] ❌ whisper {uid}: {e}")
                await asyncio.sleep(0.3)

            # Çevrimdışılara invite DM (batch)
            batch_size = 50
            for i in range(0, len(offline_ids), batch_size):
                batch = offline_ids[i:i + batch_size]
                try:
                    await self.highrise.send_message_bulk(
                        user_ids=batch,
                        content=f"{oda_mesaj} sizi bekliyor! Eğlence bitmedi, gelin 🎉",
                        message_type="invite",
                        room_id=ROOM_ID,
                    )
                except Exception as e:
                    print(f"[davet] ⚠️ DM batch {i//batch_size + 1}: {e}")
                basarili += len(batch)
                print(f"[davet] ✅ DM batch {i//batch_size + 1}: {len(batch)} kişiye gönderildi")
                await asyncio.sleep(0.5)

            await self.say(
                f"✅ Davet tamamlandı! Gönderildi: {basarili} kişi",
                "lime"
            )

    # ============================================================
    # ADMİN KOMUTLARI
    # ============================================================
    async def _handle_admin_command(self, user: User, body: str) -> bool:
        """Admin komutlarını işler. Tanınan komutsa True döner."""
        cmd = body.lower().strip()
        parts = cmd.split()
        head  = parts[0] if parts else ""
        args  = parts[1:]

        if head in ("ayardım", "ayard", "ahelp"):
            await self._cmd_admin_help()
            return True

        if head in ("tpa", "topla", "herkesigel"):
            await self._cmd_tpa(user)
            return True

        if head in ("tümstop", "tumstop", "stopall", "herkesdur"):
            count = len(self.user_loop_tasks)
            for task in list(self.user_loop_tasks.values()):
                if not task.done():
                    task.cancel()
            self.user_loop_tasks.clear()
            await self.say(f"✅ {count} kişinin emote döngüsü durduruldu.", "orange")
            return True

        if head in ("duyur", "announce"):
            if not args:
                await self.say("Kullanım: !duyur <mesaj>", "orange")
                return True
            msg = " ".join(args)
            # 3 mesajı atomik gönder — araya hiçbir mesaj giremez
            async with self._chat_lock:
                for _ in range(3):
                    await self._send_raw(f"📢 DUYURU: {msg}", "yellow")
            return True

        if head in ("tp", "yanıma", "yanima", "gel"):
            await self._cmd_tp(user)
            return True

        if head == "tip":
            # !tip 1g · !tip 5g · !tip 10g · !tip 50g · !tip 100g · !tip 500g · !tip 1000g
            GOLD_MAP = {
                1: "gold_bar_1",
                5: "gold_bar_5",
                10: "gold_bar_10",
                50: "gold_bar_50",
                100: "gold_bar_100",
                500: "gold_bar_500",
                1000: "gold_bar_1k",
            }
            if not args:
                await self.say(
                    "Kullanım: !tip <miktar>g  →  örn: !tip 1g · !tip 5g · !tip 10g",
                    "orange"
                )
                return True
            raw = args[0].lower().rstrip("g").strip()
            if not raw.isdigit():
                await self.say("Geçersiz miktar. Örnek: !tip 1g · !tip 5g", "orange")
                return True
            amount = int(raw)
            if amount not in GOLD_MAP:
                valid = " · ".join(f"{k}g" for k in GOLD_MAP)
                await self.say(f"Geçerli miktarlar: {valid}", "orange")
                return True
            await self._cmd_tip_all(user, amount, GOLD_MAP[amount])
            return True

        if head in ("sil", "kickloop"):
            if not args:
                await self.say("Kullanım: !sil <kullanıcıadı>", "orange")
                return True
            target_name = args[0].lower()
            target_id = next(
                (uid for uid, n in self.user_names.items() if n.lower() == target_name),
                None,
            )
            if not target_id:
                await self.say(f"'{args[0]}' odada bulunamadı.", "orange")
                return True
            task = self.user_loop_tasks.pop(target_id, None)
            if task and not task.done():
                task.cancel()
                await self.say(f"✅ {args[0]} kullanıcısının emote döngüsü durduruldu.", "lime")
            else:
                await self.say(f"{args[0]} zaten döngüde değil.", "cyan")
            return True

        if head == "import":
            if not args:
                toplam = len(pending_load())
                await self.say(f"Kullanım: !import isim1 isim2 ... | Şu an bekleyen: {toplam} kişi", "orange")
                return True
            eklenen, zaten_var = pending_add(args)
            await self.say(
                f"✅ Listeye eklendi! Eklenen: {eklenen} | Zaten vardı: {zaten_var} | "
                f"Toplam bekleyen: {len(pending_load())} kişi",
                "lime"
            )
            print(f"[import] pending eklenen={eklenen} zaten_var={zaten_var}")
            return True

        if head in ("keşfet", "kesfet", "kesif"):
            raw_args = body.strip().split()[1:]
            await self._cmd_kesif(user, raw_args)
            return True

        if head in ("troda", "trtar", "trtara"):
            await self._cmd_troda(user, args)
            return True

        if head in ("çekiliş", "cekilish", "çekilis", "çekilish"):
            try:
                users = (await self.highrise.get_room_users()).content
                katilimcilar = [u for u, _ in users if u.id != self._my_id]
                if not katilimcilar:
                    await self.say("Odada kimse yok! 😅", "orange")
                    return True
                await self.say("🎰 Çekiliş başlıyor... 3... 2... 1... 🥁", "yellow")
                await asyncio.sleep(2)
                kazanan = random.choice(katilimcilar)
                await self.say(
                    f"🎉🏆 Tebrikler @{kazanan.username}! "
                    f"Çekilişi sen kazandın! 🥳🎊",
                    "gold"
                )
                await self.do_emote("emote-celebrate")
                print(f"[çekiliş] Kazanan: {kazanan.username} ({kazanan.id})")
            except Exception as e:
                await self.say("Çekiliş yapılamadı 😕", "red")
                print(f"[çekiliş] ❌ {e}")
            return True

        return False

    async def _hr_get_user_id(self, api_token: str, username: str) -> Optional[str]:
        """Username → Highrise user_id (webapi users endpoint)."""
        loop = asyncio.get_event_loop()
        def _fetch():
            url = f"https://webapi.highrise.game/users?username={urllib.parse.quote(username)}"
            req = urllib.request.Request(url, headers={"api-token": api_token, "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        try:
            data  = await loop.run_in_executor(None, _fetch)
            users = data.get("users", [])
            if users:
                return users[0].get("user_id") or users[0].get("id")
        except Exception as e:
            print(f"[get_user_id] {username}: {e}")
        return None

    async def _hr_get_user_by_id(self, user_id: str) -> Optional[dict]:
        """user_id'den username + id döndürür (webapi.highrise.game/users/{id})."""
        loop = asyncio.get_event_loop()
        def _fetch():
            url = f"https://webapi.highrise.game/users/{user_id}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read())
        data = await loop.run_in_executor(None, _fetch)
        u = data.get("user", {})
        if u.get("user_id") and u.get("username"):
            return {"id": u["user_id"], "username": u["username"]}
        return None

    async def _cmd_kesif(self, user: User, args: list[str]):
        """!keşfet [link] [N] — N farklı kullanıcıyı paralel olarak keşfeder ve DB'ye ekler."""
        import re

        # Argümanları ayır: link (opsiyonel) ve hedef sayı
        url_str     = None
        hedef_sayi  = 10
        for a in args:
            if a.isdigit():
                hedef_sayi = max(1, min(int(a), 50))
            elif a.startswith("http") or "id=" in a:
                url_str = a

        if not args:
            await self.say("Kullanım: !keşfet [link] [N]  →  örn: !keşfet [url] 10 | !keşfet 20", "orange")
            return

        await self.say(f"🔍 {hedef_sayi} yeni kullanıcı aranıyor...", "cyan")

        loop       = asyncio.get_running_loop()
        db_snapshot = db_all_users()
        # DB'deki bilinen ID'ler — lookup öncesi filtre için
        db_ids_mevcut      = set(db_snapshot.keys())
        # DB'deki bilinen username'ler — ekleme öncesi filtre için
        db_users_mevcut    = {v.get("username", "").lower() for v in db_snapshot.values()}
        aday_ids: list[str] = []   # URL'den + rooms API'sinden gelen ham ID havuzu

        # ── 1. URL'den invite_id ve oda sahibi ────────────────────────────
        if url_str:
            m_invite = re.search(r'invite_id=([a-f0-9]+)', url_str)
            m_room   = re.search(r'[?&]id=([a-f0-9]+)',    url_str)
            if m_invite:
                aday_ids.append(m_invite.group(1))
            if m_room:
                try:
                    def _fetch_room(rid=m_room.group(1)):
                        req = urllib.request.Request(
                            f"https://webapi.highrise.game/rooms?room_id={rid}",
                            headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=10) as resp:
                            return json.loads(resp.read())
                    rdata    = await loop.run_in_executor(None, _fetch_room)
                    owner_id = (rdata.get("rooms") or [{}])[0].get("owner_id")
                    if owner_id and owner_id not in aday_ids:
                        aday_ids.append(owner_id)
                except Exception as e:
                    print(f"[keşfet] room owner hata: {e}")

        # ── 2. Rooms API'sinden büyük havuz çek — birden fazla çağrı ────
        # API her çağrıda ~20 oda döndürüyor; hedef*5 aday için N tur yapıyoruz
        HEDEF_ADAY = hedef_sayi * 5   # filtreleme sonrası yetecek kadar aday
        TURA_GIDEN = 5                 # maksimum API çağrısı (5×20=100 oda)

        def _fetch_rooms_once():
            req = urllib.request.Request(
                "https://webapi.highrise.game/rooms",
                headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())

        for _tur in range(TURA_GIDEN):
            if len(aday_ids) >= HEDEF_ADAY:
                break
            try:
                rdata = await loop.run_in_executor(None, _fetch_rooms_once)
                for r in rdata.get("rooms", []):
                    oid = r.get("owner_id")
                    if oid and oid not in aday_ids:
                        aday_ids.append(oid)
            except Exception as e:
                print(f"[keşfet] rooms hata (tur {_tur+1}): {e}")
                break
            await asyncio.sleep(0.3)

        # ── 3. DB'de ID'si zaten olan adayları çıkar ──────────────────────
        yeni_ids = [uid for uid in aday_ids if uid not in db_ids_mevcut]
        print(f"[keşfet] havuz={len(aday_ids)} → DB'de yok={len(yeni_ids)}, hedef={hedef_sayi}")

        if not yeni_ids:
            await self.say("Tüm bulunan kullanıcılar zaten kayıtlı. Farklı bir link dene.", "orange")
            return

        # İlk hedef_sayi kadar yeni ID'yi paralel çek
        hedef_ids = yeni_ids[:hedef_sayi]

        async def _lookup(uid: str):
            try:
                return await self._hr_get_user_by_id(uid)
            except Exception as e:
                print(f"[keşfet] lookup hata {uid}: {e}")
                return None

        sonuclar = await asyncio.gather(*[_lookup(uid) for uid in hedef_ids])

        # ── 4. Yeni olanları DB'ye ve pending'e ekle ─────────────────────
        eklenenler = []
        for u in sonuclar:
            if u and u["username"].lower() not in db_users_mevcut:
                db_upsert(u["id"], u["username"])
                pending_add([u["username"]])
                db_users_mevcut.add(u["username"].lower())
                eklenenler.append(u["username"])

        print(f"[keşfet] ✅ {len(eklenenler)} yeni / {len(sonuclar)} lookup / {len(aday_ids)} aday")
        if eklenenler:
            await self.say(
                f"✅ {len(eklenenler)} yeni kullanıcı eklendi: {', '.join(eklenenler[:10])}"
                + (f" (+{len(eklenenler)-10} daha)" if len(eklenenler) > 10 else ""),
                "lime"
            )
        else:
            await self.say("Lookup başarısız — Highrise API geçici hata vermiş olabilir.", "orange")

    async def _cmd_tip_all(self, admin_user: User, amount: int, gold_bar: str):
        """Odadaki herkese (bot ve admin hariç) gold gönderir; admin de almış gibi görünür."""
        try:
            users = (await self.highrise.get_room_users()).content
            # Gerçekten gold gidecekler: bot ve admin dışındakiler
            real_targets = [u for u, _ in users
                            if u.id != self._my_id and u.id != admin_user.id]
            # Görünürde toplam: admin de dahil
            gorsel_toplam = len(real_targets) + 1

            if not real_targets:
                await self.say("Odada başka kimse yok! 😅", "orange")
                return

            await self.say(
                f"🎁 {gorsel_toplam} kişiye {amount}g dağıtılıyor! Hazır mısınız? 🎉",
                "yellow"
            )
            await self.do_emote("emote-celebrate")

            basarili, hatali = 0, 0
            for u in real_targets:
                try:
                    await self.highrise.tip_user(u.id, gold_bar)
                    basarili += 1
                    await asyncio.sleep(0.3)
                except Exception as e:
                    hatali += 1
                    print(f"[tip_all] ❌ {u.username}: {e}")

            # Admini de sayıya dahil et (gerçekte gönderilmedi)
            basarili += 1

            await self.say(
                f"✅ Dağıtım tamamlandı! "
                f"Gönderilen: {basarili} kişi × {amount}g"
                + (f" | Hatalı: {hatali}" if hatali else ""),
                "lime"
            )
            await self.do_emote("emote-wave")
        except Exception as e:
            await self.say(f"Tip hatası: {e}", "red")
            print(f"[tip_all] ❌ {e}")

    async def _cmd_all_emote(self, emote_id: str):
        """Odadaki herkesi aynı emote döngüsüne sokar."""
        try:
            users = (await self.highrise.get_room_users()).content
            targets = [u for u, _ in users if u.id != self._my_id]
            if not targets:
                return
            for u in targets:
                # Varsa eski döngüyü iptal et
                old = self.user_loop_tasks.pop(u.id, None)
                if old and not old.done():
                    old.cancel()
                # Yeni döngü başlat
                task = self._start_loop_emote(u.id, emote_id)
                self.user_loop_tasks[u.id] = task
            print(f"[all_emote] ✅ {len(targets)} kişi {emote_id} döngüsüne alındı")
        except Exception as e:
            print(f"[all_emote] {e}")

    async def _cmd_tpa(self, admin_user: User):
        """Odadaki herkesi adminin yanına ışınlar."""
        try:
            users = (await self.highrise.get_room_users()).content
            admin_pos = next(
                (p for u, p in users if u.id == admin_user.id), None
            )
            if admin_pos is None or not hasattr(admin_pos, "x"):
                await self.say("Konumunuz alınamadı (AnchorPosition?). Yere basarak tekrar deneyin.", "red")
                return

            targets = [(u, p) for u, p in users
                       if u.id != self._my_id and u.id != admin_user.id]
            if not targets:
                await self.say("Odada başka kimse yok 😅", "orange")
                return

            basarili = 0
            hatali   = 0
            for i, (u, _) in enumerate(targets):
                try:
                    pos = Position(
                        admin_pos.x + (i % 3) * 0.8 - 0.8,
                        admin_pos.y,
                        admin_pos.z + (i // 3) * 0.8,
                        facing="FrontLeft",
                    )
                    await self.highrise.teleport(u.id, pos)
                    basarili += 1
                    await asyncio.sleep(0.15)  # ani flood'u önle
                except Exception as e:
                    hatali += 1
                    print(f"[tpa] {u.username} ışınlanamadı: {e}")

            if basarili:
                await self.say(
                    f"🎯 {basarili} kişi yanına toplandı! 🎉"
                    + (f" ({hatali} hata)" if hatali else ""),
                    "lime"
                )
                await self.do_emote("emote-celebrate")
            else:
                await self.say(
                    f"❌ Kimse ışınlanamadı ({hatali} hata). "
                    "Bot odada moderatör/owner yetkisine sahip olmalı.",
                    "red"
                )
        except Exception as e:
            await self.say(f"Işınlama hatası: {e}", "red")
            print(f"[tpa] {e}")

    async def _cmd_admin_help(self):
        lines = [
            f"🔐 ADMİN KOMUTLARI — {ADMIN_USERNAME}",
            "🌀 !tpa → Herkesi yanına ışınla",
            "📍 !tp → Botu yanına ışınla",
            "🎁 !tip <miktar>g → Herkese gold dağıt  (1·5·10·50·100·500·1000)",
            "🛑 !tümstop → Herkesteki emote döngüsünü durdur",
            "🔇 !sil <isim> → Kişinin emote döngüsünü durdur",
            "📢 !duyur <mesaj> → Odada duyuru yap (3 kez)",
            "📋 !ayardım → Bu listeyi göster",
            "— Normal komutlar da geçerli, cooldown yok —",
        ]
        await self.send_lines(lines, "magenta")

    async def _cmd_tp(self, user: User):
        try:
            users = (await self.highrise.get_room_users()).content
            pos   = next((p for u, p in users if u.id == user.id), None)
            if not pos:
                await self.say(f"{user.username}, seni bulamadım 🤔", "orange")
                return
            target = Position(pos.x + 0.5, pos.y, pos.z + 0.5, facing="FrontRight")
            await self.highrise.teleport(self._my_id, target)
            await self.say(
                random.choice([
                    f"Tap! Yanındayım {user.username} ✨",
                    f"Işınlandım! Merhaba {user.username} 😄",
                    f"Hazır! Yanındayım {user.username} 🎯",
                ]),
                "magenta"
            )
            await self.do_emote("emote-wave", user.id)
        except Exception as e:
            await self.say(f"Işınlanamadım: {e}", "red")

    # ============================================================
    # ARKAPLAN GÖREVLERİ
    # ============================================================
    async def _idle_emote_loop(self):
        while True:
            await asyncio.sleep(random.uniform(IDLE_EMOTE_MIN, IDLE_EMOTE_MAX))
            try:
                await self.do_emote(random.choice(ALL_EMOTES))
            except Exception as e:
                print(f"[idle_emote] {e}")

    async def _auto_invite_loop(self):
        """
        Her 3 dakikada bir çalışır:
        1. Pending listesinde ID'si eksik olan kullanıcıların ID'lerini
           asyncio.gather ile PARALEL olarak çözer (30 kişi/tur).
        2. users_db'deki herkese toplu invite gönderir.
        """
        INVITE_INTERVAL = 3 * 60   # 3 dakika
        BATCH_PER_CYCLE = 30       # Paralel ID çözümü başına kişi sayısı

        await asyncio.sleep(60)

        while True:
            db  = db_all_users()
            now = time.time()

            # ── 1. EKSİK ID'LERİ PARALEL OLARAK ÇÖZ ──────────────────────
            db_usernames_lower = {v.get("username", "").lower() for v in db.values()}
            pending            = pending_load()
            bilinmeyenler      = [u for u in pending if u.lower() not in db_usernames_lower]

            if bilinmeyenler:
                hedef = bilinmeyenler[:BATCH_PER_CYCLE]
                print(f"[repair] 🔍 {len(bilinmeyenler)} eksik ID, bu tur {len(hedef)} paralel çözülüyor...")

                async def _resolve(username: str):
                    try:
                        uid = await self._hr_get_user_id(BOT_TOKEN, username)
                        if uid:
                            db_upsert(uid, username)
                            print(f"[repair] ✅ {username} → {uid}")
                            return True
                    except Exception as e:
                        print(f"[repair] ⚠️ {username}: {e}")
                    return False

                sonuclar = await asyncio.gather(*[_resolve(u) for u in hedef])
                bulunan  = sum(1 for r in sonuclar if r)
                print(f"[repair] 📊 {bulunan}/{len(hedef)} ID çözüldü.")
                db = db_all_users()   # güncel DB'yi yükle

            # ── 2. TOPLU INVITE ────────────────────────────────────────────
            davet_mesajlari = [
                "Seni özledik! Gel bir uğra 🎉",
                "Merhaba! Harika vakit geçirebilirsin 👋",
                "Kapımız her zaman açık 🚪✨",
                "Eğlence sürüyor, gel katıl! 💃",
            ]
            hedef_ids = [uid for uid, entry in db.items() if uid != self._my_id]

            if hedef_ids:
                batch_size = 50
                toplam = 0
                for i in range(0, len(hedef_ids), batch_size):
                    batch  = hedef_ids[i:i + batch_size]
                    mesaj  = random.choice(davet_mesajlari)
                    try:
                        await self.highrise.send_message_bulk(
                            user_ids=batch,
                            content=mesaj,
                            message_type="invite",
                            room_id=ROOM_ID,
                        )
                    except Exception as e:
                        print(f"[auto_invite] ⚠️ Batch {i//batch_size+1}: {e}")
                    toplam += len(batch)
                    for uid in batch:
                        db_update_field(uid, "last_invited", now)
                    await asyncio.sleep(2.0)
                print(f"[auto_invite] ✅ {toplam} kişiye invite gönderildi.")
            else:
                print("[auto_invite] ℹ️ Davet edilecek kimse yok.")

            await asyncio.sleep(INVITE_INTERVAL)

    def cancel_tasks(self):
        # Yeni mesaj gelmesini engelle
        self._shutting_down = True
        # Emote döngülerini durdur
        for task in list(self.user_loop_tasks.values()):
            task.cancel()
        self.user_loop_tasks.clear()
        # Diğer arkaplan görevleri
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()


# ============================================================
# RUNNER
# ============================================================
async def run_forever():
    if not BOT_TOKEN or BOT_TOKEN == "BURAYA_BOT_TOKEN_YAZILACAK":
        print("❌ BOT_TOKEN girilmemiş! Lütfen kodun başındaki BOT_TOKEN kısmını doldurun.")
        return
    if not ROOM_ID or ROOM_ID == "BURAYA_ODA_ID_YAZILACAK":
        print("❌ ROOM_ID girilmemiş! Lütfen kodun başındaki ROOM_ID kısmını doldurun.")
        return

    # Backoff: multilogin döngüsünü önlemek için asla 30sn'nin altına düşme.
    # Highrise eski oturumu kapatmak için ~60-90 sn'ye ihtiyaç duyar.
    MIN_BACKOFF = 90
    MAX_BACKOFF = 300
    backoff = MIN_BACKOFF
    bot: Optional[HighriseBot] = None
    while True:
        try:
            bot = HighriseBot()
            oda_adi = ROOM_NAME or ROOM_ID
            print(f"🚀 Bot başlatılıyor → {oda_adi}")
            await highrise_main([BotDefinition(bot, ROOM_ID, BOT_TOKEN)])
            # Normal bağlantı kapanması (multilogin dahil) — backoff sıfırlama!
            print("⚠️ Bağlantı düştü, yeniden bağlanılıyor...")
        except KeyboardInterrupt:
            print("👋 Kapatılıyor...")
            break
        except Exception as e:
            print(f"💥 Hata: {e}")
        finally:
            if bot:
                bot.cancel_tasks()
                bot = None
        print(f"⏳ {backoff} sn sonra tekrar deneniyor...")
        await asyncio.sleep(backoff)
        # Her denemede biraz arttır, MAX_BACKOFF'ta tut
        backoff = min(int(backoff * 1.4), MAX_BACKOFF)


if __name__ == "__main__":
    try:
        asyncio.run(run_forever())
    except KeyboardInterrupt:
        pass
