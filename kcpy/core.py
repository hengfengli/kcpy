import boto3
import time
from multiprocessing import Process, Queue
from typing import Optional, Dict
import uuid

from .checkpoint import Checkpoint


class ShardConsumer(object):
    DEFAULT_SLEEP_TIME = 0.1

    def __init__(self, stream_name, shard_id, options, checkpoint: Optional[Checkpoint] = None):
        self.stream_name = stream_name
        self.shard_id = shard_id
        self.client = boto3.client('kinesis', **options)
        self.sleep_time = self.DEFAULT_SLEEP_TIME
        self.checkpoint = checkpoint

    def __iter__(self, shard_iter_type='TRIM_HORIZON', seq: Optional[str] = None):
        if self.checkpoint and not seq:
            seq = self.checkpoint.get()
            if seq:
                shard_iter_type = 'AFTER_SEQUENCE_NUMBER'
                seq = str(int(seq))
            print('start after seq:', seq)

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
            last_record = None

            for record in resp['Records']:
                yield record
                last_record = record

            if self.checkpoint and last_record:
                last_seq = last_record['SequenceNumber']
                print('last_seq:', last_seq)
                self.checkpoint.set(last_seq)

            shard_iter = resp['NextShardIterator']

            time.sleep(self.sleep_time)


class ShardConsumerProcess(Process):
    def __init__(self, stream_name, shard_id, options, checkpoint: Optional[Checkpoint] = None):
        Process.__init__(self)
        self.consumer = ShardConsumer(stream_name, shard_id, options, checkpoint)
        self.queue = Queue()  # type: Queue

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

    def __init__(self,
                 stream_name: str,
                 consumer_name: Optional[str] = None,
                 checkpoint: bool = False,
                 checkpoint_db_file_path: str = 'kcpy_checkpoint.db',
                 checkpoint_db_name: str = 'kcpy',
                 **options
                 ) -> None:
        self.stream_name = stream_name
        self.options = options
        self.client = boto3.client('kinesis', **self.options)
        self.processes = {}  # type: Dict[str, ShardConsumerProcess]
        self.sleep_time = self.DEFAULT_SLEEP_TIME
        self.enable_checkpoint = checkpoint

        if consumer_name:
            self.consumer_name = consumer_name
        else:
            self.consumer_name = f'consumer-{str(uuid.uuid4())[:8]}'

        self.checkpoint_db_file_path = checkpoint_db_file_path
        self.checkpoint_db_name = checkpoint_db_name

    def __iter__(self):
        try:
            stream_data = self.client.describe_stream(
                StreamName=self.stream_name)

            for shard_data in stream_data['StreamDescription']['Shards']:
                shard_id = shard_data['ShardId']
                checkpoint = None
                if self.enable_checkpoint:
                    checkpoint = Checkpoint(
                        self.checkpoint_db_file_path,
                        self.checkpoint_db_name,
                        self.consumer_name,
                        self.stream_name,
                        shard_id
                    )
                self.processes[shard_id] = ShardConsumerProcess(
                    self.stream_name, shard_id, self.options, checkpoint=checkpoint)
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
