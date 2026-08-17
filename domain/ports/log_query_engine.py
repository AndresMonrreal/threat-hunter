from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities.detection import Detection

class LogQueryEnginePort(ABC):
    @abstractmethod
    def save_detections(self, detections: list[Detection]) -> None:
        """Guarda uno o mas detecciones guardadas"""
        raise NotImplementedError

    @abstractmethod
    def query_detections(self, in_origin: str | None = None, desde: datetime | None = None) -> list[Detection]:
        """
        Consulta detecciones guardadas. Sin filtros, regresa todas.
        ip_origen y desde acotan por IP y por fecha de inicio.
        """
        raise NotImplementedError