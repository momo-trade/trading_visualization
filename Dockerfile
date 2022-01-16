FROM python:3.9

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN mkdir -p /usr/src/python_env

RUN apt update && apt install -y \
    vim \
    iputils-ping \
    net-tools \
    git \
    cron \
    build-essential \
    wget \
    procps

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -zxvf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && make install

COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt