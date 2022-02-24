# Installing docker 

# uninstall old versions
sudo yum remove docker \
  docker-common\
  docker-selinux \
  docker-engine

# set up the repository
sudo yum install -y yum-utils;
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo;

# install docker engine
sudo yum install docker-ce docker-ce-cli containerd.io

# start docker
sudo systemctl start docker

# hello world
sudo docker run hello-world

https://download.docker.com/linux/centos/7/x86_64/stable/Packages/docker-ce-17.03.0.ce-1.el7.centos.x86_64.rpm   