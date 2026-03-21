import structlog

logger = structlog.get_logger()

# Lazy-loaded spaCy model
_nlp = None


def get_nlp():
    """Load spaCy model lazily."""
    global _nlp
    if _nlp is None:
        import spacy

        try:
            _nlp = spacy.load("en_core_web_lg")
        except OSError:
            logger.warning("nlp.model.fallback", msg="en_core_web_lg not found, using en_core_web_sm")
            _nlp = spacy.load("en_core_web_sm")

        # Add custom entity patterns for Indian business
        ruler = _nlp.add_pipe("entity_ruler", before="ner")
        patterns = [
            # Regulators
            {"label": "ORG", "pattern": "RBI"},
            {"label": "ORG", "pattern": "SEBI"},
            {"label": "ORG", "pattern": "NCLT"},
            {"label": "ORG", "pattern": "NCLAT"},
            {"label": "ORG", "pattern": "BSE"},
            {"label": "ORG", "pattern": "NSE"},
            {"label": "ORG", "pattern": "IRDAI"},
            # Common Indian business entities
            {"label": "ORG", "pattern": [{"LOWER": "byju"}, {"TEXT": "'s"}]},
            {"label": "ORG", "pattern": "Adani Group"},
            {"label": "ORG", "pattern": "Hindenburg Research"},
            {"label": "ORG", "pattern": "Paytm"},
            {"label": "ORG", "pattern": [{"LOWER": "yes"}, {"LOWER": "bank"}]},
        ]
        ruler.add_patterns(patterns)

    return _nlp


def extract_entities(text: str) -> list[dict]:
    """Extract named entities from text."""
    nlp = get_nlp()
    doc = nlp(text)

    entities = []
    seen = set()
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PERSON", "GPE", "MONEY", "DATE") and ent.text not in seen:
            seen.add(ent.text)
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            })

    return entities
