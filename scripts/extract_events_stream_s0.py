#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""

import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

#import redis
#r = redis.Redis(host = 'redis', port = '6379')

def order_events_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- coupon: string (nullable = true)
    |-- description: string (nullable = true)
    |-- event_timestamp: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- price: string (nullable = true)
    |-- uid: string (nullable = true)
    """   
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("coupon", StringType(), True),
        StructField("description", StringType(), True),
        StructField("event_timestamp", TimestampType(), True),
        StructField("event_type", StringType(), True),
        StructField("price", IntegerType(), True),
        StructField("uid", StringType(), True),
    ])

@udf('boolean')
def is_order_food(event_as_json):
    event = json.loads(event_as_json)
    if event['event_type'] == 'order_food':
        return True
    return False

def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .enableHiveSupport() \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "menu_app_events") \
        .load()

    # These are all the events that are the order_food schema
    order_events = raw_events \
        .filter(is_order_food(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
            raw_events.timestamp.cast('timestamp').alias('kafka_timestamp'),
            from_json(raw_events.value.cast('string'),
                      order_events_schema()).alias('json')) \
        .select('raw_event', 'kafka_timestamp', 'json.*')

    sink_0 = order_events \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_menu_app_order_events") \
        .option("path", "/tmp/menu_app_orders") \
        .trigger(processingTime="10 seconds") \
        .start()

    sink_0.awaitTermination()

if __name__ == "__main__":
    main()
