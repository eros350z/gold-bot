#!/usr/bin/env python3
"""
Gold Analysis Telegram Bot
يرسل تحليل الذهب يومياً قبل جلسة لندن ونيويورك
"""

import requests
import schedule
import time
from datetime import datetime
import pytz

# ==========================================
# إعدادات البوت - عدّل هنا فقط
# ==========================================
BOT_TOKEN  = "8764834987:AAHZ_dC1TmEfTO-Pbmd1AyZQcuHsNFQZy64"
CHAT_ID    = "6652508619"
TIMEZONE   = "Asia/Kuwait"   # توقيت الكويت

# ==========================================
# إعدادات الجلسات (بتوقيت الكويت)
# ==========================================
LONDON_HOUR   = 9
LONDON_MIN    = 45
NY_HOUR       = 15
NY_MIN        = 45

# ==========================================
# جلب سعر الذهب الحالي
# ==========================================
def get_gold_price():
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        prev  = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
        change = price - prev
        pct    = (change / prev) * 100
        return round(price, 2), round(change, 2), round(pct, 2)
    except:
        return None, None, None

# ==========================================
# حساب مستويات SL و TP تلقائياً
# ==========================================
def calc_levels(price, direction="up"):
    sl_pct  = 0.007   # 0.7% وقف خسارة
    tp1_pct = 0.008   # TP1
    tp2_pct = 0.015   # TP2
    tp3_pct = 0.022   # TP3

    if direction == "up":
        sl  = round(price * (1 - sl_pct), 2)
        tp1 = round(price * (1 + tp1_pct), 2)
        tp2 = round(price * (1 + tp2_pct), 2)
        tp3 = round(price * (1 + tp3_pct), 2)
        trade = "شراء 📈"
    else:
        sl  = round(price * (1 + sl_pct), 2)
        tp1 = round(price * (1 - tp1_pct), 2)
        tp2 = round(price * (1 - tp2_pct), 2)
        tp3 = round(price * (1 - tp3_pct), 2)
        trade = "بيع 📉"

    sl_dist  = abs(price - sl)
    tp1_dist = abs(tp1 - price)
    rr = round(tp1_dist / sl_dist, 1) if sl_dist > 0 else 0

    return sl, tp1, tp2, tp3, rr, trade

# ==========================================
# تحديد اتجاه السوق بناءً على الحركة
# ==========================================
def get_direction(change):
    if change is None:
        return "up", "صاعد 📈", "محايد"
    if change > 5:
        return "up",   "صاعد قوي 📈",  "ترند صاعد واضح"
    elif change > 0:
        return "up",   "صاعد 📈",       "ميل صاعد"
    elif change < -5:
        return "down", "هابط قوي 📉",   "ترند هابط واضح"
    else:
        return "down", "هابط 📉",       "ميل هابط"

# ==========================================
# جلب الأخبار المهمة (ثابتة حالياً)
# ==========================================
def get_news(session):
    if session == "london":
        news = [
            "تحقق من Forex Factory لأخبار EUR وGBP",
            "راقب بيانات التضخم الأوروبي إن وجدت"
        ]
    else:
        news = [
            "بيانات البطالة الأمريكية (Jobless Claims) إن كان يوم الخميس",
            "تصريحات Fed إن وجدت — تأثير عالي على الذهب",
            "تجنب الدخول 15 دقيقة قبل وبعد الخبر"
        ]
    return news

# ==========================================
# بناء رسالة لندن
# ==========================================
def build_london_message():
    price, change, pct = get_gold_price()

    if price is None:
        price  = 0
        change = 0
        pct    = 0

    direction, dir_text, trend_reason = get_direction(change)
    sl, tp1, tp2, tp3, rr, trade = calc_levels(price, direction)
    news = get_news("london")

    kuwait_tz = pytz.timezone(TIMEZONE)
    now = datetime.now(kuwait_tz)
    date_str = now.strftime("%A %d %B %Y")

    change_str = f"+{change}" if change > 0 else str(change)
    pct_str    = f"+{pct}%" if pct > 0 else f"{pct}%"

    msg = f"""🌅 تحليل جلسة لندن
{date_str}
━━━━━━━━━━━━━━━
💛 XAUUSD | {dir_text}
السعر الحالي: {price} ({change_str} | {pct_str})
━━━━━━━━━━━━━━━

📌 التوصية: {trade}
🎯 سعر الدخول: {price}
🛑 وقف الخسارة: {sl}

✅ الأهداف:
   🥇 TP1: {tp1}
   🥈 TP2: {tp2}
   🥉 TP3: {tp3}

📊 نسبة المخاطرة: 1:{rr}

💡 أسباب التحليل:
• {trend_reason}
• السعر مقارنة بإغلاق الأمس: {change_str}
• تحقق من H4 قبل الدخول

📰 أخبار مهمة:
• {news[0]}
• {news[1]}

━━━━━━━━━━━━━━━
⏰ الجلسة: لندن (10:00 بتوقيتك)
⚠️ تحليل شخصي وليس توصية استثمارية"""

    return msg

# ==========================================
# بناء رسالة نيويورك
# ==========================================
def build_ny_message():
    price, change, pct = get_gold_price()

    if price is None:
        price  = 0
        change = 0
        pct    = 0

    direction, dir_text, trend_reason = get_direction(change)
    sl, tp1, tp2, tp3, rr, trade = calc_levels(price, direction)
    news = get_news("ny")

    kuwait_tz = pytz.timezone(TIMEZONE)
    now = datetime.now(kuwait_tz)
    date_str = now.strftime("%A %d %B %Y")

    change_str = f"+{change}" if change > 0 else str(change)
    pct_str    = f"+{pct}%" if pct > 0 else f"{pct}%"

    msg = f"""🌆 تحليل جلسة نيويورك
{date_str}
━━━━━━━━━━━━━━━
💛 XAUUSD | {dir_text}
السعر الحالي: {price} ({change_str} | {pct_str})
━━━━━━━━━━━━━━━

📌 التوصية: {trade}
🎯 سعر الدخول: {price}
🛑 وقف الخسارة: {sl}

✅ الأهداف:
   🥇 TP1: {tp1}
   🥈 TP2: {tp2}
   🥉 TP3: {tp3}

📊 نسبة المخاطرة: 1:{rr}

💡 أسباب التحليل:
• {trend_reason}
• جلسة لندن أغلقت على: {change_str}
• راجع مستويات الدعم والمقاومة على H1

📰 أخبار أمريكية مهمة:
• {news[0]}
• {news[1]}
• {news[2]}

━━━━━━━━━━━━━━━
⏰ الجلسة: نيويورك (4:00 مساءً بتوقيتك)
⚠️ تحليل شخصي وليس توصية استثمارية"""

    return msg

# ==========================================
# إرسال رسالة تيليغرام
# ==========================================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            print(f"✅ رسالة أُرسلت بنجاح | {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"❌ خطأ في الإرسال: {r.text}")
    except Exception as e:
        print(f"❌ استثناء: {e}")

# ==========================================
# وظائف الجدولة
# ==========================================
def is_weekday():
    from datetime import datetime
    import pytz
    kuwait_tz = pytz.timezone(TIMEZONE)
    now = datetime.now(kuwait_tz)
    return now.weekday() < 5  # 0=Monday, 4=Friday

def send_london():
    if not is_weekday():
        print("⏸️ الويك اند - لا إرسال")
        return
    print("📤 إرسال تحليل لندن...")
    msg = build_london_message()
    send_telegram(msg)

def send_ny():
    if not is_weekday():
        print("⏸️ الويك اند - لا إرسال")
        return
    print("📤 إرسال تحليل نيويورك...")
    msg = build_ny_message()
    send_telegram(msg)

# ==========================================
# اختبار فوري - يرسل الرسالتين الآن
# ==========================================
def test_now():
    print("🧪 اختبار — إرسال رسالة لندن...")
    send_london()
    time.sleep(2)
    print("🧪 اختبار — إرسال رسالة نيويورك...")
    send_ny()

# ==========================================
# تشغيل البوت
# ==========================================
if __name__ == "__main__":
    import sys

    print("🤖 Gold Analysis Bot — شغال")
    print(f"📅 التوقيت: {TIMEZONE}")
    print(f"🇬🇧 لندن: {LONDON_HOUR:02d}:{LONDON_MIN:02d}")
    print(f"🇺🇸 نيويورك: {NY_HOUR:02d}:{NY_MIN:02d}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # لو حطيت "test" يرسل الرسائل فوراً للتجربة
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_now()
        sys.exit(0)

    # جدولة الرسائل اليومية
    schedule.every().day.at(
        f"{LONDON_HOUR:02d}:{LONDON_MIN:02d}"
    ).do(send_london)

    schedule.every().day.at(
        f"{NY_HOUR:02d}:{NY_MIN:02d}"
    ).do(send_ny)

    print("✅ البوت جاهز وينتظر المواعيد...")
    print("💡 لاختبار فوري: python gold_bot.py test")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    while True:
        schedule.run_pending()
        time.sleep(30)
