FROM gboeing/osmnx:latest

WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

CMD gunicorn -t 3600 --bind :$PORT app:app