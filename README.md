# CodexEbay

CodexEbay is a lightweight eBay listing helper that lets you draft, polish, and publish listings from a simple desktop GUI.

## Features
- **Listing model** with validation for required fields.
- **AI helper** to generate titles, descriptions, and categories from basic input.
- **eBay service layer** for authentication and publishing.
- **Tkinter GUI** for drafting and publishing listings.

## Getting Started

1. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Export your eBay credentials (sandbox or production):

```bash
export EBAY_CLIENT_ID="your-client-id"
export EBAY_CLIENT_SECRET="your-client-secret"
export EBAY_REFRESH_TOKEN="your-refresh-token"
# Optional if you want to hit a sandbox endpoint
export EBAY_BASE_URL="https://api.sandbox.ebay.com"
```

3. Launch the GUI:

```bash
python gui.py
```

Fill in the product details, generate a draft, and publish the listing.
