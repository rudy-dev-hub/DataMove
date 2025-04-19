from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import *

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Data Transformation") \
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Read source data
source_df = spark.read.format("delta").load("/mnt/data/source")

# Apply transformations
transformed_df = source_df \
    .withColumn("processed_date", current_timestamp()) \
    .withColumn("year", year("date")) \
    .withColumn("month", month("date")) \
    .withColumn("day", dayofmonth("date")) \
    .dropDuplicates() \
    .orderBy("date")

# Write to Delta Lake
transformed_df.write \
    .format("delta") \
    .mode("overwrite") \
    .partitionBy("year", "month", "day") \
    .save("/mnt/data/transformed")

# Optimize table
spark.sql("""
    OPTIMIZE '/mnt/data/transformed'
    ZORDER BY (date)
""")

# Clean up old files
spark.sql("""
    VACUUM '/mnt/data/transformed'
    RETAIN 168 HOURS
""") 