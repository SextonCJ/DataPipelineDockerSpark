# Instructions

Follow the steps below to setup the project for data gathering and querying

## Step 1: Start docker cluster
```
docker-compose up -d
```

## Step 2: Run Setup

This script initializes a few modules that need to be run before we begin broadcasting/gathering data. This includes creating our topic, creating tables in hive, and installing a module for creating usernames

```
./setup.sh
```

## Step 3: Broadcasting and Gathering Data

This step may require either starting 4 terminals, or using `tmux` to have 4 windows in parallel. The following scripts should be run in the order they are listed


### Session 1 - flask.sh

This file runs the web server

```
./flask.sh
```

###  Session 2 - bench.sh

This script runs each event. While you can run `bench_1.sh` to test the functionality of this step, `bench.sh` will run 1000s of events. It will take roughly 5 minutes for `bench.sh` to generate all 42,452 events

```
./bench.sh
```

### Sessions 3 and 4 - spark0.sh and spark1.sh

These two spark streaming scripts should run in parallel and will store the `menu_app_events` and `menu_app_orders` events

```
./spark0.sh
./spark1.sh
```
""

## Step 4: Querying the data

Once these steps are done, the data is ready to be queried and viewed. We do this through presto. In a new window, run the following 


```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default
```

The tables should then be ready to be viewed and queried. Run the following simple queries to see the results:
```
show tables;
select count(*) from menu_app_events;
select * from menu_app_events limit 5;

select count(*) from menu_app_orders;
select * from menu_app_orders limit 5;
```

- press q to quit the query


### Optional - Querying Data Using Jupyter with Spark

While we made our queries using Presto, you can also do this using Jupyter with Spark


First, create a softlink in spark directory so we can easily navigate around without copying files

```
docker-compose exec spark bash 
ln -s /w205/project-3-SextonCJ/ mydir
exit
```

This creats a link to your directory on the spark image - so when you are in jupyter, as long as you create your notebook in mydir it will always save to mapped drive in w205


#### Start Jupyter Notebook in Spark
```
docker-compose exec spark env PYSPARK_DRIVER_PYTHON=jupyter PYSPARK_DRIVER_PYTHON_OPTS='notebook --no-browser --port 9999 --ip 0.0.0.0 --allow-root' pyspark
```

In your browser, replace ip with your ip, and the token with what was provided

```
http://<your>.<four>.<digit>.<ip>:9999/?token=05aa56554d9d0e0f45cadeec537bf1b5fcbc6b51076349e7
```

After this is done, open a new notebook and run some queries. Below are some samples:

```
# read the data files and register as tables so can do SQL
events = spark.read.parquet('/tmp/menu_app_events')
events.registerTempTable('events')
orders = spark.read.parquet('/tmp/menu_app_orders')
orders.registerTempTable('orders')
```

```
spark.sql("describe events").show()
spark.sql("select event_type, description from events group by event_type, description").show()
```

```
spark.sql("describe orders").show()
spark.sql("select event_type, description from orders group by event_type, description").show()
```

```
spark.sql("select event_type, event_timestamp, description, coupon, price from orders where description = 'Lebanese'").show()
```

Alternatively, you can write files to your local machine if you prefer to run locally.


```
df_events = events.toPandas()
df_events.to_csv (r'/w205/project-3-SextonCJ/data/events.csv', index = None, header=True)
```

```
df_orders = orders.toPandas()
df_orders.to_csv (r'/w205/project-3-SextonCJ/data/orders.csv', index = None, header=True)
```
