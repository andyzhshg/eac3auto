FROM ubuntu:18.04

MAINTAINER andyzhshg <andyzhshg@gmail.com>

RUN apt-get update

RUN apt-get install -y ffmpeg python inotify-tools

ADD entry.sh /
ADD convert.py /

RUN chmod +x entry.sh && chmod +x convert.py

ENTRYPOINT [ "/entry.sh" ]
