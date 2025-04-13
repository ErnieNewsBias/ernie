import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Optional

def rank_biased_quotes(text: str, n: int = 5, model_id: str = "BAAI/bge-large-en-v1.5") -> List[str]:
    """
    Rank text chunks by their potential political bias and return the top n most biased quotes.
    
    Args:
        text: Input article or text to analyze
        n: Number of biased quotes to return (default: 5)
        model_id: Sentence transformer model to use (default: BAAI/bge-large-en-v1.5)
        
    Returns:
        List of strings containing the most biased quotes ranked by bias score
    """
    # Load the embedding model
    try:
        model = SentenceTransformer(model_id)
    except Exception as e:
        raise Exception(f"Error loading model: {e}")
    
    # Chunk the text into paragraphs and multi-sentence chunks
    def chunk_text(text):
        # First split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # For each paragraph, split into chunks of multiple sentences
        chunks = []
        for para in paragraphs:
            # If paragraph is within reasonable size, keep it as is
            if len(para.split()) < 150:  # Increased threshold to allow longer chunks
                chunks.append(para)
            else:
                # Split into sentences for long paragraphs
                sentences = re.split(r'(?<=[.!?])\s+', para)
                
                # Group sentences into multi-sentence chunks
                current_chunk = ""
                sentence_count = 0
                
                for sentence in sentences:
                    # Try to get 2-4 sentences per chunk, or respect word limit
                    if (sentence_count < 3 and len(current_chunk.split()) + len(sentence.split()) < 200) or not current_chunk:
                        current_chunk += " " + sentence if current_chunk else sentence
                        sentence_count += 1
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                        sentence_count = 1
                        
                if current_chunk:  # Add the last chunk
                    chunks.append(current_chunk.strip())
        
        return chunks
    
    # Apply chunking to our text
    chunks = chunk_text(text)
    if not chunks:
        return []
    
    # Define bias detection queries
    bias_queries = [
        "This text shows political partisan bias in its foundation or claims",
        "This text uses politically charged language or framing",
        "This statement presents a one-sided political viewpoint without acknowledging alternatives",
        "This text contains unsupported political claims presented as facts"
    ]
    
    # Embed chunks and queries
    chunk_embeddings = model.encode(chunks)
    query_embeddings = model.encode(bias_queries)
    
    # Compute similarities between each query and each chunk
    similarity_scores = []
    for query_embedding in query_embeddings:
        similarities = cosine_similarity([query_embedding], chunk_embeddings)[0]
        similarity_scores.append(similarities)
    
    # Average similarity across all bias queries for each chunk
    avg_similarity = np.mean(similarity_scores, axis=0)
    
    # Get indices sorted by average similarity (highest first)
    ranked_indices = np.argsort(avg_similarity)[::-1]
    
    # Return top n biased quotes
    top_n = min(n, len(chunks))
    return [chunks[idx] for idx in ranked_indices[:top_n]]


if __name__ == "__main__":
    # Example usage
    sample_text = """
    Decisions of the U.S. Supreme Court rarely attract much public interest. One news cycle and a few days' discussion in the op-ed section is probably the norm for even the most important and sweeping decisions. The average person probably has to cast back to a high school history course to recall the names of even a few landmark cases other than Miranda v. Arizona (known mainly from the scripts of popular police shows).
But one Supreme Court decision eclipses all others in the past century. Far from being forgotten, in the thirty years since Roe v. Wade announced that the "constitutional" right to privacy encompasses a woman's decision to abort her child, its fame (or infamy) just keeps growing.
How Roe is Perceived
For many Americans, Roe is a symptom of and catalyst for a continuing decline in American culture and institutions. It represents a tragic failure of the government, an abdication of its duty to defend the vulnerable and innocent. The judicially-created regime permitting abortion on request throughout pregnancy has eroded principles on which this nation was founded – the sanctity of life, the equal dignity of all, and impartial justice. Even the fundamental principle of self-government is shaken when seven unelected judges can overturn the will of the people expressed in the laws of 50 states. And how does one begin to assess the meaning and impact of destroying over 40 million children?
Many other Americans, less attuned to public policy matters, hold a very different view of Roe v. Wade. They see Roe as being immutable, permanent, "settled law." "Abortion is a constitutional right." End of discussion. In thirty years, the Roe abortion license has been elevated by some to the stature of "freedom of speech," "trial by jury" and other bedrock American principles.
It is not surprising that many people share this distorted view of Roe v. Wade. For thirty years, the abortion industry has refined and perfected this message. Advocates like Planned Parenthood's president, Gloria Feldt, proclaim (with no apparent irony): "It's been 30 years since women were guaranteed the basic human right to make their own childbearing choices – a right as intrinsic as the right to breathe and to walk, to work and to think, to speak our truths, to thrive, to learn, and to love."
Roe has also become a lodestar for abortion advocates and the politicians who support their agenda. Any event or policy affecting a child before or near birth is minutely scrutinized for its potential to "undermine Roe v. Wade." Anything (and anyone) that threatens the shaky "constitutionality" of Roe must be stopped. For example, state laws which punish violent attacks on unborn children and their mothers are denounced as schemes "designed to chip away at the constitutional rights of women." Even expanding eligibility under the State Children's Health Insurance Program to provide prenatal care to children from conception onward is attacked as "a guerilla attack on abortion rights."2
Allegiance to Roe has become the sine qua non for presidential aspirants of one political party and a litmus test used by many politicians in evaluating judicial nominees. Senate filibusters are being used to block confirmation votes on nominees. Individuals who have received the American Bar Association's highest recommendation based on their knowledge of law, their integrity and judicial temperament are blocked chiefly because abortion lobbyists suspect they are not sufficiently deferential to Roe v. Wade.
Already two presidential candidates seeking election in 2004 have announced that, if elected, they would appoint no one to the Supreme Court "if they don't commit to supporting Roe v. Wade and a woman's right to choose." This, too, is an unprecedented admission. They strain to explain why their position does not constitute a single issue "litmus test" for judicial appointees: "The focus is on the constitutional right that Roe established in America," says one. "I want jurists to agree, to swear to uphold the Constitution." Are abortion and the Constitution really synonymous?
Many Americans, including members of Congress, believe or act as if Roe v. Wade and the U.S. Constitution have equal authority. They are wrong, both as to Roe's place in American constitutional law and as to the duty of citizens and judges to follow it unquestioningly. Few decisions in the history of the Supreme Court have cried out so loudly for reversal, on both moral and legal grounds. And rarely has any decision been so fraught with conspicuous errors of law, fact and reasoning as the majority opinion in Roe.
This article is addressed to all who may think that Roe deserves a measure of deference as a landmark of constitutional law (notwithstanding its immoral outcome). Not so! Legally speaking, Roe is an abomination, and an embarrassment to lawyers and public officials who feel compelled to defend it.
Who Says So?
Among the legal scholars who have roundly criticized the Court's ruling in Roe as not being grounded in the U.S. Constitution are the following:
Six justices of the U.S. Supreme Court, unfortunately not simultaneously seated – White, Rehnquist, Scalia, Thomas, Kennedy3 and O'Connor4;
Virtually every recognized constitutional scholar who has published a book or article on Roe – including many, like Harvard's Laurence Tribe, who support Roe's outcome on other grounds (although he's switched grounds over the years).5 Yale Law School professor John Hart Ely spoke for many when he stated: Roe v. Wade "is bad because it is bad constitutional law, or rather because it is not constitutional law and gives almost no sense of an obligation to try to be";6 and
Edward Lazarus, a former law clerk to Roe's author, Justice Harry Blackmun, who writes:
As a matter of constitutional interpretation and judicial method, Roe borders on the indefensible. I say this as someone utterly committed to the right to choose, as someone who believes such a right has grounding elsewhere in the Constitution instead of where Roe placed it, and as someone who loved Roe's author like a grandfather. . . . .
What, exactly, is the problem with Roe? The problem, I believe, is that it has little connection to the Constitutional right it purportedly interpreted. A constitutional right to privacy broad enough to include abortion has no meaningful foundation in constitutional text, history, or precedent. ...
The proof of Roe's failings comes not from the writings of those unsympathetic to women's rights, but from the decision itself and the friends who have tried to sustain it. Justice Blackmun's opinion provides essentially no reasoning in support of its holding. And in the almost 30 years since Roe's announcement, no one has produced a convincing defense of Roe on its own terms.7
Ten Legal Reasons to Condemn Roe
1.    The Court's decision in Roe v. Wade exceeded its constitutional authority.
Under the legal system established by the U.S. Constitution, the power to make laws is vested in Congress and retained by state legislatures. It is not the role of the Supreme Court to substitute the policy preferences of its members for those expressed in laws enacted by the people's elected representatives. The role of the judiciary in constitutional review is to determine if the law being challenged infringes on a constitutionally protected right.
Justice O'Connor reiterates this principle, quoting Chief Justice Warren Burger:
Irrespective of what we may believe is wise or prudent policy in this difficult area, "the Constitution does not constitute us as 'Platonic Guardians' nor does it vest in this Court the authority to strike down laws because they do not meet our standards of desirable social policy, 'wisdom,' or 'common sense.'"8
In Roe v. Wade and its companion case, Doe v. Bolton, however, the Court struck down criminal laws of Texas and Georgia which outlawed certain abortions by finding that these laws (and those of the other 48 states) violated a "right of privacy" that "is broad enough to encompass a woman's decision whether or not to terminate her pregnancy." Such a right is nowhere mentioned in the Constitution nor derivable from values embodied therein.
In his dissenting opinion in Doe v. Bolton, Justice Byron White, joined by Justice William Rehnquist, wrote:
I find nothing in the language or history of the Constitution to support the Court's judgment. The Court simply fashions and announces a new constitutional right for pregnant mothers ... and, with scarcely any reason or authority for its action, invests that right with sufficient substance to override most existing state abortion statutes. The upshot is that the people and the legislatures of the 50 states are constitutionally disentitled to weigh the relative importance of the continued existence and development of the fetus, on the one hand, against a spectrum of possible impacts on the mother, on the other hand. As an exercise of raw judicial power, the Court perhaps has authority to do what it does today; but, in my view, its judgment is an improvident and extravagant exercise of the power of judicial review that the Constitution extends to this Court.
2. The Court misrepresents the history of abortion practice and attitudes toward abortion.
The apparent purpose of the Roe opinion's long historical excursion is to create the impression that abortion had been widely practiced and unpunished until the appearance of restrictive laws in the prudishly Victorian 19th century. One example is adequate to show how distorted is Justice Harry Blackmun's rendition of history. He must overcome a huge hurdle in the person of Hippocrates, the "Father of Medicine," and his famous Oath which has guided medical ethics for over 2,000 years. The Oath provides in part: "I will give no deadly medicine to anyone if asked, nor suggest any such counsel; and in like manner I will not give to a woman a pessary to produce abortion."9 This enduring standard was followed until the Roe era and is reflected in Declarations of the World Medical Association through 1968: "I will maintain the utmost respect for human life, from the time of conception. ..."10 But Justice Blackmun dismisses this universal, unbroken ethical tradition as nothing more than the manifesto of a fringe Greek sect, the Pythagoreans, to which Hippocrates is alleged to have belonged!
    """
    
    try:
        biased_quotes = rank_biased_quotes(sample_text, n=10)
        print("Top biased quotes:")
        for i, quote in enumerate(biased_quotes, 1):
            print(f"{i}. {quote}")
    except Exception as e:
        print(f"Error: {e}")