# spark/stream_user_events.py
import os, json, requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr
from pyspark.sql.types import StructType, StructField, StringType, LongType

# ---------- Config ----------
BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC      = os.environ.get("KAFKA_TOPIC", "user-events")         # your producer topic
FORMAT     = os.environ.get("EVENT_FORMAT", "avro")               # "json" or "avro"
SCHEMA_REG = os.environ.get("SCHEMA_REGISTRY_URL", "http://localhost:8081")
SUBJECT    = os.environ.get("SCHEMA_SUBJECT", "user-events-value")

S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "http://localhost:9000")
S3_KEY      = os.environ.get("S3_ACCESS_KEY", "minioadmin")
S3_SECRET   = os.environ.get("S3_SECRET_KEY", "minioadmin")
S3_BUCKET   = os.environ.get("S3_BUCKET", "data-lake")
S3_PREFIX   = os.environ.get("S3_PREFIX", "user-events")
OUT_PATH    = f"s3a://{S3_BUCKET}/{S3_PREFIX}/"
CHECKPOINT  = os.environ.get("CHECKPOINT", "/tmp/spark-checkpoints/user-events")

# ---------- Spark ----------
spark = (SparkSession.builder
         .appName("DWAI-003-UserEvents-Stream")
         .getOrCreate())

# MinIO/S3A config
hconf = spark._jsc.hadoopConfiguration()
hconf.set("fs.s3a.endpoint", S3_ENDPOINT)
hconf.set("fs.s3a.access.key", S3_KEY)
hconf.set("fs.s3a.secret.key", S3_SECRET)
hconf.set("fs.s3a.path.style.access", "true")
hconf.set("fs.s3a.impl.disable.cache", "true")

# Read from Kafka (value is bytes)
raw = (spark.readStream
       .format("kafka")
       .option("kafka.bootstrap.servers", BOOTSTRAP)
       .option("subscribe", TOPIC)
       .option("startingOffsets", "earliest")
       .load())

# Common projection of Kafka columns you may want:
# key, value, headers, timestamp, partition, offset
base = raw.selectExpr(
    "CAST(key AS STRING) AS k",
    "value",
    "timestamp",
    "partition",
    "offset"
)

# Decide parsing path
if FORMAT.lower() == "json":
    # Define expected JSON schema
    schema = StructType([
        StructField("id",        LongType(),   True),
        StructField("name",      StringType(), True),
        StructField("email",     StringType(), True),
        StructField("created_at",StringType(), True),
    ])
    parsed = (base
              .withColumn("json", expr("CAST(value AS STRING)"))
              .select(from_json(col("json"), schema).alias("data"),
                      "timestamp", "partition", "offset")
              .select("data.*", "timestamp", "partition", "offset"))

elif FORMAT.lower() == "avro":
    # Fetch schema string from Schema Registry
    resp = requests.get(f"{SCHEMA_REG}/subjects/{SUBJECT}/versions/latest")
    resp.raise_for_status()
    avro_schema_str = resp.json()["schema"]

    # Use from_avro (provided by spark-avro) to decode value bytes
    # Note: from_avro is available when spark-avro package is on the classpath
    spark.udf.registerJavaFunction  # this line just ensures Spark loads JVM functions early

    from pyspark.sql.avro.functions import from_avro
    parsed = (base
              .select(from_avro(col("value"), avro_schema_str).alias("data"),
                      "timestamp", "partition", "offset")
              .select("data.*", "timestamp", "partition", "offset"))
else:
    raise ValueError("EVENT_FORMAT must be 'json' or 'avro'")

# Example transformations:
# - keep only user-created events (if you add event_type later)
# - basic cleanup
result = (parsed
          .withColumnRenamed("created_at", "event_time")
          .filter(col("email").isNotNull()))

# Write stream to Parquet on MinIO/S3
query = (result.writeStream
         .format("parquet")
         .option("path", OUT_PATH)
         .option("checkpointLocation", CHECKPOINT)
         .outputMode("append")
         .start())

print(f"🚀 Streaming to {OUT_PATH} (checkpoint: {CHECKPOINT})")
query.awaitTermination()

