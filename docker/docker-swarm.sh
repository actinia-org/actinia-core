# Put this node into the docker swarm
docker swarm init --advertise-addr docker0

# Create the overlay network that connects the actinia container with the redis container
docker network create \
  --driver overlay \
  --subnet 172.20.128.0/24 \
  --gateway 172.20.128.99 \
  backend

# Inspect the backend network
docker network inspect backend

# to have a local actinia-core image, run
docker-compose build

# Run it
docker stack deploy -c docker-swarm.yml actinia_swarm

# List the service
docker service ls
# List infos about each docker run of the swarm
docker service ps actinia_swarm_actinia
docker service ps actinia_swarm_redis

# Remove the stack
# outcommented, otherwise this script is useless ;)
# docker stack rm actinia_swarm
# docker swarm leave --force

# Remove the overlay network
# outcommented, because removing stack will already remove network
# docker network rm backend
