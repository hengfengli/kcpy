# Kinesis Consumer in Python

[![alt text][mit_license]][mit_license_url]
[![alt text][wheel]][wheel_url] 
[![alt text][pyversion]][pyversion_url] 
[![alt text][pyimp]][pyimp_url]

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
consumer = StreamConsumer('my_stream_name')
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

Or, you can consume stream data with checkpointing: 

```python
from kcpy import StreamConsumer
consumer = StreamConsumer('my_stream_name', consumer_name='my_consumer', checkpoint=True)
for record in consumer:
    print(record)
```

## Checkpointing

Below shows the schema of checkpointing: 

```
                                                                   producer
[stream_1]                                                            |
+---------------+---+---+---+---+---+---+---+---+                     |
| shard_1       | 1 | 2 | 3 | 4 | 5 | 6 | 7 |...| <-------------------+
+---------------+---+---+---+---+---+---+---+---+                     |
| shard_2       | 1 | 2 | 3 | 4 | 5 |...| <---------------------------+
+---------------+---+---+---+---+---+---+---+---+---+                 |
| shard_3       | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |...| <---------------+
+---------------+---+---+---+---+---+---+---+---+---+
                          ^                   ^
                          |                   |
                      consumer_1          consumer_2
                          |                   |
                          |                   +---------+
                          |                             |
                          +------------------+          |
                                             |          |
                                             v          |
+---------------+-------------+----------+--------+     |
| consumer_name | stream_name | shard_id | seq_no |     |
+---------------+-------------+----------+--------+     |
| consumer_1    | stream_1    | shard_1  |   5    |     |
| consumer_1    | stream_1    | shard_2  |   15   |     |
| consumer_1    | stream_1    | ...      |   15   |     |
| consumer_1    | stream_1    | shard_N  |   XX   |     |
| consumer_2    | stream_1    | shard_1  |   6    | <---+
+---------------+-------------+----------+--------+
```

## Features

* Read records from a stream with multiple shards
* Save checkpoint for each shard consumer for a stream

## Todo

* Add type checking with `mypy` 
* Add the config for travis CI
* Add code coverage check
* Support other storage solutions (mysql, dynamodb, redis, etc.) for checkpointing  
* Rebalance when the number of shards changes
* Allow kcpy to run on multiple machines

## Changelog

### 0.1.5

* Add consumer checkpointing with a simple sqlite storage solution. 

### 0.1.4

* Pass aws configurations into boto3 client directly. 

### 0.1.3

* Update the README. 

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

[mit_license]: https://img.shields.io/pypi/l/kcpy.svg "MIT License"
[mit_license_url]: https://opensource.org/licenses/MIT

[wheel]: https://img.shields.io/pypi/wheel/kcpy.svg "kcpy can be installed via wheel" 
[wheel_url]: http://pypi.org/project/kcpy/

[pyversion]: https://img.shields.io/pypi/pyversions/kcpy.svg "Supported Python versions."
[pyversion_url]: http://pypi.org/project/kcpy/

[pyimp]: https://img.shields.io/pypi/implementation/kcpy.svg "Support Python implementations."
[pyimp_url]: http://pypi.org/project/kcpy/
