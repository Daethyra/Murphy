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

def is_binary_content(response, url) -> bool:
    """Quick check for binary content - return True if binary detected"""
    
    # 1. Content-Type check (fastest)
    content_type = response.headers.get('content-type', '').lower()
    if any(bt in content_type for bt in ['application/pdf', 'image/', 'video/', 'audio/']):
        return True
    
    # 2. File extension check
    if any(url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.zip', '.rar', '.exe', '.dmg']):
        return True
    
    # 3. Quick magic bytes check
    if len(response.content) >= 4:
        first_bytes = response.content[:4]
        if first_bytes.startswith(b'%PDF') or first_bytes.startswith(b'PK') or first_bytes.startswith(b'\x89PNG'):
            return True
    
    return False