from dataclasses import dataclass
from typing import List

from domain.entities.db.models.executor import Executor as ExecutorDomain


@dataclass
class Genre:
    id: int
    title: str
    executors: List[ExecutorDomain] = None
