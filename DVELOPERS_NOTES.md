connect to db :

`$ docker exec -it $(docker ps -qf "name=postgres") psql -U knowledge -d knowledge` 