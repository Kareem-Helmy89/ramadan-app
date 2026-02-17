# تطبيق تنسيق الشخصيات بالذكاء الاصطناعي - رمضان

تطبيق ويب بسيط لتنسيق شخصيات كارتونية باستخدام الذكاء الاصطناعي مع تصميم يحمل أجواء رمضان.

## المتطلبات

- Python 3.8+
- MySQL 5.7+ أو MariaDB
- XAMPP (أو أي خادم محلي)

## التثبيت

### 1. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 2. إعداد قاعدة البيانات

1. افتح MySQL (من خلال phpMyAdmin أو سطر الأوامر)
2. قم بتشغيل ملف `schema.sql` لإنشاء قاعدة البيانات والجداول

أو من سطر الأوامر:
```bash
mysql -u root -p < schema.sql
```

### 3. إعداد ملف البيئة

انسخ ملف `.env.example` إلى `.env` وعدّل إعدادات قاعدة البيانات:

```env
DB_HOST=localhost
DB_NAME=ramadan_app
DB_USER=root
DB_PASSWORD=your_password
```

### 4. إضافة الصورة الأصلية

ضع صورة الشخصية الأصلية في:
```
static/images/original-character.jpg
```

يمكنك استخدام الصورة المرفقة (Jerry Mouse) أو أي صورة شخصية كارتونية أخرى.

### 5. تشغيل التطبيق

```bash
python app.py
```

افتح المتصفح على: `http://localhost:5000`

## هيكل المشروع

```
ramadan/
├── app.py                 # تطبيق Flask الرئيسي
├── requirements.txt       # مكتبات Python المطلوبة
├── schema.sql            # مخطط قاعدة البيانات
├── .env.example          # مثال لملف الإعدادات
├── templates/
│   └── index.html        # صفحة HTML الرئيسية
├── static/
│   ├── css/
│   │   └── style.css     # ملف التنسيقات
│   ├── js/
│   │   └── main.js       # ملف JavaScript
│   └── images/
│       └── original-character.jpg  # صورة الشخصية الأصلية
└── README.md
```

## دمج واجهة برمجة تطبيقات توليد الصور

في ملف `app.py`، ابحث عن الدالة `call_ai_image_api()` وأضف كود الاتصال بواجهة برمجة التطبيقات المفضلة لديك:

### مثال: OpenAI DALL-E

```python
import openai

def call_ai_image_api(prompt):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Image.create(
        prompt=f"cartoon mouse character, {prompt}, Ramadan theme, high quality, detailed",
        n=1,
        size="512x512"
    )
    return response['data'][0]['url']
```

### مثال: Replicate (Stable Diffusion)

```python
import replicate

def call_ai_image_api(prompt):
    output = replicate.run(
        "stability-ai/stable-diffusion:...",
        input={
            "prompt": f"cartoon mouse character, {prompt}, Ramadan theme, high quality",
            "width": 512,
            "height": 512
        }
    )
    return output[0]
```

## المميزات

- ✅ تصميم رمضاني جميل مع ألوان دافئة
- ✅ دعم كامل للغة العربية واتجاه RTL
- ✅ خطوط عربية أنيقة (Aref Ruqaa, Tajawal)
- ✅ معرض للتصاميم المولدة حديثاً
- ✅ واجهة مستخدم سلسة وسريعة الاستجابة
- ✅ جاهز لدمج واجهات برمجة تطبيقات توليد الصور

## الملاحظات

- التطبيق حالياً يستخدم رابط صورة وهمية (placeholder) حتى يتم دمج واجهة برمجة التطبيقات الفعلية
- تأكد من إضافة صورة الشخصية الأصلية في `static/images/original-character.jpg`
- يمكنك تخصيص الألوان من ملف `style.css` باستخدام المتغيرات CSS

## الرخصة

هذا المشروع مفتوح المصدر ويمكن استخدامه بحرية.
