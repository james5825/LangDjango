import os

from langchain.chains import LLMChain, ConversationChain
from langchain.llms.cohere import Cohere
from langchain.memory import ConversationBufferMemory, ChatMessageHistory
from langchain.prompts import PromptTemplate

from chatapi.models.models import NtChatMessage, MessageStatus


class ChatService:
    # https://docs.cohere.com/reference/generate
    # https://www.youtube.com/watch?v=X550Zbz_ROE
    # https://www.pinecone.io/learn/series/langchain/langchain-conversational-memory/
    api_key = os.environ['COHERE_API_KEY']

    # todo: abstract llm call
    # local llm
    # model_path = "D:\\_WK_GIT\\core\\chatapi\\service\\llm\\gpt4all-falcon-q4_0.gguf"
    # llm = GPT4All(model=model_path, verbose=True)

    def __init__(self, llm=None):
        if llm is not None:
            self.llm = llm
        else:
            self.llm = Cohere(cohere_api_key='r1LGYzJMC7izxmAnyiVM88oLwFuSr1kfCh4huNU1')

    def continue_chat(self, message: NtChatMessage, query_messages: object) -> NtChatMessage:
        chat_history = ChatMessageHistory()
        for message_item in query_messages.all():
            if message_item.role == 'user':
                chat_history.add_user_message(message_item.content)
            if message_item.role == 'assistant':
                chat_history.add_ai_message(message_item.content)
        memory = ConversationBufferMemory(
            llm=self.llm,
            chat_memory=chat_history,
            return_messages=True
        )

        conversation_with_summary = ConversationChain(llm=self.llm, memory=memory, verbose=True)

        response = conversation_with_summary.predict(input=message.content)

        message_res = NtChatMessage.objects.create(user_id=message.user_id,
                                                   thread_id=message.thread_id,
                                                   sequential_order=message.sequential_order + 1,
                                                   role='assistant', content=response,
                                                   status=MessageStatus.REPLIED)
        return message_res

    def new_chat(self, message: NtChatMessage) -> NtChatMessage:
        template = """
        You are an intelligent chatbot. Help the following question with brilliant answers.
        Question: {question}
        Answer:"""
        prompt = PromptTemplate(template=template, input_variables=["question"])
        llm_chain = LLMChain(prompt=prompt, llm=self.llm)
        response = llm_chain.run(message.content)

        message_res = NtChatMessage.objects.create(user_id=message.user_id,
                                                   thread_id=message.thread_id,
                                                   sequential_order=message.sequential_order + 1,
                                                   role='assistant', content=response,
                                                   status=MessageStatus.REPLIED)

        return message_res
