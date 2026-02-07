#!/usr/bin/env python3
"""Minimal working model for an image-to-eBay listing pipeline."""
from __future__ import annotations

import argparse
import hashlib
import imghdr
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ImageInfo:
    filename: str
    file_size_bytes: int
    image_type: Optional[str]
    sha256: str


@dataclass
class ResearchResult:
    title_guess: str
    brand_guess: Optional[str]
    category_guess: str
    attributes: Dict[str, Any]
    sources: List[str]


@dataclass
class ListingDraft:
    title: str
    category: str
    condition: str
    quantity: int
    price: float
    currency: str
    description: str
    attributes: Dict[str, Any]
    images: List[str]
    shipping: Dict[str, Any]
    returns: Dict[str, Any]


def read_image_info(path: str) -> ImageInfo:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")

    file_size = os.path.getsize(path)
    image_type = imghdr.what(path)
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            sha256_hash.update(chunk)

    return ImageInfo(
        filename=os.path.basename(path),
        file_size_bytes=file_size,
        image_type=image_type,
        sha256=sha256_hash.hexdigest(),
    )


def stub_research(image_info: ImageInfo, query: Optional[str]) -> ResearchResult:
    keyword = (query or image_info.filename).lower()

    if "shoe" in keyword:
        category = "Shoes"
        title = "Athletic Running Shoes"
        brand = "Generic"
        attributes = {"Size": "10", "Color": "Black"}
    elif "phone" in keyword:
        category = "Cell Phones"
        title = "Smartphone Unlocked"
        brand = "Generic"
        attributes = {"Storage": "128GB", "Color": "Midnight"}
    else:
        category = "Collectibles"
        title = "Vintage Item"
        brand = None
        attributes = {"Material": "Unknown"}

    return ResearchResult(
        title_guess=title,
        brand_guess=brand,
        category_guess=category,
        attributes=attributes,
        sources=[
            "stub://local-heuristics",
            f"image-hash:{image_info.sha256[:12]}",
        ],
    )


def build_listing(
    research: ResearchResult,
    image_info: ImageInfo,
    price: float,
    condition: str,
) -> ListingDraft:
    description = (
        f"Auto-generated listing draft on {datetime.utcnow().isoformat()}Z. "
        "Review details before publishing."
    )
    attributes = dict(research.attributes)
    if research.brand_guess:
        attributes.setdefault("Brand", research.brand_guess)

    return ListingDraft(
        title=research.title_guess,
        category=research.category_guess,
        condition=condition,
        quantity=1,
        price=price,
        currency="USD",
        description=description,
        attributes=attributes,
        images=[image_info.filename],
        shipping={"service": "USPSGroundAdvantage", "cost": 6.95},
        returns={"accepted": True, "days": 30},
    )


def build_output(
    image_info: ImageInfo,
    research: ResearchResult,
    listing: ListingDraft,
) -> Dict[str, Any]:
    return {
        "image": asdict(image_info),
        "research": asdict(research),
        "listing": asdict(listing),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an eBay listing draft from an image (stub model)."
    )
    parser.add_argument("image", help="Path to the product image")
    parser.add_argument(
        "--query",
        help="Optional text hint to improve the stub research step",
    )
    parser.add_argument(
        "--price",
        type=float,
        default=19.99,
        help="Draft price for the listing",
    )
    parser.add_argument(
        "--condition",
        default="Used",
        choices=["New", "Used", "For parts"],
        help="Condition for the listing",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_info = read_image_info(args.image)
    research = stub_research(image_info, args.query)
    listing = build_listing(research, image_info, args.price, args.condition)
    output = build_output(image_info, research, listing)
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
