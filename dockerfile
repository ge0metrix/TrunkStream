FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get -y update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY . /code

expose 8000

#CMD ["uvicorn", "trunkstream.app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4", "--log-config", "logconfig.yml"]