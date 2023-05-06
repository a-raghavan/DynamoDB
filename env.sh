sudo apt update
sudo apt -y install python3-pip
pip3 install grpcio
pip3 install grpcio-tools
pip3 install kazoo
pip3 install leveldb

yes | sudo apt-get -y install tmux
yes | sudo apt-get -y install vim