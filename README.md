
# 🌟 پروژه پیشرفته: سیستم جستجو و احراز هویت فارسی با امنیت و کارایی بالا

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-red?style=for-the-badge&logo=python&logoColor=white)](https://www.django-rest-framework.org/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)](https://jwt.io/)
[![UnitTest](https://img.shields.io/badge/UnitTest-FA7343?style=for-the-badge&logo=python&logoColor=white)](#)
[![Kibana](https://img.shields.io/badge/Kibana-E8478B?style=for-the-badge&logo=kibana&logoColor=white)](https://www.elastic.co/kibana)

---

## 🚀 ویژگی‌های کلیدی سیستم

### 🔒 سیستم احراز هویت پیشرفته
- **ورود سریع با موبایل**: ثبت‌نام و ورود فقط با شماره تلفن ایرانی
- **OTP امن با زمان انقضا**: کد یکبار مصرف TOTP با اعتبار محدود
- **استفاده از Redis**: برای ذخیره‌سازی موقت و امن OTP
- **ارسال با Celery**: ارسال OTP از طریق تسک‌های غیرهمزمان
- **JWT با کوکی HttpOnly**: مدیریت امن نشست + حفاظت CSRF

---

### 🔍 موتور جستجوی هوشمند فارسی
- **الاستیک‌سرچ نسخه 8.18.1**
- **آنالایزر سفارشی فارسی**: شامل فیلترهای `edge_ngram`، `persian_stem`، `normalization`
- **تشخیص خطای تایپی**: fuzzy search با نزدیک‌ترین نتایج به کلمه ورودی
- **ایندکس‌گذاری حرفه‌ای**: بر اساس عنوان، توضیحات، و تگ‌های فارسی و انگلیسی
- **پرفورمنس بالا**: پاسخ‌دهی زیر 100ms برای دیتاستی با بیش از 5 میلیون رکورد
- **نمایش نتایج search-as-you-type**
- **کاهش نویز متن**: حذف فاصله صفر (ZWSP) در آنالیز اولیه

---

### 🧪 تست‌نویسی
- تست یونیت با فریم‌ورک رسمی Django
- تست کامل ماژول‌های:
  - احراز هویت OTP
  - لایه کش Redis
  - عملکرد ایندکس و جستجو
- اجرای تست‌ها:
```bash
docker-compose exec django python manage.py test
```

---

### 🎬 ویدیو عملکرد سیستم

![Demo Video](https://img.shields.io/badge/DEMO%20VIDEO-ff0000?style=for-the-badge&logo=youtube&logoColor=white)


> این ویدیو نمایشی از سرعت و کارایی پروژه است که روی دیتاست با **۵ میلیون رکورد فارسی** تست شده است.



https://github.com/user-attachments/assets/5a34f669-9bc6-486a-8aa4-23acdea95217


📌 **نکات مهم در عملکرد جستجو:**

- در جستجوی اول، ممکن است چند صدم ثانیه بیشتر طول بکشد چون Elasticsearch ایندکس‌ها را warm-up کرده و کش‌سازی اولیه انجام می‌شود.
- از جستجوی دوم به بعد، نتایج در کمتر از **100ms** بازگردانده می‌شوند.
- عملکرد سیستم حتی با تایپ اشتباه یا ناقص، کلمات نزدیک و مرتبط را پیدا می‌کند (fuzzy match).

---

## 🛠 راه‌اندازی و مدیریت پروژه با Docker

### اجرای کامل پروژه:
```bash
docker-compose up --build
```

### توقف موقت سرویس‌ها:
```bash
docker-compose stop
```

### حذف کامل پروژه:
```bash
docker-compose down --remove-orphans --volumes
```

### اجرای دستورات مدیریتی:
```bash
docker-compose exec django [command]
```

### راه‌اندازی مجدد سرویس خاص:
```bash
docker-compose restart [service_name]
```

---

## 🔌 پورت‌ها و دسترسی سرویس‌ها

| سرویس             | پورت خارج از Docker | پروتکل | دسترسی                  | توضیحات                     |
|-------------------|----------------------|--------|--------------------------|-----------------------------|
| **Django App**    | 8010                 | HTTP   | http://localhost:8010    | رابط اصلی برنامه           |
| **PostgreSQL**    | 54321                | TCP    | http://localhost:54321   | دسترسی به دیتابیس          |
| **Redis**         | 6380                 | TCP    | http://localhost:6380    | حافظه کش OTP                |
| **Elasticsearch** | 9201                 | HTTP   | http://localhost:9201    | موتور جستجو                 |
| **Kibana**        | 56012                | HTTP   | http://localhost:56012   | داشبورد مانیتورینگ         |

---

## 🗂️ ساختار پروژه (Directory Structure)


```bash
├── accounts
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_forms.py
│   │   ├── test_serializers.py
│   │   └── test_views.py
│   ├── admin.py
│   ├── apps.py
│   ├── authentication.py
│   ├── forms.py
│   ├── __init__.py
│   ├── jwt.py
│   ├── managers.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── throttles.py
│   ├── urls.py
│   └── views.py
├── core
│   ├── asgi.py
│   ├── celery.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── postman
│   └── collection.json
├── products
│   ├── management
│   │   ├── commands
│   │   │   ├── create_test_products.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── documents.py
│   ├── filters.py
│   ├── __init__.py
│   ├── models.py
│   ├── pagination.py
│   ├── serializers.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── utils
│   ├── custom_fields
│   │   └── phone_number_field.py
│   ├── cache_manager.py
│   ├── __init__.py
│   └── otp.py
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── manage.py
├── README.md
├── requirements.txt
└── video.mp4
```

---

## 📄 لایسنس و نحوه استفاده

📌 **مجوز عمومی با ذکر منبع**  
استفاده از این پروژه برای مقاصد شخصی، نمونه‌کاری یا آموزشی آزاد است.  
در صورت استفاده از بخش‌هایی از کد، لطفاً لینک به مخزن GitHub یا نام سازنده (`aliazizi-code`) را ذکر نمایید.

---

👨‍💻 تهیه و توسعه توسط [aliazizi-code](https://github.com/aliazizi-code)
