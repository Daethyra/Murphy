import os
from dotenv import load_dotenv
import logging
import discord
from generation import chain, prompt_template

# Configure our logger
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Set our Discord and LangChain tokens
CURRENCY_BOT_TOKEN = os.getenv('CURRENCY_BOT_TOKEN')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT')
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')

# Claim intent and instantiate Discord client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Using Client>Bot because there are no commands to create
client = discord.Client(intents=intents)


# On ready, print a message to the console
@client.event
async def on_ready():
    logging.info(f'\nWe have logged in as {client.user}')



@client.event
async def on_message(message):
    """
    An event handler that is triggered whenever a message is received.

    Parameters:
    - message: The message object containing information about the received message.

    Returns:
    - None

    Notes:
    - This function checks if the message author is not the bot itself.
    - If the message content starts with '$hello', the rest of the content is stripped and passed as the `user_prompt` for the `prompt_template`.
    - If the `user_prompt` is not empty, it formats the `user_prompt` into the `prompt_template` and passes it for generation.
    - It sends the generated response to the message channel.
    - If the `user_prompt` is empty, it sends a default message to the message channel.
    """
    if message.author == client.user:
        return

    # if a user message starts with '$hello' the rest of the content will \
      # be stripped and passed in as the `user_prompt` for the `prompt_template`
    if message.content.startswith('$hello'):
        logging.info("\n----------\n\nMessage contains $hello.")

        # Extract the message text after '$hello'
        user_prompt = message.content[len('$hello'):].strip()
        logging.info("\n\nStripped user's message content. \n\n" + str(user_prompt))

        # Default message if no text is provided
        default_message = 'Hello! How can I assist you today?'

        if user_prompt:
          
            # Use `.format` to pass in the user's prompt
            prompt = prompt_template.format(user_prompt=user_prompt)
            # Pass the user's prompt for generation
            response = chain.invoke({"user_prompt": prompt})

            # Send the response once available
            await message.channel.send(response)
            logging.info("\nResponse sent to Discord.")

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
