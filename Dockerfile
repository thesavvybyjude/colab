FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN useradd --create-home --uid 1000 colab

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Collect static files at build time; the secret here is a placeholder used only for this step.
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput

USER colab
EXPOSE 8000

# Migrate, then serve. Two workers keeps memory low on a small server.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --access-logfile -"]
