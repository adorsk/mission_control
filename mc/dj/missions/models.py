import enum
import uuid
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.postgres.fields import JSONField

def str_uuid4(): return str(uuid.uuid4())

def uuid_model_str(instance):
    return '<{class_name}: {uuid}>'.format(
        class_name=instance.__class__.__name__,
        uuid=instance.uuid)

class Mission(TimeStampedModel):
    uuid = models.CharField(primary_key=True, default=str_uuid4,
                            editable=False, max_length=64)
    name = models.CharField(null=True, max_length=1024)

    def __str__(self):
        return uuid_model_str(self)

class WorkflowStatuses(enum.Enum):
    PENDING = {'label': 'pending'}
    RUNNING = {'label': 'running'}
    COMPLETED = {'label': 'completed'}

class Workflow(TimeStampedModel):
    uuid = models.CharField(primary_key=True, default=str_uuid4,
                            editable=False, max_length=64)
    serialization = models.TextField(null=True)
    mission = models.ForeignKey('Mission', null=True, on_delete=models.CASCADE)
    status = models.CharField(null=True, max_length=32,
                              choices=[(status.name, status.value['label'])
                                       for status in WorkflowStatuses],
                              default=WorkflowStatuses.PENDING.name)
    claimed = models.NullBooleanField(null=True, default=False)

    def __str__(self):
        return uuid_model_str(self)

class WorkflowJob(TimeStampedModel):
    uuid = models.CharField(primary_key=True, default=str_uuid4,
                            editable=False, max_length=64)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE,
                                 related_name='workflow_jobs')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE)
    finished = models.NullBooleanField(null=True, default=False)
    meta = JSONField(default=dict)

    def __str__(self):
        return '<{class_name}: {{workflow_id: {wf}, job_id: {j}}}>'.format(
            class_name=self.__class__.__name__,
            wf=self.workflow_id,
            j=self.job_id)
