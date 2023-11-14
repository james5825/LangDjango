from django.test import TestCase
from langchain.llms.fake import FakeListLLM

from chatapi.models.models import NtChatMessage, MessageStatus
from chatapi.service.chat_service import ChatService


class ChatServiceTestCase(TestCase):
    def setUp(self):
        message1 = NtChatMessage.objects.create(user_id='A1001', thread_id=42, sequential_order=1, role='user',
                         content='Please remember, my dog\'s name is L3393. How many meals a day for L3393?',
                         status=MessageStatus.CREATED)
        message1.save()

        message2 = NtChatMessage.objects.create(user_id='A1001', thread_id=42, sequential_order=2, role='assistant',
                         content='I will remember your dog\'s name is L3393. L3393 need to eat 3 meals a day.',
                         status=MessageStatus.REPLIED)
        message2.save()

    def test_new_chat(self):
        # Set up llm for test
        responses = ["I'm fine, thank you."]
        llm = FakeListLLM(responses=responses)
        chat_service = ChatService(llm)

        # Set up test data
        message = NtChatMessage.objects.create(user_id='1001', thread_id=42, sequential_order=1,
                        role='user', content='How are you?',
                        status=MessageStatus.CREATED)

        # Call service method
        response = chat_service.new_chat(message)

        # Assertions
        self.assertEqual(response.role, 'assistant')
        self.assertEqual(response.content, responses[0])
        self.assertEqual(response.sequential_order, message.sequential_order + 1)
        self.assertEqual(response.thread_id, message.thread_id)
        self.assertEqual(response.user_id, message.user_id)

    def test_continue_chat(self):
        # Set up llm for test
        responses = ["L3393 is a dog"]
        llm = FakeListLLM(responses=responses)
        chat_service = ChatService(llm)

        # Set up test data
        message = NtChatMessage.objects.create(user_id='1001', thread_id=42, sequential_order=3,
                        role='user', content='L3393 is what kind of animal?',
                        status=MessageStatus.CREATED)

        history = NtChatMessage.objects.filter(user_id='1001', thread_id=42).order_by('sequential_order')

        # Call service method
        response = chat_service.continue_chat(message, history)

        # Assertions
        self.assertEqual(response.role, 'assistant')
        self.assertEqual(response.content, responses[0])
        self.assertEqual(response.sequential_order, message.sequential_order + 1)
        self.assertEqual(response.thread_id, message.thread_id)
        self.assertEqual(response.user_id, message.user_id)

    def tearDown(self):
        NtChatMessage.objects.filter(user_id='1001', thread_id=42).delete()
