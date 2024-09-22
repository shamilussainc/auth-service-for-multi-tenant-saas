FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./alembic /code/alembic
COPY alembic.ini /code/alembic.ini
COPY ./app /code/app

CMD [ "fastapi", "run", "app/main.py", "--port", "80" ]
