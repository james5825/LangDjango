from django.test import TestCase
from rest_framework.test import APIClient

from chatapi.models.models import NtChatMessage, MessageStatus
from chatapi.schema.serializers import NTChatMessageSerializer


class ChatViewTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        message1 = NtChatMessage.objects.create(user_id='A1001', thread_id=42, sequential_order=1, role='user',
                         content='Please remember, my dog\'s name is L3393. How many meals a day for L3393?',
                         status=MessageStatus.CREATED)
        message1.save()

        message2 = NtChatMessage.objects.create(user_id='A1001', thread_id=42, sequential_order=2, role='assistant',
                         content='I will remember your dog\'s name is L3393. L3393 need to eat 3 meals a day.',
                         status=MessageStatus.REPLIED)
        message2.save()

    def test_chat_new_chat(self):
        # Setup request data
        data = {
            'user_id': 'A1001',
            'thread_id': 43,
            'content': 'Hello'
        }
        response = self.client.post('/chatapi/chat/', data, format='json')

        # Assert response
        self.assertEqual(response.status_code, 200)

        serialized_response = NTChatMessageSerializer(data=response.data)
        self.assertTrue(serialized_response.is_valid())

        message = serialized_response.save()

        # Assert message fields
        self.assertEqual(message.user_id, data['user_id'])
        self.assertEqual(message.thread_id, data['thread_id'])
        self.assertEqual(message.sequential_order, 2)
        self.assertEqual(message.role, 'assistant')

    def test_chat_continue_chat(self):
        # Setup request data
        data = {
            'user_id': 'A1001',
            'thread_id': 42,
            'content': 'Can you help me?'
        }

        # Make API request
        response = self.client.post('/chatapi/chat/', data, format='json')

        # Assert response
        self.assertEqual(response.status_code, 200)

        serialized_response = NTChatMessageSerializer(data=response.data)
        self.assertTrue(serialized_response.is_valid())

        message = serialized_response.save()

        # Assert message fields
        self.assertEqual(message.user_id, data['user_id'])
        self.assertEqual(message.thread_id, data['thread_id'])
        self.assertEqual(message.sequential_order, 4)
        self.assertEqual(message.role, 'assistant')

    def tearDown(self):
        NtChatMessage.objects.filter(user_id='1001', thread_id=42).delete()
