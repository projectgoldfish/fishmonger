FROM centos:7
MAINTAINER Charles Zilm <ch@rleszilm.com>

RUN yum install -y epel-release
RUN yum install -y python34
RUN yum install -y python34-devel
RUN yum install -y python34-setuptools
RUN yum install -y gcc-c++

RUN update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.4 2
RUN update-alternatives --install /usr/bin/easy_install easy_install /usr/bin/easy_install-3.4 1

RUN easy_install pip

RUN pip install networkx
RUN pip install GitPython

COPY src /opt/fishmonger/src
VOLUME /opt/fishmonger/src
WORKDIR /usr/lib/python3.4/site-packages
RUN ln -s /opt/fishmonger/src fishmonger

RUN mkdir -p /src/fishmonger
VOLUME    /src/fishmonger
WORKDIR   /src/fishmonger

CMD ["bash"]