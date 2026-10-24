import pytest

from data.post_data import post_data

import json
from pathlib import Path
from common.validators import assert_matches_schema

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"

def load_schema(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))

@pytest.mark.parametrize("post_id", [1, 2, 3])
def test_get_post(post_api, post_id):
    response = post_api.get_post(post_id)

    assert response.status_code == 200

    data = response.json()
    assert isinstance (data["id"],int)
    assert data["id"] > 0

    assert isinstance (data["title"],str)
    assert len(data["title"])>0

    assert isinstance(data["userId"], int)
    assert data["userId"]>0

    assert isinstance(data["body"], str)      
    assert len(data["body"]) > 0 

def test_create_post(post_api):
    response = post_api.create_post(post_data)

    result = response.json()

    assert response.status_code == 201
    assert result["title"] == post_data["title"]
    assert result["body"] == post_data["body"]
    assert result["userId"] == post_data["userId"]
    assert "id" in result

def test_get_post_not_found(post_api):
    response = post_api.get_post(999)
    assert response.status_code == 404
def test_get_post_invalid_id(post_api):
    response = post_api.get_post("abc")
    assert response.status_code == 404
@pytest.mark.xfail(raises=AssertionError,strict=True,
                   reason="缺陷:删除不存在的资源返回 200 而非 404")
def test_delete_not_found(post_api):
    response = post_api.delete_post(99999)
    assert response.status_code == 404

def test_get_post_schema(post_api):
    response = post_api.get_post(1)
    assert response.status_code == 200
    assert_matches_schema(response.json(), load_schema("post_schema.json"), "GET /posts/1")  
    
    
