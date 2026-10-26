# Design checklist: apply before asking for a review

Built from the findings the two reviews of the uploads proposal raised. An author who answers these before the review removes the findings that cost the most time.

- [ ] CHK-01 [throughput] Did you compute the peak rate from the facts you have, and show that every stage can carry it?
- [ ] CHK-02 [latency] Is there a latency number for the slowest realistic request, and a way to measure it?
- [ ] CHK-03 [freshness] Is every background stage sized for the peak and not only the average, and is there a metric for how old its oldest item is?
- [ ] CHK-04 [freshness] What happens to a background job that fails, and who sees it?
- [ ] CHK-05 [availability] Which components are single points of failure, and what happens when each one fails?
- [ ] CHK-06 [durability] Does the design say which write happens first, and what a crash between two writes leaves behind?
- [ ] CHK-07 [cost] Is there a monthly estimate, and is it under the ceiling?
