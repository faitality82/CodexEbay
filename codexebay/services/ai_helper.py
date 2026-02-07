from __future__ import annotations

from decimal import Decimal
from typing import Dict, List

from codexebay.models import Listing


class AiListingAssistant:
    """Generate listing content from user input using lightweight heuristics."""

    CATEGORY_MAP: Dict[str, str] = {
        "laptop": "Electronics > Computers & Tablets",
        "phone": "Electronics > Cell Phones & Accessories",
        "camera": "Cameras & Photo",
        "furniture": "Home & Garden > Furniture",
        "shoes": "Clothing, Shoes & Accessories > Shoes",
        "collectible": "Collectibles",
    }

    def generate_listing(
        self,
        product_name: str,
        features: List[str],
        condition: str,
        category_hint: str,
        price: Decimal,
        image_urls: List[str],
    ) -> Listing:
        normalized_name = product_name.strip()
        normalized_condition = condition.strip() or "Good"
        features_text = ", ".join(feature.strip() for feature in features if feature.strip())
        category = self._pick_category(category_hint, normalized_name)

        title_parts = [normalized_name, normalized_condition]
        if features_text:
            title_parts.append(features_text)
        title = " - ".join(part for part in title_parts if part)

        description_lines = [
            f"{normalized_name} in {normalized_condition} condition.",
            "\nKey features:",
        ]
        if features_text:
            description_lines.append(f"- {features_text}")
        else:
            description_lines.append("- No additional features provided.")
        description_lines.extend(
            [
                "\nWhat you get:",
                "- Item exactly as shown in photos.",
                "- Ships securely with tracking.",
            ]
        )
        description = "\n".join(description_lines)

        return Listing(
            title=title,
            description=description,
            category=category,
            price=price,
            images=image_urls,
        )

    def _pick_category(self, hint: str, product_name: str) -> str:
        lookup_source = f"{hint} {product_name}".lower()
        for keyword, category in self.CATEGORY_MAP.items():
            if keyword in lookup_source:
                return category
        return hint.strip() or "Other"
