FROM python:3.10
EXPOSE 8000
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["sh", "-c", "cd project && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]