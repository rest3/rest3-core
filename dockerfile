FROM python:2.7.12-alpine
MAINTAINER Joe Truncale <jtruncale@apprenda.com>
RUN apk update; mkdir /root/ierepo; mkdir /root/ierepo/staging
COPY . /root/ierepo
RUN python -m pip install --update pip; pip install -r /root/ierepo/requirements.txt
ENV REDIS_HOST redis
CMD ["python", "/root/ierepo/rest3API.py"]
EXPOSE 8080