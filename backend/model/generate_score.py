from . import model_prediction as mp
from google import genai
import json
import time
import re
import os
from google.genai import types
import threading

# Do a Gemini call to validate that the bias score is appropriate for the text snippet.
def gemini_validation_check(biases, quotes, url):
    """
    Uses Gemini API with structured function calling to validate bias scores for quotes.
    """
    thread_name = threading.current_thread().name
    print(f"[THREAD:{thread_name}] gemini_validation_check: Starting validation")
    print(f"[THREAD:{thread_name}] gemini_validation_check: Quotes count: {len(quotes)}")
    print(f"[THREAD:{thread_name}] gemini_validation_check: Biases count: {len(biases)}")
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Modified schema to avoid additionalProperties
    validation_declaration = {
        "name": "validate_bias_scores",
        "description": "Validates and adjusts bias scores for quotes based on content and outlet",
        "parameters": {
            "type": "object",
            "properties": {
                "validated_scores": {
                    "type": "object",
                    "description": "Dictionary with quotes as keys and validated bias scores as values"
                }
            },
            "required": ["validated_scores"]
        }
    }

    print(f"[THREAD:{thread_name}] Schema definition complete")
    # Set up the function calling tool and configuration
    tools = types.Tool(function_declarations=[validation_declaration])
    config = types.GenerateContentConfig(tools=[tools])
    print(f"[THREAD:{thread_name}] Tool configuration complete")

    # Debugging: Print the first few quotes and scores
    for i, (quote, bias) in enumerate(zip(quotes[:3], biases[:3])):
        print(f"[THREAD:{thread_name}] [DEBUG] Quote {i} preview: {quote[:50]}..., Bias: {bias}")

    # Create a simpler format for the prompt to ensure compatibility
    prompt = f"""
I need you to validate bias scores for quotes from a news article.

The initial bias scores for these quotes range from -10 (extreme left) to +10 (extreme right).
For each quote, please:
1. Validate if the score makes sense given the quote content
2. Consider the media outlet bias from the URL: {url}
3. Return the validated scores as a dictionary with quotes as keys and scores as values

Raw data:
- Quotes: {quotes}
- Initial bias scores: {biases}

Return ONLY a function call to validate_bias_scores with a validated_scores object 
where keys are the exact quotes and values are the adjusted scores as numbers.
"""

    print(f"[THREAD:{thread_name}] [DEBUG] Prompt created")
    print(f"[THREAD:{thread_name}] [DEBUG] Prompt length: {len(prompt)} characters")
    
    try:
        print(f"[THREAD:{thread_name}] [DEBUG] Calling Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        print(f"[THREAD:{thread_name}] [DEBUG] Received response from Gemini")
        
        # Extract and debug function call
        candidate = response.candidates[0]
        if not hasattr(candidate.content, 'parts') or not candidate.content.parts:
            print(f"[THREAD:{thread_name}] [ERROR] No parts in content")
            return {quote: bias for quote, bias in zip(quotes, biases)}
            
        part = candidate.content.parts[0]
        print(f"[THREAD:{thread_name}] [DEBUG] Response part type: {type(part)}")
        
        if not hasattr(part, 'function_call'):
            print(f"[THREAD:{thread_name}] [ERROR] No function_call in part")
            print(f"[THREAD:{thread_name}] [DEBUG] Part content: {part}")
            return {quote: bias for quote, bias in zip(quotes, biases)}
            
        function_call = part.function_call
        print(f"[THREAD:{thread_name}] [DEBUG] Function call name: {function_call.name}")
        
        if function_call and function_call.name == "validate_bias_scores":
            print(f"[THREAD:{thread_name}] [DEBUG] Successfully received validate_bias_scores function call")
            
            if not hasattr(function_call, 'args'):
                print(f"[THREAD:{thread_name}] [ERROR] No args in function_call")
                return {quote: bias for quote, bias in zip(quotes, biases)}
                
            args = function_call.args
            print(f"[THREAD:{thread_name}] [DEBUG] Args keys: {args.keys() if hasattr(args, 'keys') else 'No keys method'}")
            
            validated_scores = args.get("validated_scores", {})
            print(f"[THREAD:{thread_name}] [DEBUG] validated_scores type: {type(validated_scores)}")
            
            if validated_scores:
                print(f"[THREAD:{thread_name}] [DEBUG] First few keys: {list(validated_scores.keys())[:2]}")
                print(f"[THREAD:{thread_name}] [DEBUG] First few values: {list(validated_scores.values())[:2]}")
            
            # Handle potential string values
            result = {}
            for key, value in validated_scores.items():
                print(f"[THREAD:{thread_name}] [DEBUG] Processing key: {key[:30]}...")
                try:
                    if isinstance(value, str):
                        result[key] = float(value)
                        print(f"[THREAD:{thread_name}] [DEBUG] Converted string '{value}' to float")
                    else:
                        result[key] = value
                except ValueError as ve:
                    print(f"[THREAD:{thread_name}] [WARNING] Could not convert value '{value}' to float: {ve}")
                    result[key] = 0.0
                    
            print(f"[THREAD:{thread_name}] [DEBUG] Result has {len(result)} entries")
            return result
        else:
            print(f"[THREAD:{thread_name}] [ERROR] Expected function name 'validate_bias_scores', got: {function_call.name if function_call else 'None'}")
            return {quote: bias for quote, bias in zip(quotes, biases)}
            
    except Exception as e:
        print(f"[THREAD:{thread_name}] [ERROR] gemini_validation_check: {str(e)}")
        import traceback
        traceback.print_exc()
        return {quote: bias for quote, bias in zip(quotes, biases)}

def generate_scores(quotes_list, url, use_local_model):
    start_time = time.time()
    
    try:
        # Get model predictions for all quotes first.
        bias_list = []
        for quote in quotes_list:
            try:
                bias_score = mp.run_model_prediction(quote, use_local_model)
                bias_list.append(bias_score)
                print(f"Good Length: {len(quote)}")
            except Exception as e:
                print(f"Bad Length: {len(quote)}")
                print(f"Error processing quote: {e}")
                # Add a neutral score if prediction fails
                bias_list.append(0.0)
        print(bias_list)
        
        # Use one Gemini call to validate all bias scores at once.
        try:
            final_output = gemini_validation_check(bias_list, quotes_list, url)
            return final_output
        except Exception as e:
            print(f"Error with Gemini validation: {e}")
            return {quote: bias for quote, bias in zip(quotes_list, bias_list)}
            
    except Exception as e:
        print(f"Unexpected error in generate_scores: {e}")
        return {}


# quotes = [
#       "These are not the only examples of problematic statements from Trump and his advisers on the basics of American democracy, but they are five that are most directly addressed by the citizenship test. Trump has also posted on Truth Social an image of himself wearing a crown with the phrase "LONG LIVE THE KING!" over a dispute on congestion pricing in New York City. He's also mangled the number of articles in the Constitution (it's seven), telling House Republicans, "I'm for Article I, I'm for Article II, I'm for Article XII." And in a Truth Social post in 2022 that made false claims of election fraud, he called for the "termination of all rules, regulations and articles, even those found in the Constitution." While those basic factual inaccuracies are unlikely to come up during a citizenship test, they certainly would raise eyebrows if you volunteered them at a naturalization hearing.",
#       "But any interpretation is hard to square with either the separation of powers or federalism, especially since Trump was referring to an executive order. Correct answer: No one is above the law. In January, Trump posted a supposed quote from French emperor Napoleon Bonaparte on his Truth Social and X accounts, then reposted it from the White House X account and pinned it to the top of his feed.",
#       "A day later, he reposted a variation of it with a portrait of Napoleon. The quote: "He who saves his Country does not violate any Law." Trump adviser Elon Musk, meanwhile, has been known to claim, "The only rules are the ones dictated by the laws of physics. Everything else is a recommendation." Correct answers: Checks and balances, or the separation of powers.",
#       "Speaking at the National Republican Congressional Committee in April, Trump called for a federal bill on elections, which are run by the states under the elections clause of the Constitution. "The states are just an agent of the federal government," he said. To be fair, Trump is correct that Congress has some power over elections, but his description of states as agents of the federal government does not jibe with the general principles of federalism.",
#       "But if you were to ask these same questions of President Donald Trump and his top advisers, I'm not sure if their answers would be accepted by a United States Citizenship and Immigration Services officer. Let's compare public statements from Trump and his allies with history and civics facts provided for test-takers by the U.S. government.",
#       "In a May 2024 podcast on President Joe Biden's student loan forgiveness, now-Deputy FBI Director Dan Bongino openly laughed at the idea of checks and balances. "That's really funny," he told his listeners, arguing that "the only thing that matters" is power. In response to an order from a judge barring the Department of Government Efficiency from accessing sensitive Treasury Department data, Vice President JD Vance posted on X that "Judges aren't allowed to control the executive's legitimate power." Around the same time, Trump said at a news briefing, "It seems hard to believe that a judge could say, 'We don't want you to do that,' so maybe we have to look at the judges because I think that's a very serious violation." Musk has gone even further, calling for the firing of federal judges, who serve lifetime appointments under the Constitution.",
#       "Keep in mind that "passing" this portion of the test means merely getting six out of 10 questions correct. Correct answer: the Constitution. While speaking at a White House event for the National Governors Association in February, Trump asked Maine Gov.",
#       "© 2025 MSNBC Cable, L.L.C.",
#       "universities who protested the war in Gaza. "This is not about free speech," he said. "This is about people that don't have a right to be in the United States to begin with.",
#       "No one has a right to a student visa. No one has a right to a green card." However, as the citizenship test notes in the question itself, the First Amendment applies to everyone living in the United States, not just U.S. citizens."
#     ]

# url = "https://www.msnbc.com/opinion/msnbc-opinion/trump-constitution-citizenship-test-immigration-rcna200435"

# generate_scores(quotes, url, use_local_model=True)
