FROM python

WORKDIR /usr/src/blink_downloader

COPY requirements.txt main.py ./

RUN pip install -r requirements.txt

ENV BLINK_PERIOD=3600 \
    BLINK_LOCATION=/blink

CMD python main.py