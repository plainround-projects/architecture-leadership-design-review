# Design review: uploads service, security lens

Date: 2026-10-22
Reviewers: Security engineer
Author: Uploads team lead
Requirements file: docs/requirements/uploads-security.md

## Requirements used (with the way to check each one)
| ID | Requirement | Target | How to verify |
| --- | --- | --- | --- |
| S1 | Unauthenticated uploads accepted | 0 | integration test with no session |
| S2 | Uploads scanned and type-checked before READY | 100 percent, 3 allowed types (JPEG, PNG, WebP) | upload test with 10 disguised files |
| S3 | Random bits in an object key | at least 120 bits | key generation unit test |
| S4 | Public original photos | 0 objects | bucket policy check |
| S5 | Published thumbnails that keep location data | 0 | sample of 100 thumbnails |

## Assessment
| ID | Verdict | Reason |
| --- | --- | --- |
| S1 | might not | The draft says the service accepts the file over HTTPS and never says who may upload. |
| S2 | doesn't | The only limit is 25 MB; 0 of the 3 allowed types are checked, so a script renamed to .jpg is stored and served. |
| S3 | meets | The author's key is a version 4 UUID: 128 bits - 6 fixed bits = 122 random bits, above the 120 asked for. |
| S4 | doesn't | The CDN reads from the same object storage as the originals, and the draft names no policy that keeps the originals private. |
| S5 | might not | Thumbnails are produced by a job the draft does not describe, so whether it strips location data from photos is unknown. |

## Findings
| # | Finding | Requirement | Class |
| --- | --- | --- | --- |
| 1 | The draft does not say who may upload | S1 | must-fix |
| 2 | Only the size is limited; the type and content are not checked or scanned | S2 | must-fix |
| 3 | The object key scheme is not stated | S3 | withdrawn |
| 4 | The CDN and the originals share storage, with no stated policy | S4 | must-fix |
| 5 | The thumbnail job may keep location data | S5 | should-fix |
| 6 | A preference for direct-to-storage uploads with signed URLs | none | taste, dropped |

## Decisions
- Uploads will require a seller session, and the endpoint will refuse anything else with a 401.
- The service will check each file's type by its content and scan it before the row becomes READY.
- The originals will live in a private bucket, and only the thumbnails bucket will be readable by the CDN.

## Accepted risks
| Risk | Owner | Look again |
| --- | --- | --- |
| S5: location data may remain in thumbnails until the job is reviewed | Security engineer | 2026-11-12 |

## Action items
| Action | Owner | Date |
| --- | --- | --- |
| Add the bucket policy check and an integration test with no session | Uploads team lead | 2026-11-05 |
| Review the thumbnail job for location data and strip it | Uploads team lead | 2026-11-12 |

## Disagreement
Finding: 3
Author: Keys are version 4 UUIDs made on the server, which is 122 random bits.
Outcome: accepted. 122 bits is above the 120 the requirement asks for, so the key scheme meets S3. I changed my position on finding 3.
