import jsonschema

def assert_matches_schema(instance, schema):
    """校验json结构符合schema契约"""
    jsonschema.validate(instance=instance, schema=schema)
