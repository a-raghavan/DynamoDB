sudo apt update
sudo apt -y install python3-pip
sudo apt install default-jdk
sudo apt install default-jre

pip3 install grpcio
pip3 install grpcio-tools
pip3 install kazoo
pip3 install leveldb

yes | sudo apt-get -y install tmux
yes | sudo apt-get -y install vim


wget https://dlcdn.apache.org/zookeeper/zookeeper-3.7.1/apache-zookeeper-3.7.1-bin.tar.gz
tar -xvf apache-zookeeper-3.7.1-bin.tar.gz