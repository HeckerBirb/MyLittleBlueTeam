#!/bin/bash

git pull

while true; do
    read -p "Do you wish to redeploy MyLittleBlueTeam with these git changes? This will replace the image mylittleblueteam:latest [Y/n]: " yn
    case $yn in
        [Yy]* ) echo Deploying...; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer Y or n.";;
    esac
done
echo

CONTAINER=$(docker ps -a | grep mylittleblueteam | cut -d ' ' -f 1)
IMAGE=$(docker images | grep 'mylittleblueteam.*latest' | awk '{print $3}')

docker stop $CONTAINER && docker rm $CONTAINER
docker image rm $IMAGE

docker-compose build && docker-compose up -d && docker ps -a

CONTAINER=$(docker ps -a | grep mylittleblueteam:latest | cut -d ' ' -f 1)
docker logs -f $CONTAINER
