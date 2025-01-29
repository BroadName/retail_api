FROM python:3.10
RUN apt-get update && apt-get install -y gosu
EXPOSE 8000
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENTRYPOINT ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]