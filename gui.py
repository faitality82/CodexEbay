from __future__ import annotations

import os
import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

from codexebay.models import Listing
from codexebay.services.ai_helper import AiListingAssistant
from codexebay.services.ebay import EbayAPIError, EbayService


class ListingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CodexEbay Listing Studio")
        self.geometry("860x640")

        self.ai_helper = AiListingAssistant()
        self.ebay_service = EbayService(
            client_id=os.getenv("EBAY_CLIENT_ID", ""),
            client_secret=os.getenv("EBAY_CLIENT_SECRET", ""),
            refresh_token=os.getenv("EBAY_REFRESH_TOKEN", ""),
            base_url=os.getenv("EBAY_BASE_URL", "https://api.ebay.com"),
        )

        self._build_form()

    def _build_form(self) -> None:
        self.inputs = {}

        form_frame = tk.Frame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        self._add_entry(form_frame, "Product Name", row=0)
        self._add_entry(form_frame, "Condition", row=1)
        self._add_entry(form_frame, "Category Hint", row=2)
        self._add_entry(form_frame, "Price (USD)", row=3)
        self._add_entry(form_frame, "Features (comma-separated)", row=4)
        self._add_entry(form_frame, "Image URLs (comma-separated)", row=5)

        self._add_separator(form_frame, row=6)

        self._add_entry(form_frame, "Title", row=7)
        self._add_text(form_frame, "Description", row=8)
        self._add_entry(form_frame, "Category", row=9)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=16, pady=8)

        generate_btn = tk.Button(button_frame, text="Generate Draft", command=self.generate_draft)
        generate_btn.pack(side=tk.LEFT, padx=8)

        publish_btn = tk.Button(button_frame, text="Publish Listing", command=self.publish_listing)
        publish_btn.pack(side=tk.LEFT, padx=8)

    def _add_entry(self, parent: tk.Widget, label: str, row: int) -> None:
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        entry = tk.Entry(parent, width=80)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        self.inputs[label] = entry
        parent.grid_columnconfigure(1, weight=1)

    def _add_text(self, parent: tk.Widget, label: str, row: int) -> None:
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="nw", pady=4)
        text = tk.Text(parent, width=80, height=10)
        text.grid(row=row, column=1, sticky="ew", pady=4)
        self.inputs[label] = text
        parent.grid_columnconfigure(1, weight=1)

    def _add_separator(self, parent: tk.Widget, row: int) -> None:
        separator = tk.Frame(parent, height=2, bd=1, relief=tk.SUNKEN)
        separator.grid(row=row, column=0, columnspan=2, sticky="ew", pady=12)

    def generate_draft(self) -> None:
        try:
            price = self._parse_price(self.inputs["Price (USD)"].get())
        except ValueError as exc:
            messagebox.showerror("Invalid price", str(exc))
            return

        features = self._parse_list(self.inputs["Features (comma-separated)"].get())
        images = self._parse_list(self.inputs["Image URLs (comma-separated)"].get())

        listing = self.ai_helper.generate_listing(
            product_name=self.inputs["Product Name"].get(),
            features=features,
            condition=self.inputs["Condition"].get(),
            category_hint=self.inputs["Category Hint"].get(),
            price=price,
            image_urls=images,
        )

        self._set_entry("Title", listing.title)
        self._set_text("Description", listing.description)
        self._set_entry("Category", listing.category)

    def publish_listing(self) -> None:
        try:
            listing = self._collect_listing()
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc))
            return

        try:
            response = self.ebay_service.create_listing(listing)
        except EbayAPIError as exc:
            messagebox.showerror("Publish failed", str(exc))
            return

        messagebox.showinfo("Listing published", f"Listing created: {response}")

    def _collect_listing(self) -> Listing:
        price = self._parse_price(self.inputs["Price (USD)"].get())
        images = self._parse_list(self.inputs["Image URLs (comma-separated)"].get())
        title = self.inputs["Title"].get().strip()
        description = self._get_text("Description")
        category = self.inputs["Category"].get().strip()

        listing = Listing(
            title=title,
            description=description,
            category=category,
            price=price,
            images=images,
        )
        errors = listing.validate()
        if errors:
            raise ValueError("\n".join(errors))
        return listing

    def _parse_price(self, value: str) -> Decimal:
        try:
            parsed = Decimal(value.strip())
        except (InvalidOperation, AttributeError):
            raise ValueError("Price must be a valid number.")
        if parsed <= 0:
            raise ValueError("Price must be greater than zero.")
        return parsed

    def _parse_list(self, value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    def _set_entry(self, label: str, value: str) -> None:
        entry = self.inputs[label]
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def _set_text(self, label: str, value: str) -> None:
        text = self.inputs[label]
        text.delete("1.0", tk.END)
        text.insert(tk.END, value)

    def _get_text(self, label: str) -> str:
        text = self.inputs[label]
        return text.get("1.0", tk.END).strip()


if __name__ == "__main__":
    app = ListingApp()
    app.mainloop()
