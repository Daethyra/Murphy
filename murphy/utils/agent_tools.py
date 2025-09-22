import math
import os
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain.agents.tool_node import InjectedState
from langchain_core.tools import tool
from serpapi import GoogleSearch
from typing_extensions import Annotated
import trafilatura
from trafilatura.spider import focused_crawler

from .utilityfuncs import format_weather_data, is_binary_content


# Agent Tools
@tool
def get_weather(location: str) -> str:
    """Get current weather information for a specific location.
    Example: "portland oregon", "new york", "los angeles"
    """
    try:
        params = {
            "engine": "google_ai_mode",
            "q": f"{location} weather",
            "api_key": os.getenv("SERPAPI_KEY"),
            "location": "Portland, OR"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "text_blocks" in results and len(results["text_blocks"]) > 0:
            # Extract and format weather information from the text blocks
            weather_info = format_weather_data(results["text_blocks"])
            return f"Weather in {location}:\n{weather_info}"
        else:
            return f"Could not find weather information for {location}"
            
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

@tool
def web_search(query: str) -> str:
    """Retrieve an AI overview of a search query to Google. You can use anything that you would use in a regular Google search. e.g. inurl:, site:, intitle:. 
    """
    try:
        params = {
            "engine": "google_ai_mode",
            "q": f"{query}",
            "api_key": os.getenv("SERPAPI_KEY"),
            "location": "Portland, OR"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "text_blocks" in results and len(results["text_blocks"]) > 0:
            # Extract and format weather information from the text blocks
            output = results["text_blocks"]
            return f"{query} results:\n{output}"
        else:
            return f"Could not find search Google for {query}"
            
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

@tool
def clock():
    """Get the datetime. Returns datetime.now().strftime("%Y-%m-%d %I:%M %p")"""    
    return datetime.now().strftime("%Y-%m-%d %I:%M %p")

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression. You can use basic operators (+, -, *, /, ^) and functions like sqrt, sin, cos, etc.
    Example expressions: 
    - "2 + 3 * 4" 
    - "sqrt(16)" 
    - "sin(30) + cos(60)"
    """
    try:
        # Replace ^ with ** for exponentiation
        expression = expression.replace('^', '**')
        
        # Add math functions to the evaluation context
        safe_dict = {
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos, 
            'tan': math.tan, 'log': math.log, 'log10': math.log10,
            'pi': math.pi, 'e': math.e
        }
        
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, safe_dict)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

@tool
def search_chat_history(
    keyword_lookup: str,
    chat_history: Annotated[list, InjectedState("messages")]
) -> str:
    """Search through conversation history using advanced query operators to find specific messages in the chat history.
    Supports boolean operators (AND, OR, NOT), role filtering (user:, assistant:), exact phrases (quotes), wildcards (*), and date filters (after:, before:, on:).
    """
    try:
        # Convert LangChain message objects to dictionary format
        formatted_messages = []
        for msg in chat_history:
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                # This is a LangChain message object
                role_map = {
                    'human': 'user',
                    'ai': 'assistant',
                    'system': 'system'
                }
                role = role_map.get(msg.type, 'unknown')
                formatted_messages.append({
                    'role': role,
                    'content': msg.content
                })
            elif isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                # This is already in dictionary format
                formatted_messages.append(msg)
        
        messages = formatted_messages
        
        # Parse the search query for special operators
        query_parts = keyword_lookup.split()
        search_terms = []
        filters = {
            'role': None,
            'after': None,
            'before': None,
            'on_date': None,
            'case_sensitive': False,
            'limit': None,
            'exact_phrase': None
        }
        
        # Parse special operators from the query
        i = 0
        while i < len(query_parts):
            part = query_parts[i]
            
            if part.lower() in ['and', 'or', 'not']:
                # Boolean operators will be handled later
                search_terms.append(part.lower())
                i += 1
            elif part.startswith('user:') or part.startswith('assistant:'):
                filters['role'] = part.split(':', 1)[0].lower()
                i += 1
            elif part.startswith('after:'):
                try:
                    date_str = part.split(':', 1)[1]
                    filters['after'] = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    pass
                i += 1
            elif part.startswith('before:'):
                try:
                    date_str = part.split(':', 1)[1]
                    filters['before'] = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    pass
                i += 1
            elif part.startswith('on:'):
                try:
                    date_str = part.split(':', 1)[1]
                    filters['on_date'] = datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    pass
                i += 1
            elif part.startswith('case:'):
                case_val = part.split(':', 1)[1].lower()
                filters['case_sensitive'] = (case_val == 'true' or case_val == 'yes')
                i += 1
            elif part.startswith('limit:'):
                try:
                    filters['limit'] = int(part.split(':', 1)[1])
                except:
                    pass
                i += 1
            elif part.startswith('"') and part.endswith('"'):
                # Exact phrase match
                filters['exact_phrase'] = part[1:-1]
                i += 1
            else:
                # Regular search term
                search_terms.append(part)
                i += 1
        
        # Reconstruct the search query without special operators
        search_query = " ".join(search_terms)
        
        # If we have an exact phrase, use it instead of individual terms
        if filters['exact_phrase']:
            search_query = filters['exact_phrase']
        
        # Filter messages based on criteria
        matching_messages = []
        
        for msg in messages:
            # Check role filter
            if filters['role'] and msg['role'] != filters['role']:
                continue
                
            # Check date filters
            if 'timestamp' in msg:
                try:
                    msg_time = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                    
                    if filters['after'] and msg_time < filters['after']:
                        continue
                    if filters['before'] and msg_time > filters['before']:
                        continue
                    if filters['on_date'] and msg_time.date() != filters['on_date'].date():
                        continue
                except:
                    pass
            
            # Check content against search query
            content = msg['content']
            if not filters['case_sensitive']:
                content = content.lower()
                search_query = search_query.lower()
            
            # Handle boolean operators in search terms
            terms = search_terms.copy()
            if filters['exact_phrase']:
                # For exact phrase, we just check if the phrase exists
                if filters['exact_phrase'] in content:
                    matching_messages.append(msg)
            elif not terms:
                # No search terms, just filtering by other criteria
                matching_messages.append(msg)
            else:
                # Process boolean logic
                result = None
                current_op = 'and'  # Default operator
                
                for term in terms:
                    if term in ['and', 'or', 'not']:
                        current_op = term
                        continue
                    
                    # Check if term exists (with wildcard support)
                    term_exists = False
                    if '*' in term:
                        # Convert wildcard to regex pattern
                        pattern = term.replace('*', '.*')
                        if re.search(pattern, content):
                            term_exists = True
                    else:
                        term_exists = (term in content)
                    
                    # Apply boolean logic
                    if current_op == 'and':
                        if result is None:
                            result = term_exists
                        else:
                            result = result and term_exists
                    elif current_op == 'or':
                        if result is None:
                            result = term_exists
                        else:
                            result = result or term_exists
                    elif current_op == 'not':
                        if result is None:
                            result = not term_exists
                        else:
                            result = result and not term_exists
                
                if result:
                    matching_messages.append(msg)
        
        # Apply limit if specified
        if filters['limit']:
            matching_messages = matching_messages[:filters['limit']]
        
        if not matching_messages:
            return f"No messages found matching your query: '{keyword_lookup}'"
        
        # Format the results with context
        result = f"Found {len(matching_messages)} messages matching your query:\n\n"
        
        for i, msg in enumerate(matching_messages, 1):
            # Add timestamp if available
            timestamp = ""
            if 'timestamp' in msg:
                timestamp = f" [{msg['timestamp']}]"
                
            result += f"{i}. [{msg['role'].upper()}]{timestamp}: {msg['content']}\n\n"
            
            # Add context (previous and next messages)
            msg_index = messages.index(msg)
            context_added = False
            
            # Previous message context
            if msg_index > 0:
                prev_msg = messages[msg_index - 1]
                result += f"   Context (previous): [{prev_msg['role'].upper()}]: {prev_msg['content'][:100]}...\n"
                context_added = True
                
            # Next message context
            if msg_index < len(messages) - 1:
                next_msg = messages[msg_index + 1]
                result += f"   Context (next): [{next_msg['role'].upper()}]: {next_msg['content'][:100]}...\n"
                context_added = True
                
            if context_added:
                result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error searching chat history: {str(e)}"

@tool
def read_webpage(url: str) -> str:
    """Use when you need to directly read a webpage or are given a direct link. Retrieves the page's main contents. Use repeatedly when given a direct link/list of URLs.
    """
    try:
        # Validate URL format
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return "Error: Invalid URL format. Please provide a complete URL with http:// or https://"
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check for binary content
        if is_binary_content(response, url):
            return "Error: Binary content detected (PDF, image, video, audio, or archive). This tool only processes text-based webpages."
        
        # Try multiple extraction methods
        
        # Method 1: Use trafilatura (more robust content extraction)
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded, include_links=False, include_tables=False)
                if content and len(content) > 100:  # Ensure we have meaningful content
                    return f"Content from {url}:\n\n{content}"
        except:
            pass  # Fall back to other methods
        
        # Method 2: Use BeautifulSoup with less aggressive filtering
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove obviously unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 
                            'header', 'form', 'iframe', 'button', 'input']):
            element.decompose()
        
        # Try to find the main content area with less specific selectors
        content_selectors = [
            'article', 'main', '[role="main"]', 
            '.content', '#content', '.main-content',
            '.post-content', '.entry-content', '.article-body',
            'div', 'section'  # More generic selectors as fallback
        ]
        
        main_content = None
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Find the element with the most text content
                elements.sort(key=lambda x: len(x.get_text()), reverse=True)
                main_content = elements[0]
                break
        
        # If no specific content area found, use the body but remove more clutter
        if not main_content:
            main_content = soup.body if soup.body else soup
            
            # Remove more potential clutter from body
            clutter_selectors = [
                '[class*="ad"]', '[id*="ad"]', 
                '[class*="banner"]', '[id*="banner"]',
                '[class*="popup"]', '[id*="popup"]',
                '[class*="modal"]', '[id*="modal"]',
                '[class*="cookie"]', '[id*="cookie"]',
                '[class*="newsletter"]', '[id*="newsletter"]',
                '.social-share', '.share-buttons',
                '.comments', '#comments',
                'nav', 'footer', 'header', 'aside'
            ]
            
            for selector in clutter_selectors:
                for element in main_content.select(selector):
                    element.decompose()
        
        # Extract text and clean it up
        text = main_content.get_text(separator='\n', strip=True)
        
        # Remove excessive whitespace and empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # If we still don't have meaningful content, try a different approach
        if len(cleaned_text) < 100:
            # Try to get at least the title and meta description
            title = soup.find('title')
            title_text = title.get_text() if title else "No title found"
            
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            desc_text = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else "No description found"
            
            cleaned_text = f"{title_text}\n\n{desc_text}"
        
        # # Truncate if too long (to avoid token limits)
        # max_length = 8000
        # if len(cleaned_text) > max_length:
        #     cleaned_text = cleaned_text[:max_length] + "... [content truncated]"
        # apparently not necessary, keeping code regardless
        
        return f"Content from {url}:\n\n{cleaned_text}"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"Error processing the webpage: {str(e)}"

@tool
def crawl_url(
    url: str, 
    max_links: int = 25,
    same_domain: bool = True
) -> str:
    """Extract outlinks from a webpage for further discovery and exploration.
    
    This tool is designed to help agents discover related content by extracting
    hyperlinks from a webpage. It's useful when you need to find additional
    resources or context related to the current page.
    """
    try:
        # Use Trafilatura's focused crawler to extract links
        to_visit, known_links = focused_crawler(
            url, 
            max_seen_urls=1,  # Only process the initial URL
            max_known_urls=max_links * 2  # Allow some buffer for filtering
        )
        
        # Filter links based on requirements
        if same_domain:
            from urllib.parse import urlparse
            base_domain = urlparse(url).netloc
            filtered_links = [
                link for link in to_visit 
                if urlparse(link).netloc == base_domain
            ]
        else:
            filtered_links = list(to_visit)
        
        # Limit to the requested number of links
        result_links = filtered_links[:max_links]
        
        if not result_links:
            return "No relevant outlinks found on this page."
        
        # Format the results
        formatted_output = f"Found {len(result_links)} outlinks:\n"
        for i, link in enumerate(result_links, 1):
            formatted_output += f"{i}. {link}\n"
            
        return formatted_output
        
    except Exception as e:
        return f"Error extracting outlinks: {str(e)}"