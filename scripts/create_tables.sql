drop table if exists default.menu_app_orders;
create external table if not exists default.menu_app_orders (
    raw_event string,
    kafka_timestamp timestamp,
    Accept string,
    Host string,
    User_Agent string,
    coupon string,
    description string,
    event_timestamp timestamp,
    event_type string,
    price int,
    uid string
  )
  stored as parquet 
  location '/tmp/menu_app_orders'
  tblproperties ("parquet.compress"="SNAPPY");

drop table if exists default.menu_app_events; 
create external table if not exists default.menu_app_events (
    raw_event string,
    kafka_timestamp timestamp,
    Accept string,
    Host string,
    User_Agent string,
    description string,
    event_timestamp timestamp,
    event_type string,
    uid string
  )
  stored as parquet 
  location '/tmp/menu_app_events'
  tblproperties ("parquet.compress"="SNAPPY");
