FROM python:3.9

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY  . /code/

ENTRYPOINT ["bash", "docker-entrypoint.sh"]
CMD ["runserver", "0.0.0.0:8080"]