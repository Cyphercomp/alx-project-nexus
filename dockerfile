FROM python:3.12-bullseye
ENV PYTHONUNBUFFERED 1

RUN mkdir /nexus

WORKDIR  /nexus

RUN pip install requirements.txt

COPY . .

EXPOSE 8000

ENTRYPOINT [ "python","manage.py","runserver","0.0.0.0:8000" ]