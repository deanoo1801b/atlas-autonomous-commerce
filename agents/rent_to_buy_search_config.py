"""Expanded London and commuter-belt Rent to Buy search configuration.

London searches include London Living Rent and intermediate-rent terminology,
which is often the local route toward ownership. Surrounding search coverage
includes the main commuter counties and towns around Greater London.
"""

LONDON_BOROUGHS = [
    "Barking and Dagenham", "Barnet", "Bexley", "Brent", "Bromley",
    "Camden", "Croydon", "Ealing", "Enfield", "Greenwich", "Hackney",
    "Hammersmith and Fulham", "Haringey", "Harrow", "Havering",
    "Hillingdon", "Hounslow", "Islington", "Kensington and Chelsea",
    "Kingston upon Thames", "Lambeth", "Lewisham", "Merton", "Newham",
    "Redbridge", "Richmond upon Thames", "Southwark", "Sutton", "Tower Hamlets",
    "Waltham Forest", "Wandsworth", "Westminster", "City of London",
]

SURROUNDING_AREAS = [
    # Essex
    "Basildon", "Brentwood", "Chelmsford", "Grays", "Harlow", "Romford",
    "Southend-on-Sea", "Thurrock",
    # Kent
    "Dartford", "Gravesend", "Maidstone", "Sevenoaks", "Swanley", "Tonbridge",
    "Tunbridge Wells",
    # Surrey
    "Epsom", "Guildford", "Redhill", "Reigate", "Staines-upon-Thames", "Woking",
    # Hertfordshire
    "Borehamwood", "Hatfield", "Hemel Hempstead", "Hertford", "St Albans",
    "Stevenage", "Watford",
    # Berkshire
    "Bracknell", "Maidenhead", "Reading", "Slough", "Windsor",
    # Buckinghamshire and Bedfordshire
    "Aylesbury", "High Wycombe", "Luton", "Milton Keynes",
]

RTB_SEARCH_PHRASES = (
    '"Rent to Buy"',
    '"rent-to-buy"',
    '"rent then buy"',
    '"intermediate rent"',
    '"London Living Rent"',
)

def build_rent_to_buy_queries():
    """Build geographically broad scheme queries, with and without bedroom terms."""
    areas = ["London"] + LONDON_BOROUGHS + SURROUNDING_AREAS
    phrase_group = " OR ".join(RTB_SEARCH_PHRASES)
    bedroom_group = '("2 bedroom" OR "3 bedroom" OR "2-bed" OR "3-bed" OR house)'
    queries = []
    for area in areas:
        # The first catches property ads; the second catches provider/development pages
        # that omit bedroom counts from the search snippet.
        queries.append(f'({phrase_group}) "{area}" {bedroom_group}')
        queries.append(f'({phrase_group}) "{area}" housing provider development')
    return queries
