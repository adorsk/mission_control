import os

from mc.flows.flow_engine import FlowEngine

_DIR = os.path.dirname(__file__)

def main():
    flow_spec = {
        'label': 'test_flow',
        'tasks': [
            {
                'key': 'task_1',
                'task_type': 'wire',
                'task_params': {
                    'wirings': [
                        {
                            'dest': (
                                'ctx.flow.tasks.task_2.task_params.msg'
                            ),
                            'value': 'message set by task_1'
                        }
                    ]
                },
                'precursors': ['ROOT'],
            },
            {
                'key': 'task_2',
                'task_type': 'print',
                'task_params': {'msg': 'I will be set from task_1'},
                'precursors': ['task_1'],
            }
        ]
    }
    flow_engine = FlowEngine()
    flow = flow_engine.flow_spec_to_flow(flow_spec=flow_spec)
    flow_engine.run_flow(flow=flow)

if __name__ == '__main__': main()
