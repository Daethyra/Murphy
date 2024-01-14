# Currency Bot

Currency Bot is a Discord bot that generates responses based on user prompts. By using an event handler to process messages we can create a chatbot that only response to messages prefixed with `$hello`. For responses, it uses LangChain for all generative AI functionality.

## Installation

1. Clone the repository: `git clone https://github.com/daethyra/currency-bot.git`
2. Navigate to the project directory: `cd currency-bot`
3. Install the dependencies: 
    1. `pip install -U pdm`
    2. `pdm install`
4. Set up the environment variables:
   - Create a copy of `template.env` and name the copy, `.env` and place it in the project's root directory.
   - Note: You will need to create the bot's token via Discord's developer portal. Save that token's value inside the `.env` file.
5. Start the bot: `python src/messages_handler.py`

## Usage

Once the bot is running, you can interact with it on Discord by sending messages in a server where the bot is present. The bot will respond to various commands related to currency conversion.

## Contributing

Contributions to Currency Bot are welcome! If you have any bug reports, feature requests, or code improvements, please submit them as issues or pull requests on the GitHub repository.

## License

Currency Bot is licensed under the GNU AGPLv3 License. See the [LICENSE](LICENSE) file for more details.