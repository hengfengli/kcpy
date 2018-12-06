import pytest
import boto3
import time
import uuid
import os
from moto import mock_kinesis
from kcpy import StreamConsumer
from kcpy.checkpoint import Checkpoint
from faker import Faker
fake = Faker()

# avoid to use the true credentials
fake_aws_creds = {
    'aws_access_key_id': 'fake_one',
    'aws_secret_access_key': 'fake_one',
    'aws_session_token': 'fake_one',
    'region_name': 'us-east-1'
}


class TestCaseKcpy:
    def setup(self):
        pass

    def teardown(self):
        pass

    def get_kinesis_client(self):
        return boto3.client('kinesis', **fake_aws_creds)

    def create_stream(self, stream_name, num_of_shards=1):
        client = self.get_kinesis_client()
        client.create_stream(StreamName=stream_name, ShardCount=num_of_shards)

    def fake_records(self, stream_name, count=1):
        client = self.get_kinesis_client()
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
        consumer = StreamConsumer(stream_name, **fake_aws_creds)
        count = 0
        for _ in consumer:
            count += 1
            if count >= 10:
                break

        assert count == 10

    @mock_kinesis
    def test_get_records_from_stream_with_two_shards(self):
        stream_name = 'test_stream'
        self.create_stream(stream_name, num_of_shards=2)
        self.fake_records(stream_name, count=10)
        consumer = StreamConsumer(stream_name, **fake_aws_creds)
        count = 0
        for _ in consumer:
            count += 1
            if count >= 10:
                break

        assert count == 10

    def test_checkpoint_storage(self):
        random_db_file = f'kcpy_{str(uuid.uuid4())[:8]}.db'
        c = Checkpoint(random_db_file, 'kcpy', 'consumer_1', 'stream_1', 'shard_1')
        c.set('123')
        assert c.get() == '123'
        c.reset()
        assert c.get() is None
        os.remove(random_db_file)

    @mock_kinesis
    def test_get_records_with_checkpoint(self):
        checkpoint_db_file_path = f'kcpy_checkpoint_{str(uuid.uuid4())[:8]}.db'
        stream_name = 'test_stream'
        self.create_stream(stream_name)
        self.fake_records(stream_name, count=10)
        consumer = StreamConsumer(stream_name, consumer_name='consumer-1', checkpoint=True,
                                  checkpoint_db_file_path=checkpoint_db_file_path, **fake_aws_creds)
        count = 0
        for _ in consumer:
            count += 1
            if count >= 10:
                break

        assert list(consumer.processes.values())[0].consumer.checkpoint.get() == '10'

        self.fake_records(stream_name, count=10)
        count = 0
        for _ in consumer:
            count += 1
            if count >= 10:
                break

        assert list(consumer.processes.values())[0].consumer.checkpoint.get() == '20'
        os.remove(checkpoint_db_file_path)
