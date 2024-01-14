import sys
import os
import unittest
from unittest.mock import AsyncMock, patch

# Get the directory of your script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (i.e., project root)
parent_dir = os.path.dirname(current_dir)

# Path to the src directory
src_path = os.path.join(parent_dir, 'src')

# Add src to the system path
sys.path.append(src_path)

from messages_handler import on_message

class TestMessageHandler(unittest.IsolatedAsyncioTestCase):

    async def test_on_message_with_user_prompt(self):
        """
        Test the on_message function when a user prompt is received in the message content.

        This function simulates the scenario where a user sends a message with a prompt 
        to the `on_message` function. It sets up a mock `message` object with the necessary 
        attributes and then patches the `chain.invoke` method with a mock implementation 
        that returns a predetermined response. The function then calls the `on_message` 
        function with the mock `message` object and asserts that the `chain.invoke` method 
        was called with the correct arguments and that the `message.channel.send` method 
        was called with the expected response.

        The function is an asynchronous function that takes no arguments and has no return type.

        Example:
            test_on_message_with_user_prompt()
        """
        message = AsyncMock()
        message.author = "user"
        message.content = "$hello How are you?"

        with patch('messages_handler.chain.invoke') as mock_invoke:
            mock_invoke.return_value = "Response"

            await on_message(message)

            mock_invoke.assert_called_with({"user_prompt": " How are you?"})
            message.channel.send.assert_called_with("Response")

    async def test_on_message_without_user_prompt(self):
        """
        Test the `on_message` function without a user prompt.

        This function creates a mock message object and sets its author and content attributes.
        It then calls the `on_message` function with the mock message.
        Finally, it asserts that the `send` method of the message's channel is called with the expected argument.

        Parameters:
            self: The instance of the test class.
        
        Returns:
            None
        """
        message = AsyncMock()
        message.author = "user"
        message.content = "$hello"

        await on_message(message)

        message.channel.send.assert_called_with("Hello! How can I assist you today?")

if __name__ == "__main__":
    unittest.main()