import argparse
import glob
import json
import os
import sys

import pybel

from mc.a2g2.a2g2_client.a2g2_client import A2G2_Client

def execute_job(*args, job=None, cfg=None, output_dir=None, ctx_dir=None,
                **kwargs):
    Command().handle(job=job, cfg=cfg, ctx_dir=ctx_dir)

class ConfgenLoadJobEngine(object):
    def __init__(self, a2g2_client=None):
        self.a2g2_client = a2g2_client

    def execute_job(self, job=None, ctx_dir=None):
        dir_to_parse = os.path.join(
            ctx_dir, job['data']['input']['dir_to_parse'])
        chemthings = self.parse_job_dir(dir_to_parse=dir_to_parse)
        job['data']['output'] = self.upload_chemthings(chemthings)

    def parse_job_dir(self, dir_to_parse=None, includes=None, excludes=None):
        paths_to_parse = self.get_paths_to_parse(dir_to_parse=dir_to_parse,
                                                 includes=includes,
                                                 excludes=excludes)
        chemthings = []
        for path in paths_to_parse: chemthings.extend(self.parse_path(path))
        return chemthings

    def get_paths_to_parse(self, dir_to_parse=None, includes=None,
                           excludes=None):
        if not includes: includes = ['output/**']
        paths_to_include = self.get_paths_for_globs(root_dir=dir_to_parse,
                                                    globs=includes)
        paths_to_exclude = self.get_paths_for_globs(root_dir=dir_to_parse,
                                                    globs=excludes)
        paths_to_parse = set(paths_to_include).difference(set(paths_to_exclude))
        return paths_to_parse

    def get_paths_for_globs(self, root_dir=None, globs=None):
        paths = []
        globs = globs or []
        for _glob in globs:
            full_glob = os.path.join(root_dir, _glob)
            all_paths = glob.glob(full_glob, recursive=True)
            file_paths = [path for path in all_paths if os.path.isfile(path)]
            paths.extend(file_paths)
        return paths

    def parse_path(self, path=None):
        chemthings = []
        pybel_mols = self.file_to_pybel_mols(path=path)
        for i, pybel_mol in enumerate(pybel_mols):
            chemthing = self.pybel_mol_to_chemthing(pybel_mol)
            chemthing['props']['mol_idx'] = i
            chemthings.append(chemthing)
        return chemthings

    def file_to_pybel_mols(self, path=None):
        ext = os.path.splitext(path)[1].lstrip('.')
        return pybel.readfile(ext, path)

    def pybel_mol_to_chemthing(self, pybel_mol=None):
        chemthing = {'cml': pybel_mol.write('cml'), 'props': {}}
        return chemthing

    def upload_chemthings(self, chemthings=None):
        results = []
        for chemthing in chemthings:
            result = self.a2g2_client.create_chemthing(chemthing=chemthing)
            results.append(result)
        return results

class Command(object):
    help = 'confgen_load_job'

    def __init__(self, streams=None):
        self.setup_streams(streams=streams)

    def execute(self, argv=None):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)
        parsed_args = parser.parse_args(argv)
        self.handle(**vars(parsed_args))

    def setup_streams(self, streams=None):
        streams = streams or {}
        for stream_id in ['stdout', 'stderr', 'stdin']:
            if stream_id in streams:
                stream = streams[stream_id]
            else:
                stream = getattr(sys, stream_id)
            setattr(self, stream_id, stream)

    def add_arguments(self, parser):
        def json_file_type(file_path):
            return json.load(open(file_path))
        parser.add_argument('--job', type=json_file_type)
        parser.add_argument('--cfg', type=json_file_type, default={})
        parser.add_argument('--ctx_dir', type=str)

    def handle(self, *args, job=None, cfg=None, ctx_dir=None, **kwargs):
        a2g2_client = self.generate_a2g2_client(cfg=cfg)
        self.execute_job(job=job, a2g2_client=a2g2_client, ctx_dir=ctx_dir)

    def generate_a2g2_client(self, cfg=None):
        a2g2_client_cfg_json = self.get_cfg_value(
            cfg=cfg, key='A2G2_CLIENT_CFG_JSON', default='{}')
        a2g2_client_cfg = json.loads(a2g2_client_cfg_json)
        a2g2_client = A2G2_Client(**a2g2_client_cfg)
        return a2g2_client

    def get_cfg_value(self, cfg=None, key=None, default=None):
        if key in os.environ: cfg_value = os.environ[key]
        else: cfg_value = (cfg or {}).get(key, default)
        return cfg_value

    def execute_job(self, job=None, a2g2_client=None, ctx_dir=None):
        engine = ConfgenLoadJobEngine(a2g2_client=a2g2_client)
        engine.execute_job(job=job, ctx_dir=ctx_dir)

if __name__ == '__main__':
    command = Command()
    command.run(args=sys.argv[1:])