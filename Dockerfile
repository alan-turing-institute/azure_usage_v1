FROM ubuntu:latest

# Python 3 and pip
RUN apt-get update \
  && apt-get install -y python3

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# Installing python libraries
COPY requirements.txt /
RUN pip install -r /requirements.txt && rm -rf ~/.cache/pip /requirements.txt

RUN apt-get autoclean

RUN mkdir webapp
WORKDIR webapp
ADD azure_usage azure_usage

ADD RUN.sh .
RUN chmod +x RUN.sh

ADD UPDATES.txt .
ADD README.md .

# Adding data
ADD data data

# launch the webapp
CMD ["/webapp/RUN.sh", "5006"]
