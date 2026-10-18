# Private Seller Discovery Sources

The adapter contains candidate source definitions for platforms that advertise private-owner or direct-to-seller listings. A platform's marketing and a permissive robots.txt file do **not** establish permission for automated commercial collection.

Defined source candidates:
- Keyzee
- FYSH
- OffAgent
- Hauski
- OwnerBridge
- FMDirect
- Bybricks
- OpenMoov

Fail-closed access controls:
- No private-seller source is fetched unless its exact name is included in the operator-reviewed `ATLAS_APPROVED_PRIVATE_SELLER_SOURCES` comma-separated allowlist.
- Before allowlisting a source, the operator must check its current terms, data/API licence, commercial-use conditions, and any applicable privacy obligations; obtain written permission where required.
- Public pages only; robots.txt is checked before each request and inaccessible robots.txt fails closed.
- No login, anti-bot bypass, or access-control circumvention.
- No collection of private phone/email details and no automated contact.
- New candidates enter the pipeline with Contact Permission = Unknown and remain subject to evidence and human review.
- Source URL and listing-level evidence are retained for human verification.

Open-market listings:
- The optional `open-properties` adapter currently names Rightmove as its provider.
- Rightmove's published terms prohibit automated access/collection without prior written permission. The adapter therefore requires both `ATLAS_OPEN_PROPERTIES_ENABLED=true` and `ATLAS_RIGHTMOVE_WRITTEN_PERMISSION=true`; do not set the permission flag unless that permission has actually been obtained and is still valid.
- The unit tests use mocked provider responses only and do not access listing pages.

No source should be enabled merely because it is publicly viewable. The allowlist is an operator control, not a legal determination.
