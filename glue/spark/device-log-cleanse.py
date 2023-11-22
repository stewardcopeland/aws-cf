
from pyspark.sql.window import Window
import pyspark.sql.functions as f
import time
import datetime
from datetime import timedelta as dtDelta
from pyspark.sql import SparkSession
from pyspark.sql.types import FloatType, DoubleType, StringType
from shapely import wkb
from pyspark.context import SparkContext
from pyspark.sql.session import SparkSession
import argparse
import logging

parser = argparse.ArgumentParser()

parser.add_argument('--load_type', help='must be any one of the list', choices=[
                    'DAILY_LOAD', 'DATE_RANGE', 'FULL_LOAD'], type=str, default='DAILY_LOAD', required=True)

parser.add_argument('--execution_date', help='data will cover the last calendar week preceding execution date',
                    default=  # To Do, remove this since we expect input to be string type # datetime.date.today()
                      datetime.datetime.now().strftime('%Y-%m-%d')
                    , required=False)
parser.add_argument(
    '--start_date', help='start date for the load date range', required=False)

parser.add_argument(
    '--end_date', help='end date for the loading date range', required=False)

parser.add_argument(
    '--ingress_bucket', help='input bucket name to read the parquet files', required=True)

parser.add_argument(
    '--ingress_prefix', help='input prefix name to read the parquet files', required=True)

parser.add_argument(
    '--cleansed_bucket', help='output bucket name to write the data', required=True)

parser.add_argument(
    '--cleansed_prefix', help='output prefix name to write the data', required=True)

parser.add_argument(
    '--JOB_ID', help='Aws glue job id', required=False)

parser.add_argument(
    '--JOB_RUN_ID', help='Aws glue job run id', required=False)

args, unknown = parser.parse_known_args() # https://docs.python.org/3/library/argparse.html#partial-parsing

load_type = args.load_type
ingress_bucket = args.ingress_bucket
ingress_prefix = args.ingress_prefix
cleansed_bucket = args.cleansed_bucket
cleansed_prefix = args.cleansed_prefix

ingress_path = 's3a://{0}/{1}'.format(ingress_bucket, ingress_prefix)
cleansed_path = 's3a://{0}/{1}'.format(cleansed_bucket, cleansed_prefix)

execution_date =  datetime.datetime.strptime(args.execution_date, '%Y-%m-%d')
start_date = args.start_date
end_date = args.end_date

if load_type == 'DAILY_LOAD' :
  # Get the SUNDAY of last week
  start_date = execution_date  - dtDelta(days= 7) - dtDelta(days=execution_date.isoweekday() % 7)
  # Get the SATURDAY of last week
  end_date = execution_date  - dtDelta(days=execution_date.isoweekday() % 7) - dtDelta(days= 1)


sc = SparkContext.getOrCreate()
spark = SparkSession(sc)
# spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic") # This is set in Glue in Action > Edit Job > Job Parameters (key = --conf, value = spark.sql.sources.partitionOverwriteMode=dynamic )

# To Do: use try/catch before running, check on any input files from s3://aap-dev-sc-order-mgmt-results/dl-lz
input_filepath = 's3://dl-lz/address/addresses_master.csv'
output_filepath = 's3://dl-cleansed/address/'
df = spark.read.csv(input_filepath,header=True,inferSchema=True)
df.write.mode('overwrite').parquet(output_filepath)

input_filepath = 's3://dl-lz/geo/geo.csv'
output_filepath = 's3://dl-cleansed/geo/'
df = spark.read.csv(input_filepath,header=True,inferSchema=True)
df.write.mode('overwrite').parquet(output_filepath)

input_filepath = 's3://vehicles/vin/master/vehicles_vin_master.csv'
output_filepath = 's3://dl-cleansed/vehicle-inventory/'
df = spark.read.csv(input_filepath,header=True,inferSchema=True)
df = df.withColumn('week_start',f.to_date('week_start', 'yyyy-MM-dd').alias('dt'))
df = df.withColumn('week_end',f.to_date('week_end', 'yyyy-MM-dd').alias('dt'))
cols = ['year','period','week']
df.repartition(*[f.col(c) for c in cols]).write.mode('overwrite').partitionBy(cols).parquet(output_filepath)

### device logs
output_filepath = cleansed_path 

start_dateTime = datetime.datetime.combine(
    date = start_date, time = datetime.datetime.min.time() ) 

end_dateTime = datetime.datetime.combine(
    date = end_date, time = datetime.datetime.min.time() ) 

# Define User Defined Function: Convert hex values to latitude/longitude
# wkb_udf = functions.udf(lambda p: wkb.loads(p, hex=True))
@f.udf(returnType=StringType())  
def wkb_udf(p):
  if p is not None:
    return wkb.loads(p, hex=True)
  else:
    return None

# wkb_udf_lat = functions.udf(lambda po: po.y)
@f.udf(returnType=StringType())  
def wkb_udf_lat(po):
  if po is not None:
    return po.y
  else:
    return None

# wkb_udf_long = functions.udf(lambda po: po.x)
@f.udf(returnType=StringType())  
def wkb_udf_long(po):
  if po is not None:
    return po.x
  else:
    return None

input_df = spark.read.parquet(ingress_path)
df = input_df.filter(f.col("timestamp").between(start_dateTime,end_dateTime))

# Create date col for partitioning
df = df.withColumn('utc_date', f.to_date('timestamp', 'yyyy-MM-dd'))

# Window fct to remove duplicates of modified_datetime 
w = Window().partitionBy("id").orderBy(f.col("last_modified_date").desc())

df.withColumn("rn", f.row_number().over(w)).where(f.col("rn") == 1)

# Implement hex to lat/long conversion in new columns
df = df.withColumn('lat', wkb_udf_lat(wkb_udf('point')))
df = df.withColumn('lon', wkb_udf_long(wkb_udf('point')))

### Repartition and write to cleansed bucket
cols = ['utc_date']
df.repartition(*[f.col(c) for c in cols]).write.mode('overwrite').partitionBy(cols).parquet(output_filepath)

    
