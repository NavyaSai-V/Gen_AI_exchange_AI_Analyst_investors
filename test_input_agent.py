import os
import io
import re
import requests
from PIL import Image
import easyocr
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Helper for text cleaning
def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    text = text.strip()
    return text

# Use EasyOCR for OCR on images
def extract_text_with_easyocr(image_bytes, lang='en'):
    image_stream = io.BytesIO(image_bytes)
    image = Image.open(image_stream)
    reader = easyocr.Reader([lang], gpu=False)
    result = reader.readtext(image)
    # Join detected text lines
    return " ".join([item[1] for item in result])

# Extract text, images & links from PDF
def extract_pdf_content(pdf_path: str) -> Dict[str, Any]:
    reader = PdfReader(pdf_path)
    doc = fitz.open(pdf_path)
    all_text = ""
    images = []
    page_links = []
    graphs = []  # Placeholder for possible graph detection (needs ML for advanced detection)
    for i, page in enumerate(reader.pages):
        # Extract text
        page_text = page.extract_text() or ""
        all_text += page_text + "\n"
        # Extract links
        if "/Annots" in page:
            annots = page["/Annots"]
            for annot in annots:
                uri = annot.get_object()
                if "/A" in uri and "/URI" in uri["/A"]:
                    page_links.append(uri["/A"]["/URI"])
    # Extract images using fitz (PyMuPDF)
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            images.append({
                "page": page_idx,
                "img_idx": img_idx,
                "image_bytes": image_bytes,
                "ext": image_ext
            })
            # OCR on image (could be graph, figure, etc.) using EasyOCR
            ocr_text = extract_text_with_easyocr(image_bytes)
            if ocr_text.strip():
                graphs.append({"page": page_idx, "desc": clean_text(ocr_text)})
    return {
        "text": clean_text(all_text),
        "images": images,
        "links": list(set(page_links)),
        "graphs": graphs
    }

# Download and extract web content (text, images, graphs, captions)
def extract_website_content(url: str) -> Dict[str, Any]:
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Extract main text
        paragraphs = soup.find_all("p")
        website_text = clean_text(" ".join([p.get_text() for p in paragraphs]))
        # Extract images and attempt to get captions
        images = []
        for img in soup.find_all("img"):
            img_url = img.get("src")
            if not img_url:
                continue
            # Handle relative URLs
            img_url = requests.compat.urljoin(url, img_url)
            alt = img.get("alt", "")
            caption = ""
            # Try to find figcaption or nearby text
            parent = img.find_parent("figure")
            if parent:
                figcaption = parent.find("figcaption")
                if figcaption:
                    caption = figcaption.get_text().strip()
            if not caption and alt:
                caption = alt
            images.append({"img_url": img_url, "caption": caption})
        # Try to extract SVGs (graphs)
        graphs = []
        for svg in soup.find_all("svg"):
            desc = svg.get("aria-label") or svg.get("title") or svg.get_text()
            graphs.append({"svg": str(svg), "desc": clean_text(desc)})
        return {
            "website_text": website_text,
            "images": images,
            "graphs": graphs
        }
    except Exception as e:
        return {"website_text": "", "images": [], "graphs": [], "error": str(e)}

# Main orchestrator
def extract_all_content_from_pdf(pdf_path: str) -> Dict[str, Any]:
    pdf_data = extract_pdf_content(pdf_path)
    links = pdf_data["links"]
    web_data = []
    for link in links:
        web_content = extract_website_content(link)
        web_data.append({
            "url": link,
            "content": web_content
        })
    result = {
        "pdf_text": pdf_data["text"],
        "pdf_graphs": pdf_data["graphs"],
        "pdf_images": [{"page": img["page"], "img_idx": img["img_idx"], "ext": img["ext"]} for img in pdf_data["images"]],
        "web_data": web_data
    }
    return result

def save_all_data(all_data, filename='all_extracted_data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)



# Example usage
if __name__ == "__main__":
    pdf_path = "data/input/Naario/NaarioDeck2025.pdf"
    all_data = extract_all_content_from_pdf(pdf_path)
    # Just pretty print keys
    from pprint import pprint
    pprint(all_data)
    
    save_all_data(all_data)

