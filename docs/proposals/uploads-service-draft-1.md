# Proposal: photo uploads service for a marketplace (draft 1)

Author: Uploads team lead
Date: 2026-10-20

## Overview
Sellers upload up to 10 photos per listing. A new `uploads` service accepts the file over HTTPS, stores it in object storage, writes a row in a PostgreSQL table, and returns the URL. A background job creates three thumbnail sizes and sets the row's status to READY. Files are limited to 25 MB. The setting is 120,000 listings a week, most of them created between Friday evening and Sunday night. We expect "a lot of uploads on weekends". The company wants an availability target for the seller flow and has set a cost ceiling for the service.

## Data flow
```text
 seller app --HTTPS--> uploads service (x2) --> object storage
                              |                      ^
                              v                      |
                         PostgreSQL <-- thumbnail job (1 worker)
 listings page --> CDN --> object storage (thumbnails)
```

## Datastore
Photos and thumbnails live in object storage. One PostgreSQL table, `uploads`, holds `id`, `listing_id`, `object_key` and `status` for every photo. The listings page reads the thumbnails through a CDN.

## External calls
The service calls object storage to write each photo and PostgreSQL to write its row. The thumbnail job reads the original from object storage and writes three sizes back. The CDN, which the listings page uses, reads from object storage.

## Scaling
The service runs as 2 instances behind a load balancer. The thumbnail job runs with 1 worker.

## Failure handling
If thumbnailing fails, the job tries again once. A photo whose thumbnails never appear stays in its original status.

## Unsure
- One thumbnail worker may not be enough, and nothing here says how it would grow.
- "A lot of uploads on weekends" has no number and no way to check it.
- The proposal does not say which is written first, the file or the row.
