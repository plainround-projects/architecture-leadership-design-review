# Design review: uploads service

Date: 2026-10-22
Reviewers: Platform architect
Author: Uploads team lead
Requirements file: docs/requirements/uploads-nfrs.md

## Requirements used (with the way to check each one)
| ID | Requirement | Target | How to verify |
| --- | --- | --- | --- |
| R1 | Peak throughput | 40 uploads a second | load test |
| R2 | Upload p99 latency | under 3 seconds for a 5 MB photo | load test, then dashboard |
| R3 | Thumbnails ready | 95 percent within 30 seconds of upload | queue age metric |
| R4 | Availability of the upload API | 99.9 percent a month (about 43 minutes of downtime) | uptime check |
| R5 | Accepted uploads lost | 0 accepted uploads lost | storage replication setting, restore test |
| R6 | Cost ceiling | 2,000 dollars a month | cloud bill |

## Assessment
| ID | Verdict | Reason |
| --- | --- | --- |
| R1 | might not | 840,000 photos in 216,000 s = 3.9 a second on average and about 40 at the peak; the draft gives no capacity for its 2 instances. |
| R2 | might not | The draft has no latency budget; a 5 MB photo through 2 instances with storage and a database write has never been timed. |
| R3 | doesn't | 1 worker / 2 s per photo = 0.5 photos a second, against 3.9 on average and 40 at the peak, so the queue grows for hours. |
| R4 | might not | 2 instances help, but the thumbnail worker and the database are single points, and the draft does not say what happens when they fail. |
| R5 | might not | The response goes out when the file is in storage, and the draft does not say whether the row exists by then. |
| R6 | meets | Nothing in the draft is expensive: 2 instances, a database, storage and a CDN. There is no estimate yet, so one is asked for. |

## Findings
| # | Finding | Requirement | Class |
| --- | --- | --- | --- |
| 1 | One thumbnail worker handles about 0.5 photos a second | R3 | must-fix |
| 2 | The order of writes is not stated, and a crash between the file and the row loses the link | R5 | must-fix |
| 3 | The database and the worker are single points of failure | R4 | should-fix |
| 4 | Only one retry for failed thumbnails | R3 | withdrawn |
| 5 | A preference for another CDN | none | taste, dropped |
| 6 | No capacity figure for the 2 upload instances | R1 | should-fix |
| 7 | No latency budget for a 5 MB photo | R2 | should-fix |
| 8 | A preference to rename the `uploads` table | none | taste, dropped |

## Decisions
- Thumbnail workers will autoscale on queue age, with a floor of 8 workers and a ceiling of 80.
- The service will write the row first with status PENDING, then store the file, then mark the row STORED, and only then answer the seller.
- The thumbnail job will keep one retry, and the listings page will show the original photo until its thumbnails exist.

## Accepted risks
| Risk | Owner | Look again |
| --- | --- | --- |
| R4: a single database and a single queue for now | Uploads team lead | 2026-12-01 |

## Action items
| Action | Owner | Date |
| --- | --- | --- |
| Add the queue-age metric and an alert at 15 seconds | Uploads team lead | 2026-10-29 |
| Run a 40 uploads a second load test, with and without the autoscaler | Platform architect | 2026-11-05 |
| Write a latency budget for a 5 MB photo and a monthly cost estimate | Uploads team lead | 2026-11-05 |

## Disagreement
Finding: 4
Author: Failed thumbnails are under 0.1 percent and the original is shown meanwhile, so one retry is enough.
Outcome: accepted. The requirement is 95 percent within 30 seconds, which a failure rate under 0.1 percent still meets. I changed my position on finding 4.
