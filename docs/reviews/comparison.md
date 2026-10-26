# The same proposal, two lenses

[The architecture review](review-2026-10-22-uploads-service.md) asked "will it carry the load, and can it be lost?". [The security review](review-2026-10-22-uploads-service-security.md) asked "who can reach it, and what can an attacker make it do?". Both reviews used the same method: numbers first, every finding tied to one, and a preference dropped on purpose.

| | Architecture lens | Security lens |
| --- | --- | --- |
| First question | How many photos a second, and does every stage keep up? | Who is allowed to upload, and what is a file allowed to be? |
| Where the requirements came from | The facts in the proposal (listings, photos, the weekend). | The proposal's silences (who, what type, which bucket). |
| Must-fix findings | 2 (one worker; the order of writes) | 3 (no authentication stated; no content check; shared storage) |
| What the draft got right | A CDN in front of thumbnails; two instances. | Server-made UUID keys. |
| Where the author won | One retry for failed thumbnails (finding 4). | The key scheme (finding 3). |
| Taste dropped | Another CDN; a table name. | Signed URLs for direct upload. |

What they share: both found the draft silent where it mattered, both found the answer in a number (0.5 photos a second; 3 allowed types), and both let the author win one finding on the evidence. What only the security lens found: nothing in the architecture review could have caught that a file called photo.jpg may be a script, because no throughput or availability number is about content. That is the reason to review a design more than once, each time with the requirements the other lens does not have.
