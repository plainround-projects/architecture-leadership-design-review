# Requirements: photo uploads service

Date: 2026-10-22
Categories: throughput, latency, freshness, availability, durability, cost

## Requirements
| ID | Category | Requirement | Target | How to verify |
| --- | --- | --- | --- | --- |
| R1 | throughput | Peak throughput | 40 uploads a second | load test |
| R2 | latency | Upload p99 latency | under 3 seconds for a 5 MB photo | load test, then dashboard |
| R3 | freshness | Thumbnails ready | 95 percent within 30 seconds of upload | queue age metric |
| R4 | availability | Availability of the upload API | 99.9 percent a month (about 43 minutes of downtime) | uptime check |
| R5 | durability | Accepted uploads lost | 0 accepted uploads lost | storage replication setting, restore test |
| R6 | cost | Cost ceiling | 2,000 dollars a month | cloud bill |

## Where the load number comes from
120,000 listings a week with up to 10 photos each is up to 1.2 million photos a week. If 70 percent arrive in the 2.5 days from Friday evening to Sunday night (216,000 seconds), the average is 840,000 / 216,000 = 3.9 uploads a second. A peak of ten times the average is about 39, rounded up to the 40 of R1. `design-review fitness` computes the same numbers from `model/uploads.toml`.
