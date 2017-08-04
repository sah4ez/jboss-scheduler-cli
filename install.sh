#!/usr/bin/env bash

mkdir -p $HOME/.local/bin/scheduler
cp *.py $HOME/.local/bin/scheduler
cp lxml-3.6.0.tar.gz $HOME/.local/bin/scheduler/
cp lxml-3.5.0b1.tar.gz $HOME/.local/bin/scheduler/
if [ -f template.xml ]
then
    cp template.xml $HOME/.local/bin/scheduler
fi

installed=$(dpkg --get-selections | egrep  "libxslt|libxml2" | wc -l)
if [ $installed -eq 0 ]
then
    sudo apt-get update
    sudo apt-get install -y libxml2-dev libxslt-dev
    tar -zxf $HOME/.local/bin/scheduler/lxml-3.6.0.tar.gz --directory $HOME/.local/bin/scheduler
    tar -zxf $HOME/.local/bin/scheduler/lxml-3.5.0b1.tar.gz --directory $HOME/.local/bin/scheduler

    cd $HOME/.local/bin/scheduler/lxml-3.6.0/
    python3.6 $HOME/.local/bin/scheduler/lxml-3.6.0/setup.py build_ext -i  -I /usr/include/libxml2
    cd $HOME/.local/bin/scheduler/lxml-3.5.0b1/
    pip3 install -r requirements.txt
    python3.6 $HOME/.local/bin/scheduler/lxml-3.6.0/setup.py build_ext -i  -I /usr/include/libxml2

fi

PATH_TO_EXECUTE=$HOME/bin/scheduler-tool
if [ -f $PATH_TO_EXECUTE ]
then
    rm $PATH_TO_EXECUTE
fi

ln -s $HOME/.local/bin/scheduler/scheduler.py $PATH_TO_EXECUTE
chmod +x $PATH_TO_EXECUTE
