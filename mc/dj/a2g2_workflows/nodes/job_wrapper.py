from .base import BaseNode
from .job import JobNode


class JobWrapperNode(BaseNode):
    def __init__(self, *args, data=None, **kwargs):
        super().__init__(self, *args, data=data, **kwargs)
        self.job_node = self.generate_job_node(*args, **kwargs)

    def generate_job_node(self, *args, **kwargs):
        job_node_state = self.data.get('_job_node_state', {})
        job_node_kwargs = {
            **kwargs,
            'status': job_node_state.get('status', None),
            'data': {'input': self.get_job_input(),
                     **job_node_state.get('data', {})}
        }
        return JobNode(*args, **job_node_kwargs)

    def get_job_input(self): raise NotImplementedError

    def tick(self):
        try:
            self.job_node.tick()
            self._update_nested_job_node_state()
            if self.job_node.status == 'COMPLETED':
                self.on_job_completed()
            elif self.job_node.status == 'FAILED':
                self.on_job_failed()
            else:
                self.status = self.job_node.status
        except Exception as e:
            self.logger.exception(e)
            self.data['error'] = str(e)
            self.status = 'FAILED'

    def _update_nested_job_node_state(self):
        self.data['_job_node_state'] = self._get_job_node_state()

    def _get_job_node_state(self):
        return {'status': self.job_node.status, 'data': self.job_node.data}

    def on_job_completed(self):
        self.data['output'] = self.job_node.data.get('output', None)
        self.status = 'COMPLETED'

    def on_job_failed(self):
        self.data['error'] = self.job_node.data.get('error', None)
        self.status = 'FAILED'
