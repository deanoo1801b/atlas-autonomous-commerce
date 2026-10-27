"""Pure query classification helpers for the property research scanner."""

RENT_TO_BUY_PHRASES = (
    '"rent to buy"',
    '"rent-to-buy"',
    '"rent then buy"',
    '"intermediate rent"',
)


def is_rent_to_buy_query(query: str) -> bool:
    """Return whether a search query explicitly targets Rent to Buy housing."""
    query_lower = query.lower()
    return any(phrase in query_lower for phrase in RENT_TO_BUY_PHRASES)
