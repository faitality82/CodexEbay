# eBay seller integration options

## Goal
Provide a clear path for connecting a seller-focused app to eBay so it can publish listings and support bulk uploads, with a recommendation on which path is easier for sellers to implement.

## Integration paths

### 1) eBay APIs (recommended for automation)
**What it is**: Connect directly to eBay’s seller APIs to create, update, and manage listings programmatically.

**Typical flow**
1. Seller creates/links an eBay developer application.
2. App uses OAuth (user consent) to get a token scoped for seller actions.
3. App calls listing APIs to create/modify items.
4. App stores eBay item IDs for updates and status checks.

**Pros**
- Full automation and real-time listing creation.
- Fine-grained control over data quality and validation.
- Better for high-volume and ongoing listing workflows.

**Cons**
- More setup for the seller (developer keys, OAuth consent).
- Requires ongoing maintenance for API changes.

**Best for**
- Sellers who want automated listing creation from scanned images and AI-enriched metadata.

### 2) Bulk listing file upload (CSV/XML)
**What it is**: Export a listing file in the format eBay accepts and let the seller upload it via their eBay Seller Hub or another eBay-supported bulk upload workflow.

**Typical flow**
1. App generates a bulk file from AI-enriched item data.
2. Seller uploads the file in eBay’s bulk listing UI.
3. Seller resolves any validation errors and publishes listings.

**Pros**
- Lower integration burden for the app (no OAuth, no API credentials).
- Familiar workflow for sellers who already use bulk uploads.

**Cons**
- Less automation; requires manual upload and error handling.
- Slower iteration (upload, wait for validation, fix, re-upload).
- Limited feedback for real-time listing creation.

**Best for**
- Sellers who want a simple export path and are comfortable with manual bulk upload steps.

## Recommendation: easiest path for sellers to implement
**Bulk file upload is the easiest to implement quickly** because it avoids OAuth setup and API credential management. It’s the simplest on-boarding path if the app’s main goal is to help prepare high-quality listing data and then hand it off to the seller for upload.

**API integration is the best long-term path** for a fully automated experience, but it requires more up-front effort. If the product’s goal is “scan → research → auto-list,” then the API route should be the primary target once the MVP is validated.

## Suggested phased approach
1. **Phase 1 (MVP)**: Build CSV/XML export for bulk listing upload and include a validation step in-app to minimize upload errors.
2. **Phase 2**: Add OAuth-based API integration for automated listing creation and updates.

## Key implementation notes for the app
- Track required listing fields (category, condition, quantity, price, photos, shipping, return policy) and only include fields that apply to the item type.
- Provide field-level validation and a pre-flight check before export or API submission.
- Keep a mapping layer so the same internal item data can power both API payloads and bulk listing file exports.
