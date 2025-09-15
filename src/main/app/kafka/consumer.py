import signal
from confluent_kafka import DeserializingConsumer
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

SCHEMA_REGISTRY_URL = "http://localhost:8081"
BOOTSTRAP = "localhost:9092"
TOPIC = "user-events"
GROUP_ID = "user-events-consumer"

def main():
    schema_client = SchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})
    latest = schema_client.get_latest_version("user-events-value")
    avro_schema_str = latest.schema.schema_str

    consumer = DeserializingConsumer({
        "bootstrap.servers": BOOTSTRAP,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
        "key.deserializer": StringDeserializer("utf_8"),
        "value.deserializer": AvroDeserializer(schema_client, avro_schema_str),
    })
    consumer.subscribe([TOPIC])

    running = True
    def stop(*_):
        nonlocal running; running = False
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print("👂 consuming user-events …")
    while running:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Kafka error:", msg.error())
            continue
        print(f"📥 {TOPIC} key={msg.key()} value={msg.value()}")

    consumer.close()

if __name__ == "__main__":
    main()

