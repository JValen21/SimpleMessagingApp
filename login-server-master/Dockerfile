FROM python:bullseye

RUN apt-get -y update && apt-get -y install tzdata less vim sqlite3 && apt-get clean && rm -rf /var/lib/apt/lists/* && rm -f /etc/localtime && ln -s /usr/share/zoneinfo/Europe/Oslo /etc/localtime && echo Europe/Oslo > /etc/timezone
RUN pip install flask apsw pygments
RUN adduser --system tiny
USER tiny
RUN cd /home/tiny && git clone https://git.app.uib.no/inf226/22h/tiny-server.git
WORKDIR /home/tiny/tiny-server
RUN echo 'python -c "from app import app; app.run(host=\"0.0.0.0\")"' > runit.sh
EXPOSE 5000
CMD ["python", "-c", "from app import app; app.run(host='0.0.0.0')"]

