from mc.task_handlers.base_flow_task_handler import BaseFlowTaskHandler


class FlowTaskHandler(BaseFlowTaskHandler):
    def initial_tick(self):
        flow_meta = self.create_flow()
        self.task['data']['_flow_task_flow_meta'] = flow_meta

    def create_flow(self):
        create_flow_record_fn = \
                self.task_ctx['mc.tasks.flow.create_flow_record']
        flow_record_kwargs = self.generate_flow_record_kwargs()
        flow_record = create_flow_record_fn(flow_kwargs=flow_record_kwargs)
        flow_meta = {'key': flow_record['key']}
        return flow_meta

    def generate_flow_record_kwargs(self):
        flow_spec = self.task['task_params']['flow_spec']
        flow_record_kwargs = {
            'label': flow_spec.get('label'),
            'serialization': self.serialize_flow_spec(flow_spec=flow_spec)
        }
        return flow_record_kwargs

    def serialize_flow_spec(self, flow_spec=None):
        flow_engine = self.get_flow_engine()
        flow = flow_engine.generate_flow(flow_spec=flow_spec)
        return flow_engine.serialize_flow(flow=flow)

    def intermediate_tick(self):
        flow = self.get_flow()
        self.handle_flow_status(flow=flow)

    def get_flow(self):
        get_flow_fn = self.task_ctx['mc.tasks.flow.get_flow_record']
        flow_record = get_flow_fn(
            flow_meta=self.task['data']['_flow_task_flow_meta'])
        return self.deserialize_flow_record(flow_record=flow_record)

    def deserialize_flow_record(self, flow_record=None):
        flow_engine = self.get_flow_engine()
        return flow_engine.deserialize_flow(
            serialized_flow=flow_record['serialization'])

TaskHandler = FlowTaskHandler
