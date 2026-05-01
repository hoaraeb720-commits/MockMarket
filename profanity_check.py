from transformers import pipeline
import wordninja
from loguru import logger
import streamlit as st

@st.cache_resource
def load_toxicity_model():
    return pipeline("text-classification", model="unitary/toxic-bert")

@st.cache_resource
def load_nsfw_model():
    return pipeline("text-classification", model="michellejieli/NSFW_text_classifier")

toxicity = load_toxicity_model()
nsfw = load_nsfw_model()

def check_username(username: str) -> dict:
    logger.info(f"Checking username: {username}")
    words = wordninja.split(username.lower())
    readable = " ".join(words)

    tox = toxicity(readable)[0]
    nsfw_result = nsfw(readable)[0]
    logger.info(f"Toxicity result: {tox}")
    logger.info(f"NSFW result: {nsfw_result}")

    flagged = (tox["label"] == "toxic" and tox["score"] > 0.6) or (
        nsfw_result["label"] == "NSFW" and nsfw_result["score"] > 0.9
    )

    return {
        "original": username,
        "parsed_as": readable,
        "flagged": flagged,
    }
