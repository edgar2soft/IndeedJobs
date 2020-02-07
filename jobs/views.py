from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, JobSerializer
from .models import Job, Query
from .helper.scraper import scraper_indeed
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    #permission_classes = [permissions.IsAuthenticated]


@api_view(['GET', 'POST', ])
def JobViewSet(request):
    url = Query.objects.all()[0].query
    url = url.replace("&start=0", "")

    with scraper_indeed() as scraper:
        return Response(scraper.get_account(url), status=status.HTTP_200_OK)


@api_view(['GET', 'POST', ])
def GetNewJobs(request):
    today = datetime.now().strftime("%Y-%m-%d")
    print(today)

    query = Query.objects.all()[0].query
    query = query.replace("&start=0", "")

    queryset = Job.objects.filter(date=today, query=query)
    result = JobSerializer(queryset, many=True)
    return Response(result.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', ])
def UpdateQuery(request):
    query = request.get_full_path()
    query = query.replace("&start=0", "")
    query = query.replace("/updatequery/?query=", "")
    print(query)
    obj = Query.objects.all()[0]
    obj.query = query
    obj.save()

    context = {
        'query': obj.query
    }
    return Response(context, status=status.HTTP_200_OK)
