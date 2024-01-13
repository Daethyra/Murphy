import os
import logging
import discord
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferWindowMemory

# Configure our logger
logging.basicConfig(level=logging.INFO)

# Set our Discord and LangChain tokens
CURRENCY_BOT_TOKEN = os.environ['CURRENCY_BOT_TOKEN']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LANGCHAIN_API_KEY = os.environ['LANGCHAIN_API_KEY']
LANGCHAIN_PROJECT = os.environ['LANGCHAIN_PROJECT']
LANGCHAIN_TRACING_V2 = os.environ['LANGCHAIN_TRACING_V2']

# Claim intent and instantiate Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)


# Prompt template for passing in the `user_prompt` after extracting everything after '$hello' in a user's message. 
# Therefore, the bot won't respond unless that keyword is at the beginning, and the context sent to the LLM won't include '$hello'
prompt_template = ChatPromptTemplate.from_messages(
  [
    SystemMessage(
      content=(
        """
        Answer the user prompt by writing a message-response based on the provided context, but never reference the context when writing a user message.
        The following is additional context that you *may never* reference directly, it is merely your knowledge for contextual understanding.
        [NON_REFERENCEABLE_CONTEXT]
        <context>
        "Chugma" is an inside joke for the "Chump Squad," a group of online gamer friends. Whenever asked about "Chugma," you must verbally refer the user to ask for clarification from 'Marcuchan', one of the "Chump Squad" members.
        </context>
        """
      )
    ),
    HumanMessagePromptTemplate.from_template("{user_prompt}"),
])

# Instantiate the LLM
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.5, api_key=OPENAI_API_KEY)

chain = prompt_template | llm | StrOutputParser()


# On ready, print a message to the console
@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')

# Define an event function to handle messages
# First, see if messsage begins with '$hello'
# Then, strip the rest of the message, and pass into `user_prompt`
# Finally, Use an llm for generating the response based on context and the user's message
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # if a user message starts with '$hello' the rest of the content will \
      # be stripped and passed in as the `user_prompt` for the `prompt_template`
    if message.content.startswith('$hello'):
        logging.info("Message contains $hello: \n\n" + str(message.content))

        # Extract the message text after '$hello'
        user_prompt = message.content[len('$hello'):].strip()
        logging.info("Stripped user's message content. \n\n" + str(user_prompt))

        # Default message if no text is provided
        default_message = 'Hello! How can I assist you today?'

        if user_prompt:
            # Use LangChain's LLM to generate a response based on the user's prompt
            # Wait for the LLM to generate a response
            # Define the response call

            prompt = prompt_template.format(user_prompt=user_prompt)
            response = chain.invoke({"user_prompt": prompt})

            await message.channel.send(response)
            logging.info("Response sent to Discord.")
        else:
            # Send default message
            await message.channel.send(default_message)
            logging.info("Sent default message.")

try:
    client.run(CURRENCY_BOT_TOKEN)
    logging.info("Client ran.")
except Exception as err:
    raise err
    logging.error(err)
