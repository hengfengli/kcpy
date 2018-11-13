# Kinesis Consumer in Python

A kinesis consumer is purely written in python. This is a lightweight wrapper 
on top of AWS python library [boto3](https://github.com/boto/boto3). You also can 
consume records from Kinesis Data Stream (KDS) via: 

* Lambda function: I have a demo [kinesis-lambda-sqs-demo](https://github.com/HengfengLi/kinesis-lambda-sqs-demo)
showing how to consume records in a serverless and real-time way. 
* [Kinesis Firehose](https://aws.amazon.com/kinesis/firehose/): This is a AWS managed service and easily save records
into different sinks, like S3, ElasticSearch, Redshift. 

## Installation

Install the package via `pip`: 
```bash
pip install kcpy
```

## Getting started

```python
from kcpy import StreamConsumer
consumer = StreamConsumer(stream_name)
for record in consumer:
    print(record)
```

The output would look like:

```bash
{
    'ApproximateArrivalTimestamp': datetime.datetime(2018, 11, 13, 11, 57, 55, 117807), 
    'Data': b'Jessica Walter', 
    'PartitionKey': 'Jessica Walter', 
    'SequenceNumber': '1'
}
```

## Features

* Read records from a stream with multiple shards

## Todo

* Save checkpoint for each shard
* Rebalance when the number of shards changes
* Allow kcpy to run on multiple machines

## Changelog

### 0.1.2

* Add markdown support for long description. 

### 0.1.1

* Add a long description.

### 0.1.0

* First version of kcpy.  

## License

Copyright (c) 2018 Hengfeng Li. It is free software, and may
be redistributed under the terms specified in the [LICENSE] file.

[LICENSE]: /LICENSE
