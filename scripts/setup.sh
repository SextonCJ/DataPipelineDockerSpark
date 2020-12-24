# create menu_app_events topic
docker-compose exec kafka kafka-topics --create --topic menu_app_events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181

# create tables in hive
docker-compose exec cloudera hive -f /w205/project-3-SextonCJ/scripts/create_tables.sql

# install username generator in mids container
docker-compose exec mids pip install random-username
