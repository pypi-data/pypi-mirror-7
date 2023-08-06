# coding=utf-8
from django.http import HttpResponse
from django.views.generic import View
from django_sae.contrib.tasks.settings import PARALLEL_QUEUE_NAME
from sae.taskqueue import TaskQueue


class OperationView(View):
    QUEUE_NAME = PARALLEL_QUEUE_NAME

    @staticmethod
    def as_task(operation):
        if operation is None:
            return []
        try:
            operations = list(iter(operation))
        except TypeError:
            operations = [operation]
        return [operation.as_task() for operation in operations]

    def get_operation(self, request):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        operation = self.get_operation(request)
        tasks = self.as_task(operation)
        TaskQueue(self.QUEUE_NAME).add(tasks)
        content = 'added {0:d} tasks'.format(len(tasks))
        return HttpResponse(content)