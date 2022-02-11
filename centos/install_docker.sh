# Installing docker on centos
# Used for my linode server
# 2/10/22

# uninstall old versions
sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine;

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

