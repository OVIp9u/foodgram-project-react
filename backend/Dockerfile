FROM python:3.9
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY . .
RUN pip3 install -r ./requirements.txt --no-cache-dir
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
