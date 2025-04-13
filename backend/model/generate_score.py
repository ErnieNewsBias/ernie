import model_prediction as mp
from google import genai
import json
import time
import re

# Do a Gemini call to validate that the bias score is appropriate for the text snippet.
def gemini_validation_check(biases, quotes, url):
    # Use an f-string to ensure that bias and sentence are properly inserted.
    inp_text = f"""I am ranking quotes from news articles from extreme left to extreme right on the political spectrum.
The scale of the ranking is from -10 to +10, where -10 is extreme left, 0 is neutral, and +10 is extreme right.
I will provide a list of quotes, biases, and the url of the article these quotes were from. Assume the nth entry from either of the the lists corresponds to the same entry.


The quotes I am ranking are: "{quotes}"
The bias scores I am giving this text are: {biases}
The url of the article these quotes are from is: {url}

I also have a distribution of scores from -10 to + 10 for the outlets for the political spectrum, same as the bias ranking.
The distribution is as follows for the outlets:
  "Patribotics": -10.0,
  "Palmer Report": -9.53,
  "Occupy Democrats": -9.05,
  "Forward Progressives": -8.58,
  "Alternet": -8.11,
  "Daily Kos": -7.63,
  "Second Nexus": -7.16,
  "New Republic": -6.68,
  "Buzzfeed News": -6.21,
  "Huffington Post": -5.74,
  "MSNBC": -5.26,
  "Mother Jones": -4.79,
  "Daily Beast": -4.32,
  "Slate": -3.84,
  "The Intercept": -3.37,
  "Mic": -2.89,
  "Vox": -2.42,
  "Vanity Fair": -1.95,
  "Jacobin": -1.47,
  "The New Yorker": -1.0,
  "The Guardian": -1.0,
  "The Washington Post": -0.89,
  "The New York Times": -0.79,
  "Axios": -0.68,
  "Politico": -0.58,
  "NPR": -0.47,
  "BBC": -0.37,
  "AFP": -0.26,
  "AP": -0.16,
  "ABC News": -0.05,
  "USA Today": 0.05,
  "Bloomberg": 0.16,
  "Reuters": 0.26,
  "CBS News": 0.37,
  "PBS": 0.47,
  "The Wall Street Journal": 0.58,
  "Time": 0.68,
  "The Economist": 0.79,
  "The Hill": 0.89,
  "National Review": 1.0,
  "Daily Mail": 1.0,
  "The Standard": 2.0,
  "Examiner": 3.0,
  "Washington Times": 4.0,
  "The Federalist": 5.0,
  "Fox News": 6.0,
  "Daily Wire": 7.0,
  "Newsmax": 8.0,
  "Redstate": 9.0,
  "Infowars": 10.0

For each of the quote:bias pairs from the lists above, do the following steps and append to the output JSON as described later.

1st:
Validate the bias score I am giving this quote. If it seems like a realistic score, keep it, but if it seems unrealistic, give me a new score.
For example, if the quote is clearly leftist in nature, but the score given is positive, adjust the bias score to be a more reasonable number in the negatives.

2nd:
Figure out from the url of the article, which outlet published the article
Check the validated bias score for the quote against the outlet score based on the outlet its from, to see if it is realistic.
If the assigned score is way off from the outlet's score, adjust it to be more realistic, using a distribution weighed at 30% bias score and 70% outlet score.
If the outlet does not exist in the list, make an approximation based on known public facts about the outlet.

3rd:
Create a JSON dictionary entry with the following format:
quote: <new bias score>,
where quote is the quote being analyzed, and the new bias score is the new validated number, rounded to the hundredths on the -10 to +10 scale.

Once these steps have been done, create one JSON object that contains all of the entries from the previous steps.
ONLY PROVIDE THIS JSON OBJECT IN THAT FORMAT, DO NOT PROVIDE ANY OTHER TEXT OR EXPLANATION. ALSO DO NOT INCLUDE BACKTICKS, I JUST WANT STRAIHGT JSON.
PROVIDE THE JSON OBJECT IN ONE LINE SO IT CAN BE READ INTO A JSON OBJECT IN PYTHON.
"""

    client = genai.Client(api_key="AIzaSyBJw8gvfRb2D7i4nmBrByRaDdJdQn6TTPs")
    gemini_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": inp_text
                    }
                ]
            }
        ]
    )
    print(type(gemini_response.text))

    print(gemini_response.text)

    out_gemini_response = gemini_response.text
    # remove first and last line of output
    lines = out_gemini_response.strip().split('\n')
    trimmed_out = "\n".join(lines[1:-1])

    print(trimmed_out)

    return trimmed_out

def generate_scores(quotes_list, url, use_local_model):
    start_time = time.time()
    print("Starting model prediction... @ ", start_time)

    # Get model predictions for all quotes first.
    bias_list = []
    for quote in quotes_list:
        # clean quote of special\u characters
        bias_score = mp.run_model_prediction(quote, use_local_model)
        print(f"Model prediction bias: {bias_score:.2f}")
        bias_list.append(bias_score)

    # Use one Gemini call to validate all bias scores at once.
    print("Calling Gemini for validation on all quotes at once...")
    gemini_output = gemini_validation_check(bias_list, quotes_list, url)

    print("Gemini validation output: ", gemini_output)

    clean_string = re.sub(r'\\x[0-9A-Fa-f]{2}', '', gemini_output)

    print(clean_string)
    clean_string.strip()

    final_output = json.loads(clean_string)
    print("final average bias:", sum(final_output.values()) / len(final_output))


    print("end time: ", (time.time() - start_time))


quotes = [
      "These are not the only examples of problematic statements from Trump and his advisers on the basics of American democracy, but they are five that are most directly addressed by the citizenship test. Trump has also posted on Truth Social an image of himself wearing a crown with the phrase “LONG LIVE THE KING!” over a dispute on congestion pricing in New York City. He’s also mangled the number of articles in the Constitution (it’s seven), telling House Republicans, “I’m for Article I, I’m for Article II, I’m for Article XII.” And in a Truth Social post in 2022 that made false claims of election fraud, he called for the “termination of all rules, regulations and articles, even those found in the Constitution.” While those basic factual inaccuracies are unlikely to come up during a citizenship test, they certainly would raise eyebrows if you volunteered them at a naturalization hearing.",
      "But any interpretation is hard to square with either the separation of powers or federalism, especially since Trump was referring to an executive order. Correct answer: No one is above the law. In January, Trump posted a supposed quote from French emperor Napoleon Bonaparte on his Truth Social and X accounts, then reposted it from the White House X account and pinned it to the top of his feed.",
      "A day later, he reposted a variation of it with a portrait of Napoleon. The quote: “He who saves his Country does not violate any Law.” Trump adviser Elon Musk, meanwhile, has been known to claim, “The only rules are the ones dictated by the laws of physics. Everything else is a recommendation.” Correct answers: Checks and balances, or the separation of powers.",
      "Speaking at the National Republican Congressional Committee in April, Trump called for a federal bill on elections, which are run by the states under the elections clause of the Constitution. “The states are just an agent of the federal government,” he said. To be fair, Trump is correct that Congress has some power over elections, but his description of states as agents of the federal government does not jibe with the general principles of federalism.",
      "But if you were to ask these same questions of President Donald Trump and his top advisers, I’m not sure if their answers would be accepted by a United States Citizenship and Immigration Services officer. Let’s compare public statements from Trump and his allies with history and civics facts provided for test-takers by the U.S. government.",
      "In a May 2024 podcast on President Joe Biden’s student loan forgiveness, now-Deputy FBI Director Dan Bongino openly laughed at the idea of checks and balances. “That’s really funny,” he told his listeners, arguing that “the only thing that matters” is power. In response to an order from a judge barring the Department of Government Efficiency from accessing sensitive Treasury Department data, Vice President JD Vance posted on X that “Judges aren’t allowed to control the executive’s legitimate power.” Around the same time, Trump said at a news briefing, “It seems hard to believe that a judge could say, ‘We don’t want you to do that,’ so maybe we have to look at the judges because I think that’s a very serious violation.” Musk has gone even further, calling for the firing of federal judges, who serve lifetime appointments under the Constitution.",
      "Keep in mind that “passing” this portion of the test means merely getting six out of 10 questions correct. Correct answer: the Constitution. While speaking at a White House event for the National Governors Association in February, Trump asked Maine Gov.",
      "© 2025 MSNBC Cable, L.L.C.",
      "universities who protested the war in Gaza. “This is not about free speech,” he said. “This is about people that don’t have a right to be in the United States to begin with.",
      "No one has a right to a student visa. No one has a right to a green card.” However, as the citizenship test notes in the question itself, the First Amendment applies to everyone living in the United States, not just U.S. citizens."
    ]

url = "https://www.msnbc.com/opinion/msnbc-opinion/trump-constitution-citizenship-test-immigration-rcna200435"

generate_scores(quotes, url, use_local_model=True)
