from django.test import TestCase

from chatapi.models.models import NtChatMessage, MessageStatus


class NtChatMessageTestCase(TestCase):
    message_info = {
        'user_id': 'A1001',
        'thread_id': 42,
        'sequential_order': 1,
    }
    data_create = {
        'role': 'user',
        'content': 'Please remember, my dog\'s name is L3393. How many meals a day for L3393?',
        'status': MessageStatus.CREATED
    }
    data_update = {
        'role': 'assistant',
        'content': 'L3393 is a Dog.',
        'status': MessageStatus.REPLIED
    }

    def setUp(self):
        # Set up test data
        message1 = NtChatMessage.objects.create(user_id=self.message_info['user_id'],
                                                thread_id=self.message_info['thread_id'],
                                                sequential_order=self.message_info['sequential_order'],
                                                role=self.data_create['role'],
                                                content=self.data_create['content'],
                                                status=self.data_create['status'])
        message1.save()

    def test_create_read(self):
        message1 = NtChatMessage.objects.filter(user_id=self.message_info['user_id'],
                                                thread_id=self.message_info['thread_id'],
                                                sequential_order=self.message_info['sequential_order']).first()

        # Assertions
        self.assertEqual(message1.user_id, self.message_info['user_id'])
        self.assertEqual(message1.thread_id, self.message_info['thread_id'])
        self.assertEqual(message1.sequential_order, self.message_info['sequential_order'])
        self.assertEqual(message1.role, self.data_create['role'])
        self.assertEqual(message1.content, self.data_create['content'])
        self.assertEqual(message1.status, self.data_create['status'])

    def test_update(self):
        message_update = NtChatMessage.objects.filter(user_id=self.message_info['user_id'],
                                                      thread_id=self.message_info['thread_id'],
                                                      sequential_order=self.message_info['sequential_order'])

        message_update.update(role=self.data_update['role'],
                              content=self.data_update['content'],
                              status=self.data_update['status'])

        message_check = NtChatMessage.objects.filter(user_id=self.message_info['user_id'],
                                                     thread_id=self.message_info['thread_id'],
                                                     sequential_order=self.message_info['sequential_order']).first()
        # Assertions
        self.assertEqual(message_check.role, self.data_update['role'])
        self.assertEqual(message_check.content, self.data_update['content'])
        self.assertEqual(message_check.status, self.data_update['status'])
        pass

    def test_delete(self):
        NtChatMessage.objects.filter(user_id=self.message_info['user_id'],
                                     thread_id=self.message_info['thread_id'],
                                     sequential_order=self.message_info['sequential_order']).delete()
        message_check = NtChatMessage.objects.filter(user_id=self.message_info['user_id'],
                                                     thread_id=self.message_info['thread_id'],
                                                     sequential_order=self.message_info['sequential_order'])
        # Assertions
        self.assertEqual(message_check.count(), 0)
        pass
