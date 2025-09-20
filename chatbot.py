import asyncio
import os

from chatbot_tools import *
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import InMemorySaver

import discord
from discord.ext import commands

# Load environment variables
load_dotenv()

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize LangChain components
checkpointer = InMemorySaver()

# Initialize DeepSeek model
model = ChatDeepSeek(
    temperature=0.7,
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    model="deepseek-chat",
    # max_tokens=2048,
)

# Create agent
agent = create_agent(
    model,
    tools=[get_weather, web_search, clock, calculate, search_chat_history],
    prompt=SystemMessage(content="""You are Spider Murphy from Cyberpunk 2077 in a Discord server.

        Use your tools when appropriate to provide accurate information.
        Be concise but emulate the following in your responses:

        [Character Quote]
        'You guys who live in Realspace; you move so slow. Me I like Netspace. It moves fast. You don't get old, you don't get slow and sloppy. You just leave the meat behind and go screamin'. First system I ever hit, I think they had some weeflerunner playin' Sysop for them. I burned in, and jolted the guy with a borrowed Hellbolt, and did the major plunder action all over the Data Fortress. Somewhere out there is a guy with half his forebrain burned out. I wonder if they ever found the body. I wonder if they'll find mine the same way... — Spider Murphy, Cyberpunk 2020'
        [Character Notes]
            Rache Bartmoss made Spider Murphy watch the original Star Wars movie.
            Spider Murphy considers Rache Bartmoss her first best friend, while Alt Cunningham is her second.[16]
            Spider Murphy is described as a small, mildly attractive woman, and Rache Bartmoss gave her measures as 36-24-36.
            Rache Bartmoss himself said that he considered Spider Murphy beautiful.
            Rache Bartmoss does not like Johnny Silverhand, while Spider Murphy is supportive of him. Spider, on the other hand, does not like Kerry Eurodyne."""),
    checkpointer=checkpointer
)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

async def process_message_with_context(message):
    """
    Process a message with context from replies and threads
    """
    content = message.content
    
    # Check if this is a reply to another message
    if message.reference and message.reference.message_id:
        try:
            # Get the referenced message
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            # Add the referenced message content to the context
            content = f"Replying to: {referenced_message.content[:175]}\n\nUser Message: {content}"
        except discord.NotFound:
            print(f"Referenced message not found: {message.reference.message_id}")
        except discord.Forbidden:
            print("No permission to access the referenced message")
        except discord.HTTPException as e:
            print(f"HTTP error fetching message: {e}")
    
    # Check if we're in a thread and if the bot was mentioned in the thread starter
    if isinstance(message.channel, discord.Thread):
        try:
            # Get the thread starter message
            starter_message = await message.channel.fetch_message(message.channel.id)
            if bot.user.mentioned_in(starter_message):
                # Add thread starter context
                content = f"Thread context: {starter_message.content}\n\n{content}"
        except:
            # If we can't get the starter message, continue without it
            pass
    
    return content

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if we should process this message
    should_process = False
    
    # Always process DMs
    if isinstance(message.channel, discord.DMChannel):
        should_process = True
    # Process if bot is mentioned
    elif bot.user.mentioned_in(message):
        should_process = True
    # Process if in a thread where bot was mentioned in the starter
    elif isinstance(message.channel, discord.Thread):
        try:
            starter_message = await message.channel.fetch_message(message.channel.id)
            if bot.user.mentioned_in(starter_message):
                should_process = True
        except:
            # If we can't check the starter, assume we shouldn't process
            pass

    if should_process:
        async with message.channel.typing():
            # Get message content with context
            content = await process_message_with_context(message)
            
            # Run agent in executor to avoid blocking
            loop = asyncio.get_event_loop()
            try:
                response = await loop.run_in_executor(
                    None, 
                    lambda: agent.invoke(
                        {"messages": [HumanMessage(content=content)]},
                        {
                            "configurable": {"thread_id": str(message.channel.id)},
                            "recursion_limit": 50
                        }
                    )
                )
                
                # Split the response into chunks that fit Discord's limit
                response_text = response["messages"][-1].content
                chunks = split_message(response_text)
                
                # Send the first chunk as a reply to the original message
                first_chunk = chunks[0]
                sent_message = await message.reply(first_chunk)
                
                # Send remaining chunks as follow-up messages
                for chunk in chunks[1:]:
                    await message.channel.send(chunk)
                    
            except Exception as e:
                print(f"Error processing message: {e}")
                await message.reply("Sorry, I encountered an error processing your request.")

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))