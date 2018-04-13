FROM python:3.6
LABEL maintainer="frederic.laurent@gmail.com"

RUN apt-get update
RUN apt-get -y install python3-lxml
RUN pip install requests
RUN pip install lxml
RUN pip install html5lib
RUN pip install bs4
RUN pip install mailer
RUN pip install xlrd
RUN pip install arrow

RUN git clone https://github.com/flrt/atom_gen.git /opt/atom_gen
RUN pip install /opt/atom_gen/dist/atom_gen-1.0.tar.gz
RUN git clone https://github.com/flrt/atom_to_rss2.git /opt/atomtorss2

WORKDIR /opt