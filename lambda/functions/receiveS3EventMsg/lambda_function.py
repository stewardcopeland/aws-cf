import boto3
import json
import logging
import os
from pathlib import Path
import requests
from datetime import datetime

client = boto3.client('stepfunctions')

def lambda_handler(event, context):
    inputDict = event.get('SF_INPUT', json.loads(os.environ['SF_INPUT'])) # Use event param, default to env_var
    sfTarget = event.get('SF_ARN', os.environ['SF_ARN'])
    msgBody  = event # if these were received from SQS use this -> event['Records'][0]['body']
    print('printing msgBody... ', msgBody)
    objKey = msgBody['detail']['requestParameters']['key'] # Get date from event, strip out from s3 object key format of 'vehicles/vin/w/20220522/vehicles_vin_w_20220522.csv'
    execDateDict = {'execution_date' : datetime.strptime( objKey.split('/')[3] , '%Y%m%d').strftime('%Y-%m-%d') } # get 4th element for key prefix
    print('printing object type... ' , type(execDateDict))
    print('printing execution_date dictionary keys... ', execDateDict.keys())

    inputDict.update(execDateDict) # Concat event.date to env_var inputs
    print('printing input dictionary keys... ',inputDict.keys())
    
    response = client.start_execution( #Call start StepFuction
        stateMachineArn = sfTarget
        , input = json.dumps(inputDict)
        # # # SF_INPUT should include : # additional-python-modules: 'Shapely==1.8.0' # conf: 'spark.sql.sources.partitionOverwriteMode=dynamic' # ingress_bucket # ingress_prefix # cleansed_bucket # cleansed_prefix
    )
    return(response)