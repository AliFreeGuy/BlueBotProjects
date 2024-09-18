FROM python:3.8

WORKDIR /compressorbot

ADD requirements.txt .

RUN apt-get update && \
    apt-get install -y tzdata && \
    apt-get install -y ffmpeg && \
    pip install --upgrade pip

RUN pip install -r requirements.txt

RUN python -m pip install --upgrade pip
RUN pip install --upgrade wheel
RUN pip install --upgrade setuptools
RUN pip install -U tgcrypto
RUN pip install https://github.com/KurimuzonAkuma/pyrogram/archive/v2.1.22.zip --force-reinstall


COPY . .

CMD ["python3", "main.py"]
