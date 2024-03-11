#!/bin/bash
 
base_socks_port=9080 # Номер первого прокси-порта Tor
base_control_port=8148 # Номер первого управляющего порта Tor

# Число процессов Tor, которые мы будем использовать
if [ -n $@ ]; then
    max_tor_num=$@
else
    max_tor_num=10
fi

max_attempts_num=10 # Максимальное число попыток получить IP
 
rm -rf data_tor 
# killall tor

# Создаем директорию tor_data для всех процессов Tor
if [ ! -d "tor_data" ]; then
    mkdir "tor_data"
fi
 
for tor_num in $(seq 0 $max_tor_num); do
 
    socks_port=$((base_socks_port+tor_num))
    control_port=$((base_control_port+tor_num))
    # Создаем директорию для текущего процесса Tor
    if [ ! -d "tor_data/tor$tor_num" ]; then
        echo "Creating directory data/tor$tor_num"
        mkdir "tor_data/tor$tor_num"
    fi
 
    # Запускаем Tor
    echo "Running Tor: control port = $control_port socks port = $socks_port"
    tor --RunAsDaemon 1 --CookieAuthentication 1 --HashedControlPassword "16:D3B3B714E617EC2A608D621D5636FDF855F043E86FC9C7D759A461EE64" -ControlPort $control_port --PidFile $PWD/tor_data/tor$tor_num.pid --SocksPort $socks_port --DataDirectory $PWD/tor_data/tor$tor_num
 
done
