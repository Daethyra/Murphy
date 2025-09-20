# 🕷️ Spider Murphy - Discord AI Agent

![Spider Murphy](./assets/spider-murphy.jpeg)

**Flexible LangChain Agent**

## Overview

Spider Murphy is a sophisticated Discord AI agent that embodies the iconic netrunner from Cyberpunk 2077. Built with LangChain and DeepSeek AI, this bot combines cutting-edge language model capabilities with practical tools for real-time information retrieval and conversation.

## Features

### 🤖 **AI Personality & Character**
- **Authentic Spider Murphy persona** from Cyberpunk 2077 lore
- **Cyberpunk-themed responses** with netrunner jargon and attitude (wow it got old fast!)
- **Context-aware conversations** with memory persistence

### 🛠️ **Agent Tools & Capabilities**
- **`get_weather`** - Real-time weather information for any location
- **`web_search`** - Google AI-powered search with advanced query support
- **`clock`** - Current date and time retrieval  
- **`calculate`** - Mathematical expression evaluation with math functions
- **`search_chat_history`** - Advanced conversation search with boolean operators
- **`read_webpage`** - Web content extraction using Trafilatura + BeautifulSoup

### 💬 **Smart Conversation Features**
- **Contextual awareness** - Maintains conversation history and thread context
- **File attachment processing** - Reads and processes `message.txt` attachments
- **Reply chain tracking** - Understands message replies and references
- **Thread-aware responses** - Handles Discord threads intelligently
- **Message splitting** - Automatically handles Discord's 2000-character limit

## Architecture

### **Core Components**
```python
murphy/
├── chatbot.py              # Main Discord bot implementation
├── utils/
│   ├── agent_tools.py      # LangChain tool definitions
│   └── utilityfuncs.py     # Helper functions and utilities
└── requirements.txt        # Dependencies
```

### **Technology Stack**
- **Discord.py** - Discord bot framework
- **LangChain** - AI agent orchestration
- **DeepSeek AI** - Primary language model (deepseek-chat)
- **Trafilatura** - Web content extraction
- **BeautifulSoup** - HTML parsing fallback
- **SerpAPI** - Google search integration

## Setup & Installation

### **Prerequisites**
```bash
# Clone the repository
git clone https://github.com/Daethyra/Murphy.git
cd Murphy

# Install dependencies
pip install -r requirements.txt
```

### **Environment Variables**
Create a `.env` file with:
```env
DISCORD_TOKEN=your_discord_bot_token_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here  
SERPAPI_KEY=your_serpapi_key_here
```

### **Running the Bot**
```bash
python -m murphy.chatbot
```

## Usage

### **Basic Commands**
- **Mention the bot** (`@Spider Murphy`) in any channel
- **Direct messages** for private conversations
- **Thread mentions** for focused discussions

### **Tool Usage Examples**
```
@Spider Murphy what's the weather in Night City?
@Spider Murphy search for "look up recent attacks on free speech in September"
@Spider Murphy calculate sqrt(256) + 2^8
@Spider Murphy search_chat_history user:Daethyra AND "web scraping"
@Spider Murphy read https://example.com/article
```

### **Advanced Features**
- **File attachments**: Send `message.txt` with additional context(copy/pasting large amounts of text)
- **Thread context**: Bot remembers conversation history in threads
- **Boolean search**: Use `AND`, `OR`, `NOT` operators in chat history searches
- **Role filtering**: `user:username` or `assistant:` in searches
- **Date filters**: `after:2024-01-01`, `before:2024-12-31`

## Customaization

### **Modifying Personality**
Edit the system prompt in `chatbot.py` to adjust Spider Murphy's character traits, speech patterns, or knowledge base.

### **Adding New Tools**
1. Define new tools in `agent_tools.py` using `@tool` decorator
2. Import and add to tools list in `chatbot.py`
3. Update requirements if needed

**Check the LangChain documentation for help**
  - [Agents](https://docs.langchain.com/oss/python/langchain/tools)
  - [Tools](https://docs.langchain.com/oss/python/langchain/tools)
  - [Memory](https://docs.langchain.com/oss/python/langchain/short-term-memory)

### **Model Configuration**
Change AI model parameters in `chatbot.py`:
```python
model = ChatDeepSeek(
    temperature=0.67,  # Adjust creativity
    model="deepseek-chat",
    # max_tokens=2048,  # Control response length
)
```

**Web extraction failures**: Trafilatura may fail on JS-heavy sites

## 📜 LICENSE

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for full details.

---