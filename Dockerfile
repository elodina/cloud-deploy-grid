FROM centos:7
RUN yum -y install epel-release
RUN yum -y update
RUN yum -y install -y curl ansible unzip wget openssh-clients python-pip expect tcping
RUN pip install retrying boto jinja2 six==1.8.0 flask flask-restful peewee requests
RUN wget -q http://repo.elodina.s3.amazonaws.com/terraform.zip -O terraform.zip && unzip terraform.zip -d /usr/bin
RUN wget -q https://releases.hashicorp.com/packer/0.8.6/packer_0.8.6_linux_amd64.zip -O packer.zip && unzip -o packer.zip -d /usr/sbin
RUN mkdir -p /grid
RUN echo "eval \$(ssh-agent)" >> ~/.bashrc
WORKDIR /grid
