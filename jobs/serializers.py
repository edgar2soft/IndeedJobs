from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import Job


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['href', 'title', 'cn', 'loc', 'metaheader', 'desc', 'date']
