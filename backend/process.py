from newspaper import Article
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from serpapi import GoogleSearch
from rank import rank_biased_quotes
from model.generate_score import generate_scores
from extract_text import extract_article_metadata, get_search_results
from concurrent.futures import ThreadPoolExecutor
import threading
import time
load_dotenv()

def get_ai_insights(text, url):
    """This function should take in text, url, and using gemini, send text, 
    and return ai notes about the article and similar article data"""
    thread_name = threading.current_thread().name
    print(f"[THREAD:{thread_name}] get_ai_insights: Starting for URL: {url}")
    print(f"[THREAD:{thread_name}] get_ai_insights: Text length: {len(text)} characters")
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print(f"[THREAD:{thread_name}] [ERROR] get_ai_insights: No Gemini API key found in environment variables")
        return "Unable to analyze article (API key missing)", {}
    
    print(f"[THREAD:{thread_name}] get_ai_insights: Initializing Gemini client")
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Define a function declaration for extracting information
    print(f"[THREAD:{thread_name}] get_ai_insights: Setting up function declaration")
    extract_information_declaration = {
        "name": "extract_information",
        "description": (
            "Extracts information from this article including ai notes and a search query for similar articles"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "ai_notes": {
                    "type": "string",
                    "description": "Give a brief description of the data set and potential bias that may be present"
                },
                "search_query":{
                    "type": "string",
                    "description": "Based on the topics/events/ideas discussed in this article, generate a neutral search query that will return similar articles. Do not include political bias, only capture the relevant event/information."
                }
            },
            "required": ["ai_notes", "search_query"]
        }
    }

    # Set up function calling and configuration
    print(f"[THREAD:{thread_name}] get_ai_insights: Configuring Gemini tools")
    tools = types.Tool(function_declarations=[extract_information_declaration])
    config = types.GenerateContentConfig(tools=[tools])
    
    print(f"[THREAD:{thread_name}] get_ai_insights: Creating prompt")
    prompt = (
        f"Extract information from this article text. Return a function call with ai_notes about the article content "
        f"and a neutral search query to find similar articles on the same topic.\n\n"
        f"Article Text: {text}"
    )
    print(f"[THREAD:{thread_name}] get_ai_insights: Prompt length: {len(prompt)} characters")

    try:
        # Call Gemini
        print(f"[THREAD:{thread_name}] get_ai_insights: Calling Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite-001",
            contents=prompt,
            config=config
        )
        print(f"[THREAD:{thread_name}] get_ai_insights: Received response from Gemini")

        # Extract the function call results
        print(f"[THREAD:{thread_name}] get_ai_insights: Extracting function call results")
        candidate = response.candidates[0]
        function_call = candidate.content.parts[0].function_call

        if function_call and function_call.name == "extract_information":
            print(f"[THREAD:{thread_name}] get_ai_insights: Successfully extracted function call")
            ai_notes = function_call.args.get("ai_notes")
            search_query = function_call.args.get("search_query")
            print(f"[THREAD:{thread_name}] get_ai_insights: ai_notes length: {len(ai_notes) if ai_notes else 0}")
            print(f"[THREAD:{thread_name}] get_ai_insights: search_query: '{search_query}'")
        else:
            print(f"[THREAD:{thread_name}] WARNING get_ai_insights: Invalid function call format received")
            ai_notes = "Unable to analyze article"
            search_query = None
        
        # Get similar articles
        print(f"[THREAD:{thread_name}] get_ai_insights: Processing search query")
        similar_articles = {}
        
        if search_query:
            print(f"[THREAD:{thread_name}] get_ai_insights: Getting search results for query: '{search_query}'")
            search_results = get_search_results(search_query)
            print(f"[THREAD:{thread_name}] get_ai_insights: Found {len(search_results)} search results")
        else:
            print(f"[THREAD:{thread_name}] WARNING get_ai_insights: No search query available")
            search_results = []
        
        print(f"[THREAD:{thread_name}] get_ai_insights: Processing search results")
        for i, article_url in enumerate(search_results):
            print(f"[THREAD:{thread_name}] get_ai_insights: Processing article {i+1}/{len(search_results)}: {article_url}")
            try:
                print(f"[THREAD:{thread_name}] get_ai_insights: Extracting metadata for {article_url}")
                metadata = extract_article_metadata(article_url)
                print(f"[THREAD:{thread_name}] get_ai_insights: Metadata extracted - Title: '{metadata['title'][:30]}...'")
                
                text_preview = metadata['text'][:150] + "..." if len(metadata['text']) > 150 else metadata['text']
                similar_articles[article_url] = {
                    "score": 0,  # Placeholder score
                    "title": metadata['title'],
                    "image_url": metadata['image_url'],
                    "text_preview": text_preview
                }
                print(f"[THREAD:{thread_name}] get_ai_insights: Added article to results: {article_url}")
            except Exception as e:
                print(f"[THREAD:{thread_name}] ERROR get_ai_insights: Error processing {article_url}: {str(e)}")
        
        print(f"[THREAD:{thread_name}] get_ai_insights: Finished processing. Found {len(similar_articles)} valid articles")
        print(f"[THREAD:{thread_name}] get_ai_insights: Returning ai_notes and {len(similar_articles)} similar articles")
        return ai_notes, similar_articles, search_query
        
    except Exception as e:
        print(f"[THREAD:{thread_name}] ERROR get_ai_insights: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Unable to analyze article", {}, None


def get_bias_score(text, url):
    """This function should take in some text, then pass it to the function in rank.py to 
    get a list of quotes that may have bias, then pass the list of quotes to the function in model generate score
    then format and return the bias score data.
    """
    thread_name = threading.current_thread().name
    print(f"[THREAD:{thread_name}] get_bias_score: Starting bias analysis")
    print(f"[THREAD:{thread_name}] get_bias_score: Getting quotes from rank_biased_quotes")
    
    start_time = time.time()
    bias_quotes = rank_biased_quotes(text, n=10)
    quote_time = time.time()
    print(f"[THREAD:{thread_name}] get_bias_score: Found {len(bias_quotes)} quotes in {quote_time - start_time:.2f} seconds")
    
    print(f"[THREAD:{thread_name}] get_bias_score: Scoring quotes with generate_scores")
    bias_score = generate_scores(bias_quotes, url, use_local_model=False)
    end_time = time.time()
    print(f"[THREAD:{thread_name}] get_bias_score: Finished scoring in {end_time - quote_time:.2f} seconds")
    
    return bias_score


def process_url(url):
    thread_name = threading.current_thread().name
    print(f"[THREAD:{thread_name}] process_url: Starting for URL: {url}")
    
    print(f"[THREAD:{thread_name}] process_url: Extracting article metadata")
    article = extract_article_metadata(url)
    text = article['text']
    print(f"[THREAD:{thread_name}] process_url: Extracted {len(text)} characters of text")

    print(f"[THREAD:{thread_name}] process_url: Setting up ThreadPoolExecutor")
    # Run both processes in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both tasks
        print(f"[THREAD:{thread_name}] process_url: Submitting AI insights task")
        ai_future = executor.submit(get_ai_insights, text, url)
        
        print(f"[THREAD:{thread_name}] process_url: Submitting bias score task")
        bias_future = executor.submit(get_bias_score, text, url)
        
        print(f"[THREAD:{thread_name}] process_url: Waiting for tasks to complete")
        # Get results when both are complete
        ai_notes, similar_articles, search_query = ai_future.result()
        print(f"[THREAD:{thread_name}] process_url: AI insights task completed")
        
        bias_score = bias_future.result()
        print(f"[THREAD:{thread_name}] process_url: Bias score task completed")

    print(f"[THREAD:{thread_name}] process_url: All tasks completed, returning results")
    return ai_notes, similar_articles, bias_score, search_query


#process_url("https://www.plannedparenthoodaction.org/planned-parenthood-action-fund-pacific-southwest/blog/abortion-bans-are-deadly#:~:text=Experts%20have%20repeatedly%20warned%20that,aspects%20of%20health%20and%20pregnancy.")