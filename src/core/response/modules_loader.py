from dataclasses import dataclass
from typing import Optional
from types import ModuleType


@dataclass
class ModuleInfo:
    """Модель для хранения роутера и settings модуля."""

    package: str
    root: str
    parent: Optional[str]

    router: ModuleType
    settings: ModuleType

    @property
    def is_root(self):
        return self.parent is None

    @property
    def has_children(self):
        return ".childes." in self.package
    
    @property
    def module_depth(self):
        return self.package.count(".childes.")
