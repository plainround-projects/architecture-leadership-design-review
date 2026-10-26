# Requirements: photo uploads service, security lens

Date: 2026-10-22
Categories: access, content, keys, exposure, privacy

## Requirements
| ID | Category | Requirement | Target | How to verify |
| --- | --- | --- | --- | --- |
| S1 | access | Unauthenticated uploads accepted | 0 | integration test with no session |
| S2 | content | Uploads scanned and type-checked before READY | 100 percent, 3 allowed types (JPEG, PNG, WebP) | upload test with 10 disguised files |
| S3 | keys | Random bits in an object key | at least 120 bits | key generation unit test |
| S4 | exposure | Public original photos | 0 objects | bucket policy check |
| S5 | privacy | Published thumbnails that keep location data | 0 | sample of 100 thumbnails |
