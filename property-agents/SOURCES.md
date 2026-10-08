# Private Seller Discovery Sources

The discovery layer currently targets public listing/index pages from platforms that explicitly advertise private-owner or direct-to-seller listings.

Current sources:
- Bybricks
- Keyzee
- FYSH
- OffAgent
- OpenMoov
- Hauski
- Roof Over Your Head

Current controls:
- Public pages only
- robots.txt checked before each request
- No login or access-control bypass
- No collection of private phone/email details
- No automated contact
- New candidates enter the pipeline with Contact Permission = Unknown and Compliance = Amber
- Source URL and evidence are retained for human verification

The source list is deliberately separate from the scoring engine so sources can be added/removed without changing compliance logic.
