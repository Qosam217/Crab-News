"""Source Adapter Registry for Crab News."""

from typing import Type, Dict
from ..database.models import SourceModel
from .base import BaseSource
from .antara import AntaraSource
from .cnn_indonesia import CNNIndonesiaSource
from .kompas import KompasSource
from .detik import DetikSource
from .tempo import TempoSource
from .rss_generic import GenericRSSSource

SOURCE_REGISTRY: Dict[str, Type[BaseSource]] = {
    "antara": AntaraSource,
    "cnn-indonesia": CNNIndonesiaSource,
    "kompas": KompasSource,
    "detik": DetikSource,
    "tempo": TempoSource,
}


def get_source_adapter(source: SourceModel) -> BaseSource:
    """Returns the matching BaseSource adapter class for a given source model."""
    adapter_cls = SOURCE_REGISTRY.get(source.slug.lower(), GenericRSSSource)
    return adapter_cls(source)
