FROM python:3.8

RUN mkdir /PKVIZ


COPY ./app.py /PKVIZ/app.py
COPY ./index.py /PKVIZ/index.py
COPY ./setup.py /PKVIZ/setup.py
COPY ./requirements.txt /PKVIZ/requirements.txt

COPY ./assets /PKVIZ/assets
COPY ./apps /PKVIZ/apps
COPY ./spark_display /PKVIZ/spark_display
COPY ./datasets /PKVIZ/datasets
COPY ./utils /PKVIZ/utils
COPY ./pkcase /PKVIZ/pkcase

WORKDIR /PKVIZ

RUN pip install -U pip setuptools wheel
RUN pip install -e .
EXPOSE 8080
CMD ["python", "index.py"]
