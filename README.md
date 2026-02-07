# CodexEbay

Minimal working model for an image-to-eBay listing pipeline.

## Quick start
```bash
python3 src/ebay_seller_app.py path/to/image.jpg --query "running shoe" --price 49.99 --condition Used
```

The script outputs a JSON draft that includes:
- Image metadata
- Stub research results (category, title, attributes)
- A listing draft ready to map into eBay API payloads or bulk upload files

## Build a Windows executable (PyInstaller)
Use PyInstaller on a Windows machine to create a standalone `.exe`:

```bash
python -m pip install --upgrade pip pyinstaller
pyinstaller --onefile --name ebay-seller-app src/ebay_seller_app.py
```

The executable will be in `dist/ebay-seller-app.exe`.

## Notes
- The current implementation uses a stub research step and does not call external AI or eBay APIs.
- Use this as a starting point for wiring real image recognition, web research, and eBay integrations.
