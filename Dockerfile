FROM gliderlabs/alpine:3.4

RUN apk --no-cache add \
    python \
    python-dev \
    py-pip \
    build-base

WORKDIR /app

COPY . /app
RUN pip install -r /app/requirements.txt

EXPOSE 5000
