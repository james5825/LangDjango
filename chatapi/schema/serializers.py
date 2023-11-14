from rest_framework import serializers

from chatapi.models.models import NtChatMessage


class NTChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NtChatMessage
        fields = ['user_id', 'thread_id', 'sequential_order', 'role', 'content', 'status']
