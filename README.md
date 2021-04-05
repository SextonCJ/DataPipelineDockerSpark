# Overview

This project is based on the idea of collecting events from a restaurant app. The app allows a user to create a profile, login, search for menus and then order them from restaurants who will deliver them.  

This analysis looks at user adoption with the goal of improving use of the app by examining  

- When people login and use the app
- What kind of menus they search for
- What kinds of food are ordered
- What kinds of reviews are given  
  
The data pipeline uses the following tools:

- kafka to store topics
- flask to run a python web app (restaurant_api.py)
- bench to generate ~42,000 events
- spark streaming to read the events and store in hive
- hadoop (cloudera) as the distributed storage
- hive to store the table schemas
- presto to run queries    
  
The goal is to represent something approaching large volumes of usage. It takes approximately 5 minutes to generate ~42,000 events using Bench, running on a 2 VCPU server with 3.25 GB of memory.

# Generating Events
The overall system is designed to generate events that reflect real life usage, this is done using Bench and a web app written in python. Bench is used to call events with different query strings and with differing volumes, for example there are more calls to 3 star reviews than 5 star reviews. The python web app is designed to populate the same events with different weighted fields, e.g.

- Accepting different parameters on the query string (e.g. Type of food searched for)
- The field for capturing event date is weighted towards evenings and weekends
- the field for capturing whether a user used a coupon when ordering food is weighed towards the value "No"
- the same pool of userid's is randomly selected from to generate cross usage

# Report

The report of the data analysis can be read in Report.md  

Please note that the web app restaurant_api.py creates some random elements (UIDs, dates, reviews etc.) so your results will not reflect the results shown in the report, however general ratios will be the same as will total counts of events.

# Files

|File Name                 | Description                                                                                      |
|--------------------------|--------------------------------------------------------------------------------------------------|
|scripts/setup.sh          |Creates topics in kafka, installs python module in mids, creates tables in hive                   |
|scripts/flask.sh          |Runs flask restaurant_api web app                                                                 |
|scripts/spark0.sh         |Runs spark streaming servive to collect general events                                            |
|scripts/spark1.sh         |Runs spark streaming servive to collect order specific events                                     |
|scripts/bench.sh          |Runs bench commands for multiple api calls (~42,000)                                              |
|scripts/bench1.sh         |Calls exactly one instance of each event - for testing only                                      |
|scripts/restaurant_api.py |Python script (app) to generate events, is run by flask. This is the menu app                     |
|instructions.md           |General Instructions to setup the pipeline (important parts are repeated in this file under Set Up|

# Set Up

Scripts have been created to make setup easier, however some use of docker is still required. All scripts are held in the scripts directory. 

#### 1.Login in to the server and navigate to the project scripts directory

`cd ~/<project dir>/scripts`

#### 2. start docker cluster, after checking it is not actually running

```
docker-compose ps
docker-compose up -d
```

#### 3. Run the setup.sh script which creates the kafka events and installs libraries on the mids container for generating usernames

`./setup.sh`  
  
The setup.sh script runs the following commands:

```
docker-compose exec kafka kafka-topics --create --topic menu_app_events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181  
docker-compose exec cloudera hive -f /<project dir>/scripts/create_tables.sql  
docker-compose exec mids pip install random-username  
```  
  
The create_tables.sql script creates the external tables in hive that will be populated by the spark streaming scripts and then accessed by Presto at the end of the pipeline.  

Once setup is complete, the app is run against a set of test data, spark streaming is used to capture the events and write to a parquet file on hdfs. Again scripts have been written to make the running of these services easier. Using tmux or separate console windows, the following services need to be run in order and concurrently.   
  
```
./flask.sh
./spark0.sh
./spark1.sh
./bench.sh
```

##### ./flash.sh - runs the command to spin up a flask app server running the restaurant_api.py file
`docker-compose exec mids env FLASK_APP=/w205/<project dir>/scripts/restaurant_api.py flask run --host 0.0.0.0`  

#### ./spark0.sh and spark1.sh - run the spark scripts which read in events from kafka and write (append) to a parquet file on cloudera  
There are two spark scripts as there are two distinct schemas (and hive tables) being written to. Each script can be run independently and will listen for the same topic but filtering for the different event types. This is an area that could potentially be refactored where there is only one streaming service, or there are different kafka topics listening for different event structures.

#### ./bench.sh - runs the bench commands to call the restaurant_api. These are logged to kafka, read by spark streaming and later queried in Presto.  
The restaurant_api.py app has been written so that some calls take arguments from the query string, whereas others do not. Examples of bench commands from the bench.sh script are given below:  

```
docker-compose exec mids ab -n 8291 -H "Host: user1.comcast.com"  http://localhost:5000/login0
docker-compose exec mids ab -n 367 -H "Host: user1.comcast.com"  http://localhost:5000/create_profile
docker-compose exec mids ab -n 2125 -H "Host: user1.comcast.com"  http://localhost:5000/menu_search?menu=Mexican
```

# Presto
Once the bench script has completed, all events will have been stored in parquet files in cloudera and can be read from Presto.  

`docker-compose exec presto presto --server presto:8080 --catalog hive --schema default`  
  
Once in presto queries will be written. The Report.md file describes this analysis
