FROM python:3.10.13

RUN mkdir parse
COPY entrypoint.sh /entrypoint.sh
COPY multi_tor.sh /multi_tor.sh
RUN chmod +x /entrypoint.sh
RUN chmod +x /multi_tor.sh
RUN apt-get update && apt-get install tor -y
RUN pip3 install requests[socks]
RUN pip3 install pandas==1.5.3
RUN pip3 install geopandas==0.13.2
RUN pip3 install shapely==2.0.3
RUN pip3 install pysocks==1.7.1
RUN pip3 install stem==1.8.2
RUN pip3 install fake_useragent==1.5.0
RUN pip3 install loguru

WORKDIR /parse/
ENTRYPOINT ["/entrypoint.sh"]
CMD [ ]
