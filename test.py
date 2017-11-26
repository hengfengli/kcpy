import pytest
import boto3
import time
from moto import mock_kinesis
from kcpy import StreamConsumer
from faker import Faker
fake = Faker()


class TestCaseKcpy:
    def setup(self):
        pass

    def teardown(self):
        pass

    def create_stream(self, stream_name, num_of_shards=1):
        client = boto3.client('kinesis')
        client.create_stream(StreamName=stream_name, ShardCount=num_of_shards)

    def fake_records(self, stream_name, count=1):
        client = boto3.client('kinesis')
        for i in range(count):
            data = fake.name()
            partition_key = data

            resp = client.put_record(
                StreamName=stream_name,
                Data=data.encode('utf-8'),
                PartitionKey=partition_key)

            assert resp['ResponseMetadata']['HTTPStatusCode'] == 200

    @mock_kinesis
    def test_get_records_from_stream_with_single_shard(self):
        stream_name = 'test_stream'
        self.create_stream(stream_name)
        self.fake_records(stream_name, count=10)
        consumer = StreamConsumer(stream_name)
        count = 0
        for record in consumer:
            count += 1
            if count >= 10:
                break

        assert count == 10

    @mock_kinesis
    def test_get_records_from_stream_with_two_shards(self):
        stream_name = 'test_stream'
        self.create_stream(stream_name, num_of_shards=2)
        self.fake_records(stream_name, count=10)
        consumer = StreamConsumer(stream_name)
        count = 0
        for record in consumer:
            count += 1
            if count >= 10:
                break

        assert count == 10
