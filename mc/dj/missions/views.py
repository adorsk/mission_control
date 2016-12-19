from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Workflow, WorkflowStatuses
from .serializers import WorkflowSerializer


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('status',)

@require_http_methods(["POST"])
def claim_workflows(request):
    result = {}
    csv_uuids = request.POST['uuids']
    if csv_uuids:
        uuids = csv_uuids.split(',')
        workflows = Workflow.objects.filter(uuid__in=uuids)
        for workflow in workflows:
            if workflow.status == WorkflowStatuses.Pending.name:
                workflow.status = WorkflowStatuses.Claimed.name
                workflow.save()
                result[workflow.uuid] = WorkflowSerializer(workflow).data
            else:
                result[workflow.uuid] = None
    return JsonResponse(result)
