FROM python:3.13.1

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python", "panel_project/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]