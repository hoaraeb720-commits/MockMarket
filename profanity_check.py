from transformers import pipeline
import wordninja

toxicity = pipeline("text-classification", model="unitary/toxic-bert")
nsfw = pipeline("text-classification", model="michellejieli/NSFW_text_classifier")


def check_username(username: str) -> dict:
    words = wordninja.split(username.lower())
    readable = " ".join(words)

    tox = toxicity(readable)[0]
    nsfw_result = nsfw(readable)[0]

    flagged = (tox["label"] == "toxic" and tox["score"] > 0.6) or (
        nsfw_result["label"] == "NSFW" and nsfw_result["score"] > 0.6
    )

    return {
        "original": username,
        "parsed_as": readable,
        "flagged": flagged,
    }
