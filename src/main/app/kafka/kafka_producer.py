from datetime import datetime, timezone
from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

# Local endpoints
SCHEMA_REGISTRY_URL = "http://localhost:8081"
BOOTSTRAP = "localhost:9092"
TOPIC = "user-events"
SUBJECT = "user-events-value"

_schema_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
_latest = _schema_client.get_latest_version(SUBJECT)
_avro_schema_str = _latest.schema.schema_str
_avro_serializer = AvroSerializer(_schema_client, _avro_schema_str)

_producer = SerializingProducer({
    "bootstrap.servers": BOOTSTRAP,
    "key.serializer": StringSerializer("utf_8"),
    "value.serializer": _avro_serializer,
})

def _delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(f"✅ Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

def publish_user_created(user_id: int, name: str, email: str):
    value = {
        "id": int(user_id),
        "name": name,
        "email": email,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _producer.produce(topic=TOPIC, key=email, value=value, on_delivery=_delivery_report)
    _producer.flush()  # simple/sync for now

