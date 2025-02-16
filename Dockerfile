# استفاده از نسخه کامل‌تر برای پشتیبانی از Chrome
FROM python:3.11

# تنظیم متغیرهای محیطی
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# تنظیم دایرکتوری کاری
WORKDIR /app

# نصب وابستگی‌های کروم و کروم‌درایور
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libgbm1 \
    libasound2 \
    libnss3 \
    libxss1 \
    libappindicator1 \
    fonts-liberation \
    xdg-utils \
    && apt-get clean

# دانلود و نصب Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# دانلود و نصب ChromeDriver متناسب با نسخه‌ی کروم نصب‌شده
RUN CHROMEDRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -N http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip -P /tmp/ && \
    unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# کپی کردن وابستگی‌ها و نصب آنها
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# کپی کردن سورس‌کد پروژه
COPY . /app/

# اکسپوز کردن پورت ۸۰۰۰ برای اجرای جنگو
EXPOSE 8000

# اجرای سرور جنگو
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
