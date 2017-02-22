import argparse
import importlib
import json
import sys


class A2G2JobEngine(object):
    def execute_job(self, job=None, cfg=None):
        job_module = self.get_job_module(job=job, cfg=cfg)
        return job_module.execute_job(job=job, cfg=cfg)

    def get_job_module(self, job=None, cfg=None):
        module_name = '{job_type}_job_module'.format(
            job_type=job['job_spec']['type'])
        try:
            job_module = importlib.import_module(module_name, package=__name__)
        except Exception as error:
            raise Exception("Could not load job_module for job: %s" % error)
        return job_module

class ExecuteJobCommand(object):
    help = 'Execute Job'

    def __init__(self, streams=None):
        self.setup_streams(streams=streams)

    def setup_streams(self, streams=None):
        streams = streams or {}
        for stream_id in ['stdout', 'stderr', 'stdin']:
            if stream_id in streams:
                stream = streams[stream_id]
            else:
                stream = getattr(sys, stream_id)
            setattr(self, stream_id, stream)

    def execute(self, argv=None):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)
        parsed_args = parser.parse_args(argv)
        self.handle(**vars(parsed_args))

    def add_arguments(self, parser):
        def json_file_type(file_path): return json.load(open(file_path))
        parser.add_argument('--job', type=json_file_type)
        parser.add_argument('--cfg', type=json_file_type, default={})

    def handle(self, *args, job=None, cfg=None, **kwargs):
        self.execute_job(
            job=job,
            cfg=cfg,
            a2g2_job_engine=self.generate_a2g2_job_engine()
        )

    def generate_a2g2_job_engine(self):
        return A2G2JobEngine()

    def execute_job(self, job=None, cfg=None, a2g2_job_engine=None):
        return a2g2_job_engine.execute_job(job=job, cfg=cfg)

if __name__ == '__main__':
    cmd = ExecuteJobCommand()
    cmd.run(argv=sys.argv)