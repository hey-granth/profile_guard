from django.db import models
from django.contrib.postgres.fields import ArrayField
from pgvector.django import VectorField


class BaseModel(models.Model):
    """Base model with common fields"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EmbeddingMixin(models.Model):
    """Mixin for models that store embeddings"""

    embedding = VectorField(dimensions=512, null=True, blank=True)

    class Meta:
        abstract = True
