from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.http import Http404

from django_filters.rest_framework import DjangoFilterBackend

from feedback.models import Feedback
from feedback.api.serializers import FeedbackSerializer


class FeedbackView(ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer 
    pagination_class = PageNumberPagination 
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'
    order_fields = '__all__'
    ordering = ['date']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
 

class FeedbackDetailView(APIView):

    def get_object(self):
        try:
            return Feedback.objects.get(pk=self.request.query_params['pk'])
        except Feedback.DoesNotExist:
            return Http404

    def get(self, request, *args, **kwargs):
        data = {}
        pk = request.query_params.get('pk', None)
        if pk == None:
            data['response']      = 'Error'
            data['error_message'] = 'pk must be in the query parameters'
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST) 

        feedback = self.get_object()
        if feedback == Http404:
            data['response'] = 'Order with pk does not exist'
            return Response(data=data, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FeedbackSerializer(feedback, context={'request': request})
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)

