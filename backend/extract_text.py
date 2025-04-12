from newspaper import Article
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()


def extract_important_text(url):
    """
    Uses newspaper3k to download and parse an article from the given URL,
    returning the main article text which usually excludes extraneous content.
    """
    article = Article(url)
    article.download()
    article.parse()
    #print(article.text)
    return article.text

def extract_score(text):
    """
    Calls the Gemini API using function calling to determine a political bias score
    from the provided article text. The function declaration 'extract_bias' expects a 
    single parameter 'bias' (an integer between -10 and 10, where -10 indicates extreme 
    left and 10 indicates extreme right). The function returns this bias as an integer.
    """
    # Replace with your actual Gemini API key or set it as an environment variable.
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Define a function declaration for extracting the bias.
    extract_bias_declaration = {
        "name": "extract_bias",
        "description": (
            "Extracts a political bias score from an article's text. "
            "The bias score is an integer between -10 (extreme left) and 10 (extreme right)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "bias": {
                    "type": "integer",
                    "description": "Political bias score; -10 for extreme left to 10 for extreme right. Make sure to assign the number based on the political bias of the text"
                },
                "ai_notes": {
                    "type": "string",
                    "description": "Give a brief description of the data set and potential bias that may be present"
                },
                "bias_quotes": {
                    "type": "string",
                    "description": "Give a short list of 1-5 quotes that reflect the bias in this article. Please write them with newline seperators. Make sure the quotes match actual text from the article verbatum"
                }

            },
            "required": ["bias", "ai_notes", "bias_quotes"]
        }
    }

    # Set up the function calling tool and configuration.
    tools = types.Tool(function_declarations=[extract_bias_declaration])
    config = types.GenerateContentConfig(tools=[tools])

    # Create a prompt instructing Gemini to determine the bias.
    prompt = (
        "Determine the political bias of the following article text. "
        "Return a function call to 'extract_bias' with the parameter 'bias' set to an integer between -10 "
        "(extreme left) and 10 (extreme right). Only respond with the function call, nothing else.\n\n"
        f"Article Text: {text}"
    )

    #print(prompt)

    # Call Gemini using the generate_content method with the configuration.
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite-001",
        contents=prompt,
        config=config
    )

    # Extract the function call from the first candidate's first part.
    candidate = response.candidates[0]
    function_call = candidate.content.parts[0].function_call

    # If a function call is returned and it matches our declaration, extract the bias.
    if function_call and function_call.name == "extract_bias":
        # Expecting function_call.args to be a dict with key "bias".
        bias = int(function_call.args.get("bias", 0))

        # Ensure the bias is within the range -10 to 10.
        bias = max(min(bias, 10), -10)

        ai_notes = function_call.args.get("ai_notes")
        bias_quotes = function_call.args.get("bias_quotes")
        return bias, ai_notes, bias_quotes
    else:
        # If no valid function call is returned, default to a neutral bias.
        return 0
