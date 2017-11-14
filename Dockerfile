FROM python:3.6.0

RUN apt-get update
RUN apt-get -y install python3-lxml
RUN pip install requests
RUN pip install lxml
RUN pip install html5lib
RUN pip install bs4
RUN pip install mailer
RUN pip install xlrd
RUN pip install arrow

