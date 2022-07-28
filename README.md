# aws-cf

## Current State Architecture

![Architecture for current state, using cloudtrail & eventbridge](/images/aws-cf-current-state-machine.png)




## Future State Architecture
POC, using SQS as failover. 

We anticipate common errors from the second input source:
- Not being available 
- Not being up-to-date 
- Being up-to-date, but **incomplete** compared to historical expectations

Publishing to SNS and alerting an engineer/analyst will require they manually intervene, instead we can skip that and automate the response. The obvious response is check back in at a later time and re-run the state-machine.

Reference [this link](https://catalog.us-east-1.prod.workshops.aws/workshops/44c91c21-a6a4-4b56-bd95-56bd443aa449/en-US/lab-guide/lambda) for lambda querying athena pattern.

![Architecture for future state using SQS as failover](/images/aws-cf-state-machine-future-state.jpg)