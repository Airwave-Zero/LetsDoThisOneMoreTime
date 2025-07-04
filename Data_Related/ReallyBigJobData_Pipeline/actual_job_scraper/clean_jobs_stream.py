from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StringType
from bs4 import BeautifulSoup
import re

# === Spark session ===
spark = SparkSession.builder.appName("CleanJobPostings").getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# === Kafka Config ===
raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "raw_jobs")
    .option("startingOffsets", "earliest")
    .load()
)
# === Schema for Kafka message ===
schema = StructType().add("url", StringType()).add("html", StringType())

value_df = raw_df.selectExpr("CAST(value AS STRING) as json")
json_struct_df = value_df.select(from_json(col("json"), schema).alias("data"))
json_df = json_struct_df.select("data.*")


# === UDF: Extract job fields ===
def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ").lower()

    # Look for words that are very likely to be in a page with job posting
    if "apply" not in text and "description" not in text and "experience" not in text and "qualification" not in text:
        return None

    title = None
    location = None
    company = None
    '''
    TODO: look for things like
    job title: job title: , job__title
    location: remote, hybrid, on-site job__location
    company = 'about ___', '___ is an equal opportunity'
    '''

    # Try to extract with regex or HTML tags
    title_match = re.search(r'(?i)position[:\-]?\s*(.+)', text)
    if title_match:
        title = title_match.group(1)[:100]

    location_match = re.search(r'(?i)location[:\-]?\s*(.+)', text)
    if location_match:
        location = location_match.group(1)[:100]

    return {
        "company": company,
        "title": title,
        "location": location,
        "description": text,  # give me the whole job page, will parse/grab most commons later
    }

parse_html_udf = udf(parse_html, StructType().add("title", StringType()).add("description", StringType()))

# Drop duplicates
deduplicated_df = json_df.dropDuplicates(["url"])

# Apply UDF to extract fields
parsed_df = deduplicated_df.withColumn("parsed", parse_html_udf(col("html")))

# Select the relevant fields
cleaned_df = parsed_df.select("url", "parsed.title", "parsed.description")

# Filter out records with no title
filtered_df = cleaned_df.where(col("title").isNotNull())

# === Output to Parquet ===
query = (
    filtered_df.writeStream
    .format("parquet")
    .option("checkpointLocation", "/tmp/checkpoints/clean_jobs")
    .option("path", "/data/parquet/clean_jobs/")
    .outputMode("append")
    .start()
)

query.awaitTermination()
