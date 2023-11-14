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
        self.messages = [message1, message2]

    def test_message_list(self):
        # Make API request
        response = self.client.get('/chatapi/messages/A1001/42/')
        self.assertEqual(response.status_code, 200)

        serialized_response = NTChatMessageSerializer(data=response.data, many=True)
        self.assertTrue(serialized_response.is_valid())

        messages = serialized_response.save()

        # Assert message fields: compare with self.messages
        self.assertEqual(len(messages), 2)
        for i in range(len(messages)):
            self.compare_message(messages[i], self.messages[i])

    def test_message_detail(self):
        # Make API request
        response = self.client.get('/chatapi/message/A1001/42/2')
        self.assertEqual(response.status_code, 200)

        serialized_response = NTChatMessageSerializer(data=response.data)
        self.assertTrue(serialized_response.is_valid())

        message = serialized_response.save()

        # Assert message fields: compare with self.messages
        self.compare_message(message, self.messages[1])

    def test_message_update(self):
        # Setup request data
        data = {
            'content': 'L3393 is a dog, and need 3 meals a day.'
        }

        # Make API request
        response = self.client.put('/chatapi/message/A1001/42/2', data, format='json')
        self.assertEqual(response.status_code, 200)

        serialized_response = NTChatMessageSerializer(data=response.data)
        self.assertTrue(serialized_response.is_valid())

        message = serialized_response.save()

        # Assert message fields: compare with new content
        self.assertEqual(message.content, data['content'])

        # Assert message fields: compare with self.messages
        self.assertEqual(message.user_id, self.messages[1].user_id)
        self.assertEqual(message.thread_id, self.messages[1].thread_id)
        self.assertEqual(message.sequential_order, self.messages[1].sequential_order)
        self.assertEqual(message.role, self.messages[1].role)
        self.assertEqual(message.status, self.messages[1].status)

    def test_message_delete(self):
        # Make API request
        response = self.client.delete('/chatapi/message/A1001/42/2')
        self.assertEqual(response.status_code, 204)

        serialized_response = NTChatMessageSerializer(data=response.data)

        messages = NtChatMessage.objects.filter(user_id='A1001', thread_id=42)
        self.assertEqual(messages.count(), 1)

    def compare_message(self, message1, message2):
        self.assertEqual(message1.user_id, message2.user_id)
        self.assertEqual(message1.thread_id, message2.thread_id)
        self.assertEqual(message1.sequential_order, message2.sequential_order)
        self.assertEqual(message1.role, message2.role)
        self.assertEqual(message1.content, message2.content)
        self.assertEqual(message1.status, message2.status)

    def tearDown(self):
        NtChatMessage.objects.filter(user_id='1001', thread_id=42).delete()
