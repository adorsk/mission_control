from .base_flow_task_handler import BaseFlowTaskHandler


class InlineFlowTaskHandler(BaseFlowTaskHandler):
    """Creates flows as inline flows"""

    def validate_task_params(self):
        super().validate_task_params()
        assert self.task['task_params']['flow_spec']

    def initial_tick(self):
        self.tick_flow_until_has_no_pending(flow=self.create_flow())

    def create_flow(self):
        return self.flow_engine.generate_flow(
            flow_spec=self.task['task_params']['flow_spec'])

    def tick_flow_until_has_no_pending(self, flow=None):
        self.flow_engine.tick_flow_until_has_no_pending(
            flow=flow,
            task_ctx={'parent_task_ctx': self.task_ctx,
                      **{k: v for k, v in self.task_ctx.items()
                         if k not in {'flow', 'task'}}
                     }
        )
        self.persist_flow(flow=flow)
        self.handle_flow_status(flow=flow)

    def persist_flow(self, flow=None):
        serialization = self.flow_engine.serialize_flow(flow=flow)
        self.task['data']['_flow_task_flow_meta'] = \
            {'serialization': serialization}
        self.task['status'] = 'RUNNING'

    def intermediate_tick(self):
        self.tick_flow_until_has_no_pending(flow=self.get_flow())

    def get_flow(self):
        return self.flow_engine.deserialize_flow(
            serialized_flow=(self.task['data']['_flow_task_flow_meta']
                             ['serialization'])
        )

TaskHandler = InlineFlowTaskHandler
