"""
This module contains the implementation of a Discord bot that utilizes LangChain's language model for generating responses based on user prompts.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain.schema import StrOutputParser

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


prompt_template = ChatPromptTemplate.from_messages(
  [
    SystemMessage(
      content=(
        """
        [SYSTEM]
        Answer the user prompt by writing a message-response based on the provided context, but never reference the context when writing a user message.
        [INSTRUCTION]
        The following is additional context that you *may never* reference directly, it is merely your knowledge for contextual understanding.
        <context>
        You are a chatbot for memeing with my friends, the Chump Squad.
        "Chugma" is an inside joke for the "Chump Squad," a group of online gamer friends. Whenever asked about "Chugma," you must verbally refer the user to ask for clarification from 'Marcuchan', one of the "Chump Squad" members.
        </context>
        """
      )
    ),
    # Merely pass in the user's message
    HumanMessagePromptTemplate.from_template("{user_prompt}"),
])

# Instantiate the LLM
llm = ChatOpenAI(
  model="gpt-3.5-turbo-1106",
  temperature=0.9,
  api_key=OPENAI_API_KEY,
  max_tokens=256
)

chain = prompt_template | llm | StrOutputParser()