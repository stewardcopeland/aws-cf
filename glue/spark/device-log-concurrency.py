# Part II ----------------------------------------------------------------------    
#import boto3
from pyspark.sql.functions import col
from pyspark.sql.functions import *
from pyspark.sql import Window
import datetime
from datetime import timedelta as dtDelta
from dateutil import tz
import time
import sys
import logging
from pyspark.context import SparkContext
from dateutil.relativedelta import *
import json
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import argparse
# To Do: map args
parser = argparse.ArgumentParser()

parser.add_argument('--load_type', help='must be any one of the list', choices=[
                    'DAILY_LOAD', 'DATE_RANGE', 'FULL_LOAD'], type=str, default='DAILY_LOAD', required=True)

parser.add_argument('--execution_date', help='data will cover the last calendar week preceding execution date',
                    default=datetime.date.today(), required=False)
parser.add_argument(
    '--start_date', help='start date for the load date range', required=False)

parser.add_argument(
    '--end_date', help='end date for the loading date range', required=False)

# Fix HELP
parser.add_argument(
    '--cleansed_bucket', help='input bucket name to read the data', required=True)

parser.add_argument(
    '--cleansed_prefix', help='input prefix name to read the data', required=True)

parser.add_argument(
    '--processed_bucket', help='output bucket name to write the data', required=True)

parser.add_argument(
    '--processed_prefix', help='output prefix name to write the data', required=True)

parser.add_argument(
    '--JOB_ID', help='Aws glue job id', required=False)

parser.add_argument(
    '--JOB_RUN_ID', help='Aws glue job run id', required=False)

args, unknown = parser.parse_known_args() # https://docs.python.org/3/library/argparse.html#partial-parsing

load_type = args.load_type

cleansed_bucket = args.cleansed_bucket
cleansed_prefix = args.cleansed_prefix
processed_bucket = args.processed_bucket
processed_prefix = args.processed_prefix

cleansed_path = 's3a://{0}/{1}'.format(cleansed_bucket, cleansed_prefix)
processed_path = 's3a://{0}/{1}'.format(processed_bucket, processed_prefix)

execution_date = args.execution_date
start_date = args.start_date
end_date = args.end_date

if load_type == 'DAILY_LOAD' :
    # To do, get from args.start_date / end_date 
    # start_date = '2022-01-02'     #info['start_date']
    start_date = execution_date  - dtDelta(days= 7) - dtDelta(days=execution_date.isoweekday() % 7)
    # end_date = '2022-01-08'   #  info['end_date']
    end_date = execution_date  - dtDelta(days=execution_date.isoweekday() % 7) - dtDelta(days= 1)
    
sc = SparkContext.getOrCreate()
spark = SparkSession(sc)
start = time.time()
# ...
end = time.time()
print(end - start)
