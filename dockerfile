# ใช้ Python เป็น Base Image
FROM python:3.13-slim

# ติดตั้ง Git, Node.js และ npm
RUN apt-get update && \
    apt-get install -y git curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# สร้าง virtual environment สำหรับ Python
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

# คัดลอกไฟล์ requirements
COPY requirements.txt requirements.txt

# ติดตั้ง dependencies พร้อม python-dotenv
RUN pip install --no-cache-dir -r requirements.txt && pip install python-dotenv

# คัดลอกไฟล์ทั้งหมด (รวม .env)
COPY ./ /src
WORKDIR /src

# ติดตั้ง Node.js dependencies
COPY package.json ./
RUN npm install --production

# รวบรวม static files (Django)
ENV PORT=3000
RUN python manage.py collectstatic --noinput

# โหลด environment variables จาก .env
ENV DJANGO_DEBUG_FALSE=1

RUN python manage.py migrate

# รันแอป Django ด้วย Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "Eduflow.wsgi:application"]
