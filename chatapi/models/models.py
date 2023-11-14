from django.db import models
from enumchoicefield import EnumChoiceField, ChoiceEnum


class MessageStatus(ChoiceEnum):
    CREATED = 'CREATED'

    ACTIVE_STORAGE = 'ACTIVE_STORAGE'
    ACTIVE_MEMORY = 'ACTIVE_MEMORY'

    PROCESSING = 'PROCESSING'
    PROCESSED = 'PROCESSED'
    REPLIED = 'REPLIED'

    REMOVED = 'REMOVED'


class NtChatMessage(models.Model):
    user_id = models.CharField(max_length=16, default='')
    thread_id = models.IntegerField(default=0)
    sequential_order = models.IntegerField(default=0)

    role = models.CharField(max_length=16, default='user')
    content = models.TextField(default=None)
    status = EnumChoiceField(MessageStatus, default=MessageStatus.CREATED)
