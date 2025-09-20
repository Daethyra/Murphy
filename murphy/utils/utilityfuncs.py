# for `web_search` agent tool
def format_weather_data(text_blocks):
    """Format the weather data from text_blocks into a readable string"""
    formatted_text = ""
    
    for block in text_blocks:
        if block["type"] == "paragraph":
            formatted_text += f"{block['snippet']}\n\n"
        elif block["type"] == "heading":
            formatted_text += f"--- {block['snippet']} ---\n"
        elif block["type"] == "list" and "list" in block:
            for item in block["list"]:
                formatted_text += f"• {item['snippet']}\n"
            formatted_text += "\n"
    
    return formatted_text.strip()

def split_message(message, max_length=2000):
    """Split a message into chunks that fit within Discord's character limit"""
    if len(message) <= max_length:
        return [message]
    
    # Simple approach: split into chunks of max_length
    chunks = []
    for i in range(0, len(message), max_length):
        chunk = message[i:i+max_length]
        chunks.append(chunk)
    
    return chunks