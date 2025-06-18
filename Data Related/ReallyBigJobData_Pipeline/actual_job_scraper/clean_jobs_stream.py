from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StringType
from bs4 import BeautifulSoup
import re

# === Spark session ===
spark = SparkSession.builder \
    .appName("CleanJobPostings") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# === Kafka Config ===
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "raw_jobs") \
    .option("startingOffsets", "earliest") \
    .load()

# === Schema for Kafka message ===
schema = StructType() \
    .add("url", StringType()) \
    .add("html", StringType())

json_df = raw_df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# === UDF: Extract job fields ===
def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ").lower()

    # Basic heuristics
    if "hiring" not in text and "job" not in text:
        return None

    title = None
    location = None
    company = None

    # Try to extract with regex or HTML tags
    title_match = re.search(r'(?i)position[:\-]?\s*(.+)', text)
    if title_match:
        title = title_match.group(1)[:100]

    return {
        "title": title,
        "description": text[:2000],  # truncate
    }

parse_html_udf = udf(parse_html, StructType()
    .add("title", StringType())
    .add("description", StringType())
)

cleaned_df = json_df \
    .dropDuplicates(["url"]) \
    .withColumn("parsed", parse_html_udf(col("html"))) \
    .select("url", "parsed.title", "parsed.description") \
    .where(col("title").isNotNull())

# === Output to Parquet ===
query = cleaned_df.writeStream \
    .format("parquet") \
    .option("checkpointLocation", "/tmp/checkpoints/clean_jobs") \
    .option("path", "/data/parquet/clean_jobs/") \
    .outputMode("append") \
    .start()

query.awaitTermination()