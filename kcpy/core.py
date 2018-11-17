import boto3
import time
from multiprocessing import Process, Queue


class ShardConsumer(object):
    DEFAULT_SLEEP_TIME = 0.1

    def __init__(self, stream_name, shard_id, options):
        self.stream_name = stream_name
        self.shard_id = shard_id
        self.client = boto3.client('kinesis', **options)
        self.sleep_time = self.DEFAULT_SLEEP_TIME

    def __iter__(self, shard_iter_type='TRIM_HORIZON', seq=None):
        kwargs = {
            'ShardIteratorType': shard_iter_type,
        }
        if seq:
            kwargs['StartingSequenceNumber'] = seq
        shard_iter_resp = self.client.get_shard_iterator(
            StreamName=self.stream_name, ShardId=self.shard_id, **kwargs)
        shard_iter = shard_iter_resp['ShardIterator']

        while True:
            resp = self.client.get_records(ShardIterator=shard_iter)

            for record in resp['Records']:
                yield record

            shard_iter = resp['NextShardIterator']

            time.sleep(self.sleep_time)


class ShardConsumerProcess(Process):
    def __init__(self, stream_name, shard_id, options):
        Process.__init__(self)
        self.consumer = ShardConsumer(stream_name, shard_id, options)
        self.queue = Queue()

    def run(self):
        for record in self.consumer:
            self.queue.put(record)

    def empty(self):
        return self.queue.empty()

    def get_record(self):
        if self.empty():
            return None

        return self.queue.get()


class StreamConsumer(object):
    DEFAULT_SLEEP_TIME = 0.1

    def __init__(self, stream_name, **options):
        self.stream_name = stream_name
        self.options = options
        self.client = boto3.client('kinesis', **self.options)
        self.processes = {}
        self.sleep_time = self.DEFAULT_SLEEP_TIME

    def __iter__(self):
        try:
            stream_data = self.client.describe_stream(
                StreamName=self.stream_name)

            for shard_data in stream_data['StreamDescription']['Shards']:
                shard_id = shard_data['ShardId']
                self.processes[shard_id] = ShardConsumerProcess(
                    self.stream_name, shard_id, self.options)
                self.processes[shard_id].start()

            while True:
                for shard_id, shard_consumer in self.processes.items():
                    if not shard_consumer.empty():
                        yield shard_consumer.get_record()

                time.sleep(self.sleep_time)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            for shard_id, p in self.processes.items():
                p.terminate()
                p.join()
