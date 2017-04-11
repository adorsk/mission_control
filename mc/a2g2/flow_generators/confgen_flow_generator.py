from .compute_parse_load_flow_generator import ComputeParseLoadFlowGenerator

class ConfgenFlowGenerator():
    flow_type = 'confgen'

    @classmethod
    def generate_flow(cls, *args, flow_spec=None, **kwargs):
        job_type_prefix = 'a2g2.jobs.confgen'
        flow_spec = {
            'compute_job_spec': {
                'job_type': job_type_prefix + '.confgen',
                'job_params': {
                    'smiles': flow_spec['input']['smiles'],
                    'params': flow_spec['input']['confgen_params'],
                }
            },
            'parse_job_spec': {
                'job_type': job_type_prefix + '.parse',
                'job_params': {
                    'precursors': flow_spec['input'].get('precursors', {}),
                }
            },
            'load_job_spec': {
                'job_type': job_type_prefix + '.load',
            }
        }
        flow = ComputeParseLoadFlowGenerator.generate_flow(
            *args, flow_spec=flow_spec, **kwargs)
        return flow

    @classmethod
    def get_dependencies(cls):
        return {'flow_generator_classes': set([ComputeParseLoadFlowGenerator])}
