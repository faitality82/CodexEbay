from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, Optional

import requests

from codexebay.models import Listing


class EbayAPIError(RuntimeError):
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class EbayService:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        base_url: str = "https://api.ebay.com",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None

    def authenticate(self) -> str:
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise EbayAPIError("Missing eBay credentials for authentication.")

        url = f"{self.base_url}/identity/v1/oauth2/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": "https://api.ebay.com/oauth/api_scope/sell.inventory",
        }
        response = self._request("post", url, data=payload, auth=(self.client_id, self.client_secret))
        token = response.get("access_token")
        if not token:
            raise EbayAPIError("Authentication response missing access token.")
        self._access_token = token
        return token

    def create_listing(self, listing: Listing) -> Dict[str, Any]:
        errors = listing.validate()
        if errors:
            raise EbayAPIError("Listing validation failed: " + ", ".join(errors))

        if not self._access_token:
            self.authenticate()

        url = f"{self.base_url}/sell/inventory/v1/offer"
        payload = self._build_offer_payload(listing)
        response = self._request("post", url, json=payload, headers=self._auth_headers())
        return response

    def _build_offer_payload(self, listing: Listing) -> Dict[str, Any]:
        data = asdict(listing)
        return {
            "sku": listing.title[:50].replace(" ", "-").lower(),
            "marketplaceId": "EBAY_US",
            "format": "FIXED_PRICE",
            "availableQuantity": 1,
            "listingDescription": listing.description,
            "pricingSummary": {
                "price": {
                    "currency": "USD",
                    "value": str(listing.price),
                }
            },
            "categoryId": listing.category,
            "merchantLocationKey": "default",
            "imageUrls": data.get("images", []),
        }

    def _auth_headers(self) -> Dict[str, str]:
        if not self._access_token:
            raise EbayAPIError("Access token missing. Authenticate first.")
        return {"Authorization": f"Bearer {self._access_token}", "Content-Type": "application/json"}

    def _request(self, method: str, url: str, **kwargs: Any) -> Dict[str, Any]:
        try:
            response = requests.request(method, url, timeout=20, **kwargs)
        except requests.RequestException as exc:
            raise EbayAPIError(f"Network error while calling eBay API: {exc}") from exc

        if response.status_code >= 400:
            details = self._safe_json(response)
            raise EbayAPIError(
                f"eBay API error {response.status_code}: {details}", status_code=response.status_code
            )

        return self._safe_json(response)

    @staticmethod
    def _safe_json(response: requests.Response) -> Dict[str, Any]:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"raw": response.text}
