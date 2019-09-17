FROM python:3

RUN apt-get update \
&& apt-get -y upgrade \
&& apt-get -y install sshpass 


WORKDIR /root
RUN pip install --no-cache-dir pyvcloud
CMD ["bash"]