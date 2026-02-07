from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List


@dataclass
class Listing:
    title: str
    description: str
    category: str
    price: Decimal
    images: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        errors = []
        if not self.title.strip():
            errors.append("Title is required.")
        if not self.description.strip():
            errors.append("Description is required.")
        if not self.category.strip():
            errors.append("Category is required.")
        if self.price <= 0:
            errors.append("Price must be greater than zero.")
        return errors
