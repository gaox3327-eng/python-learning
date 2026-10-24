import jsonschema

def assert_matches_schema(data,schema,label=""):
    """校验结构契约；失败的是可给出中文断言信息"""
    try:
        jsonschema.validate(data,schema)
    except jsonschema.ValidationError as exc:
        location = "/".join(str(p) for p in exc.path)or "(根)"
        raise AssertionError(
            f"{label}结构与契约不符：{exc.message} 位置:{location}"
        ) from exc   