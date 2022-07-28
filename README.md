# aws-cf

## Current State Architecture




## Future State Architecture
Using SQS as failover. 

We anticipate common errors from the second input source:
- Not being available 
- Not being up-to-date 
- Being up-to-date, but **incomplete** compared to historical expectations

Publishing to SNS and alerting an engineer/analyst will require they manually intervene, instead we can skip that and automate the response. The obvious response is check back in at a later time and re-run the state-machine.

![Architecture for future state using SQS as failover](/images/aws-cf-state-machine-future-state.jpg)