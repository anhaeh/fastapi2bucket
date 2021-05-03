FROM python:3.8-slim

MAINTAINER Andres Haehnel <anhaeh@gmail.com>

EXPOSE 8000

WORKDIR /app

COPY . .

RUN apt update \
	&& apt install --force-yes -y git libmagic1 \
	&& pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]