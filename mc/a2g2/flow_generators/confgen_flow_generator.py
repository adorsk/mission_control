from .compute_parse_load_flow_generator import ComputeParseLoadFlowGenerator

class ConfgenFlowGenerator():
    flow_type = 'confgen'

    @classmethod
    def generate_flow(cls, *args, flow_spec=None, **kwargs):
        confgen_flow_spec = flow_spec
        compute_parse_load_flow_spec = {
            'compute_job_spec': {
                'job_module': 'confgen',
                'job_module_params': {
                    'smiles': confgen_flow_spec['input']['smiles'],
                    'params': confgen_flow_spec['input']['confgen_params'],
                }
            }
        }
        flow = ComputeParseLoadFlowGenerator.generate_flow(
            *args,
            flow_spec=compute_parse_load_flow_spec,
            **kwargs
        )
        return flow

    @classmethod
    def get_dependencies(cls):
        return {
            'flow_generator_classes': set([ComputeParseLoadFlowGenerator]),
        }