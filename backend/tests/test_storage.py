import pytest
from app.storage import OptionalArtifactStorage

def test_artifact_storage_requires_explicit_consent(monkeypatch):
    monkeypatch.setenv("OBJECT_STORAGE_ENABLED", "false")
    storage = OptionalArtifactStorage()
    with pytest.raises(ValueError, match="明确授权"):
        storage.upload("user", "photo.jpg", b"image", "image/jpeg", False)

def test_artifact_storage_is_disabled_by_default(monkeypatch):
    monkeypatch.setenv("OBJECT_STORAGE_ENABLED", "false")
    storage = OptionalArtifactStorage()
    with pytest.raises(ValueError, match="未启用"):
        storage.upload("user", "photo.jpg", b"image", "image/jpeg", True)
