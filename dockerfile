FROM python:3.12-slim AS base
RUN apt-get -y update
RUN apt-get install ffmpeg  -y
RUN apt-get autoremove
RUN rm -rf /var/lib/apt/lists/*


FROM base AS trunkstream
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code
COPY requirements.txt /code
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./trunkstream /code/trunkstream
COPY logconfig.yml /code/logconfig.yml

#CMD ["uvicorn", "trunkstream.app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4", "--log-config", "logconfig.yml"]