"""Pure query classification helpers for the property research scanner."""

RENT_TO_BUY_PHRASES = (
    '"rent to buy"',
    '"rent-to-buy"',
    '"rent then buy"',
    '"intermediate rent"',
    '"london living rent"',
)


def is_rent_to_buy_query(query: str) -> bool:
    """Return whether a search query explicitly targets Rent to Buy housing."""
    query_lower = query.lower()
    return any(phrase in query_lower for phrase in RENT_TO_BUY_PHRASES)


def is_london_living_rent_signal(text: str) -> bool:
    """Identify a result explicitly mentioning London Living Rent."""
    return "london living rent" in (text or "").lower()
