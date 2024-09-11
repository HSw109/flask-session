from itsdangerous import TaggedJSONSerializer

serializer = TaggedJSONSerializer()

# Serialize a Python object
data = {"foo": {1, 2, 3}}  # JSON doesn't natively support sets
serialized = serializer.dumps(data)
print(serialized)  # {"foo": ["__set__", [1, 2, 3]]}

# Deserialize it back to Python object
deserialized = serializer.loads(serialized)
print(deserialized)  # {'foo': {1, 2, 3}}
