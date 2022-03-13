FROM python:3.10-alpine

EXPOSE 8000

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt

COPY src/ ./

ENTRYPOINT [ "python", "./main.py" ]