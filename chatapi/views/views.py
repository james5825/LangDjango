from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chatapi.models.models import NtChatMessage
from chatapi.schema.serializers import NTChatMessageSerializer
from chatapi.service.chat_service import ChatService

user_response = openapi.Response('response description', NTChatMessageSerializer)


@csrf_exempt
@swagger_auto_schema(method='post', operation_description="Send question to query api for answer",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                         'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='User'),
                         'thread_id': openapi.Schema(type=openapi.TYPE_INTEGER, description=1),
                         'sequential_order': openapi.Schema(type=openapi.TYPE_INTEGER, description=1),
                         'content': openapi.Schema(type=openapi.TYPE_STRING, description='How many meals a day?'),
                     }), responses={200: user_response})
@api_view(['POST'])
def chat(request):
    serializer = NTChatMessageSerializer(data=request.data)

    if serializer.is_valid():
        new_message = serializer.save()
        previous_messages = NtChatMessage.objects.filter(user_id=new_message.user_id, thread_id=new_message.thread_id).order_by('sequential_order')

        cs = ChatService()
        try:
            if previous_messages or previous_messages.count() == 0:
                new_message.sequential_order = previous_messages.last().sequential_order + 1
                new_message.save()
                new_message_res = cs.continue_chat(new_message, previous_messages)
            else:
                new_message.sequential_order = 1
                new_message.save()
                new_message_res = cs.new_chat(new_message)
            new_message_res.save()
        except IntegrityError as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=e)
        return Response(NTChatMessageSerializer(new_message_res).data)
    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


@csrf_exempt
@swagger_auto_schema(method='get', operation_description="retrieve all messages by /messages/{user_id}/{thread_id}/",
                     responses={200: user_response})
@api_view(['GET'])
def messages(request, user_id, thread_id):
    try:
        previous_messages = NtChatMessage.objects.filter(user_id=user_id, thread_id=thread_id).order_by('sequential_order')
        if previous_messages.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
    except NtChatMessage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(NTChatMessageSerializer(previous_messages, many=True).data)


@csrf_exempt
@swagger_auto_schema(method='get', operation_description="retrieve message by /message/{user_id}/{thread_id}/{sequential_order}",
                     responses={200: user_response})
@swagger_auto_schema(method='put', operation_description="modify message by /message/{user_id}/{thread_id}/{sequential_order}",
                     request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                         'content': openapi.Schema(type=openapi.TYPE_STRING, description='How many meals a day?'),
                     }),
                     responses={200: user_response})
@swagger_auto_schema(method='delete', operation_description="delete message by /message/{user_id}/{thread_id}/{sequential_order}",
                     responses={200: user_response})
@api_view(['GET', 'PUT', 'DELETE'])
def message(request, user_id, thread_id, sequential_order):
    try:
        previous_messages = NtChatMessage.objects.filter(user_id=user_id, thread_id=thread_id, sequential_order=sequential_order)
        if previous_messages.count() == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
    except NtChatMessage.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(NTChatMessageSerializer(previous_messages.last()).data)

    elif request.method == 'PUT':
        serializer = NTChatMessageSerializer(previous_messages.last(), data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except IntegrityError as e:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=e)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        previous_messages.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
