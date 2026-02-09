# CLAUDE.md — CodexEbay

## Project Overview

CodexEbay is a lightweight eBay listing helper for sellers. It provides two interfaces for drafting and publishing eBay listings:

1. **GUI application** (`gui.py`) — Tkinter desktop app for interactive listing creation, AI-assisted drafting, and direct eBay API publishing.
2. **CLI pipeline** (`src/ebay_seller_app.py`) — Command-line tool that generates listing drafts from product images (stub/heuristic-based, not real AI).

The project is in an early MVP phase. The AI helper uses simple keyword heuristics (not ML models), and the image research step is stubbed out.

## Repository Layout

```
CodexEbay/
├── README.md                       # Project description
├── requirements.txt                # Python dependencies (requests>=2.31.0)
├── gui.py                          # Tkinter GUI entry point
├── codexebay/                      # Core package (service layer)
│   ├── __init__.py
│   ├── models.py                   # Listing dataclass with validation
│   └── services/
│       ├── __init__.py
│       ├── ai_helper.py            # Heuristic-based listing generator
│       └── ebay.py                 # eBay OAuth + Sell API client
├── src/
│   └── ebay_seller_app.py          # CLI image-to-listing pipeline
└── docs/
    └── ebay-integration.md         # eBay API vs bulk upload integration guide
```

### Key branches

| Branch | Purpose |
|--------|---------|
| `main` | Base branch (README only) |
| `codex/define-listing-model-and-implement-service-layer` | Listing model, services, GUI |
| `codex/create-app-for-ebay-sellers` | CLI image-to-listing pipeline |

Code lives on feature branches; `main` has only the initial commit.

## Technology Stack

- **Language**: Python 3 (uses `__future__` annotations, dataclasses, type hints, `Decimal`)
- **GUI**: Tkinter (standard library)
- **HTTP**: `requests>=2.31.0` (only external dependency)
- **eBay integration**: OAuth 2.0 refresh-token flow, Sell Inventory API
- **Packaging**: PyInstaller (documented for Windows `.exe` builds)

## Development Setup

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Run the GUI
python gui.py

# Run the CLI pipeline
python3 src/ebay_seller_app.py <image-path> --query "item" --price 49.99 --condition Used
```

### Environment Variables (for eBay API access)

| Variable | Required | Description |
|----------|----------|-------------|
| `EBAY_CLIENT_ID` | Yes | OAuth client ID |
| `EBAY_CLIENT_SECRET` | Yes | OAuth client secret |
| `EBAY_REFRESH_TOKEN` | Yes | Long-lived refresh token |
| `EBAY_BASE_URL` | No | API base URL (defaults to `https://api.ebay.com`; set to `https://api.sandbox.ebay.com` for sandbox) |

## Architecture

### Service Layer (`codexebay/`)

- **`models.Listing`** — Dataclass with `title`, `description`, `category`, `price` (Decimal), `images`. Has a `validate()` method that returns a list of error strings.
- **`services.ai_helper.AiListingAssistant`** — Generates listing drafts from user input using keyword-to-category mapping. No external API calls.
- **`services.ebay.EbayService`** — Handles OAuth token refresh and listing creation via eBay's Sell Inventory API. Raises `EbayAPIError` on failures.

### CLI Pipeline (`src/ebay_seller_app.py`)

Data flow: `Image file → ImageInfo → ResearchResult (stub) → ListingDraft → JSON output`

Uses its own standalone dataclasses (`ImageInfo`, `ResearchResult`, `ListingDraft`), separate from the `codexebay` package.

### GUI (`gui.py`)

`ListingApp` extends `tk.Tk`. Two-phase workflow:
1. Fill in product details → click "Generate Draft" → AI helper populates title/description/category
2. Review/edit → click "Publish Listing" → `EbayService.create_listing()` sends to eBay

## Testing

No test framework or test files are currently configured. When adding tests:
- Use `pytest` as the test runner
- Place tests in a `tests/` directory mirroring the source layout
- The `Listing.validate()` method and `AiListingAssistant.generate_listing()` are good candidates for unit tests since they have no external dependencies

## Linting and Formatting

No linting or formatting tools are configured. The codebase follows:
- PEP 8 style conventions
- Type hints throughout (using `from __future__ import annotations`)
- Dataclasses for data models
- Descriptive variable/method names with underscore-prefixed private methods

## Build and Packaging

```bash
# Windows executable (run on Windows)
python -m pip install --upgrade pip pyinstaller
pyinstaller --onefile --name ebay-seller-app src/ebay_seller_app.py
# Output: dist/ebay-seller-app.exe
```

## Conventions for AI Assistants

### Code style
- Always include `from __future__ import annotations` at the top of Python files
- Use `dataclasses` for data models; prefer `Decimal` for monetary values
- Use type hints on all function signatures
- Prefix private methods with underscore (`_build_form`, `_parse_price`, etc.)
- Keep imports organized: stdlib, then third-party, then local

### Error handling
- Use custom exception classes (e.g., `EbayAPIError`) rather than bare exceptions
- Validate data at boundaries (model validation, input parsing)
- Return error lists from validation rather than raising immediately

### Security
- eBay credentials come from environment variables — never hardcode secrets
- Do not commit `.env` files or credentials
- The `EbayService` validates that credentials exist before making API calls

### Design principles
- Keep external dependencies minimal (currently only `requests`)
- Separate concerns: models, services, and UI are in distinct modules
- The CLI pipeline and GUI application are independent entry points that can evolve separately
- Stub implementations are acceptable for MVP; mark them clearly for future replacement
