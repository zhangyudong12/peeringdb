FROM python:3.7

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app

#CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
