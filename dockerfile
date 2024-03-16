FROM python:3.11

WORKDIR /code
 
COPY ./requirements.txt /code/requirements.txt
RUN apt-get -y update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY . /code

CMD ["uvicorn", "trunkstream.app:app", "--host", "0.0.0.0", "--port", "80"]