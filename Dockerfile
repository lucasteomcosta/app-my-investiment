FROM python:3.9

COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# running migrations
RUN python manage.py migrate

EXPOSE 80

# gunicorn
#CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]

