# 🌟 پروژه پیشرفته سیستم جستجو و احراز هویت با قابلیت‌های امنیتی

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Elasticsearch](https://img.shields.io/badge/Elasticsearch-005571?style=for-the-badge&logo=elasticsearch&logoColor=white)](https://www.elastic.co/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)](https://jwt.io/)
[![UnitTest](https://img.shields.io/badge/UnitTest-FA7343?style=for-the-badge&logo=python&logoColor=white)](#)

## 🚀 ویژگی‌های کلیدی سیستم

### 🔒 سیستم احراز هویت پیشرفته
- **امن**: احراز هویت با کد یکبار مصرف(OTP) مبتنی بر زمان (TOTP)
- **رمزنگاری حرفه‌ای**: ذخیره‌سازی هش شده کدها در Redis
- **مدیریت نشست**: استفاده از JWT با مکانیزم HTTPOnly Cookie + CSRF Protection
- **امنیت لایه‌ای**: جداسازی کامل لایه احراز هویت از دسترسی فرانت‌اند
- **انقضای خودکار**: کدهای OTP با زمان انقضای پویا (60-120 ثانیه)
#

### 🔍 موتور جستجوی هوشمند فارسی
- **پردازش**: آنالایزر سفارشی‌سازی شده برای زبان فارسی
- **تشخیص خودکار**: تشخیص و اصلاح خطاهای املایی و تایپی
- **عملکرد بالا**: پاسخگویی در کمتر از 50ms برای 1 میلیون رکورد(محصول یا سند)
- **فیلتر پیشرفته**: پشتیبانی از فیلترهای ترکیبی و رنج‌های داینامیک
  #

### 🧪 تست‌نویسی
- استفاده از فریم‌ورک رسمی <img src="https://img.shields.io/badge/UnitTest-FA7343?style=for-the-badge&logo=python&logoColor=white" alt="UnitTest" width="80"/>
 در تست‌های backend
- پوشش تست برای ماژول احراز هویت، کش Redis و عملکرد جستجو
- قابل اجرا با دستور:
```bash
docker-compose exec django python manage.py test
```


---


### 📽 نمایش عملکرد سیستم

[![VIDEO](https://img.shields.io/badge/VIDEO-FF0000?style=for-the-flat&logo=film&logoColor=white)](https://example.com/video-demo)


---
## 🛠 راه‌اندازی و مدیریت پروژه با Docker

#### اجرای پروژه
```bash
docker-compose up --build
```

#### توقف موقت سرویس‌ها (حفظ داده‌ها)
```bash
docker-compose stop
```

#### توقف و حذف کانتینرها (حذف داده‌ها)
```bash
docker-compose down
```

#### توقف و حذف کامل (حذف کانتینرها و حجم‌ها)
```bash
docker-compose down --remove-orphans --volumes
```


#### اجرای دستورات در کانتینر django
```bash
docker-compose exec django [command]
```

#### راه‌اندازی مجدد سرویس خاص
```bash
docker-compose restart [service_name]
```
---


## 🔌 پورت‌ها و دسترسی سرویس‌ها

| سرویس             | پورت  | پروتکل | دسترسی                  | توضیحات                     |
|-------------------|-------|---------|-------------------------|-----------------------------|
| **Django App**    | 8010  | HTTP    | http://localhost:8010   | رابط اصلی برنامه            |
| **PostgreSQL**    | 54321 | TCP     | http://localhost:54321       | دسترسی مستقیم به دیتابیس    |
| **Redis**         | 6380  | TCP     | http://localhost:6380        | مدیریت حافظه موقت           |
| **Elasticsearch** | 9201  | HTTP    | http://localhost:9201   | موتور جستجو                 |
| **Kibana**        | 56012  | HTTP    | http://localhost:56012   | مانیتورینگ Elasticsearch    |





---
