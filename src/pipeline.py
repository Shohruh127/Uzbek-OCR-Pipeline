import logging
import os
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pdf2image import convert_from_path

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    input_path: str
    classification: str
    text: str = ""
    pages: int = 0
    audit_log: List[Dict[str, Any]] = field(default_factory=list)

def process_document(input_path: str) -> PipelineResult:
    result = PipelineResult(input_path=input_path, classification="scan")
    
    # 1. Initialize Engine (Lazy Load)
    try:
        from paddleocr import PaddleOCR
        # lang='en' supports Latin/Uzbek characters well
        ocr_engine = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    except ImportError:
        logger.error("PaddleOCR not installed.")
        return result

    images = []
    
    # 2. Convert Input to Images
    try:
        if input_path.lower().endswith(".pdf"):
            logger.info(f"Converting PDF: {input_path}")
            images = convert_from_path(input_path)
        else:
            from PIL import Image
            images = [Image.open(input_path)]
            
        result.pages = len(images)
        logger.info(f"Successfully loaded {len(images)} pages.")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return result

    # 3. Run OCR on Each Page
    full_text_parts = []
    
    for i, img in enumerate(images):
        logger.info(f"Scanning page {i+1}...")
        try:
            img_np = np.array(img)
            ocr_result = ocr_engine.ocr(img_np, cls=True)
            
            page_text = []
            if ocr_result and ocr_result[0]:
                # Sort boxes by Y (vertical) then X (horizontal)
                sorted_lines = sorted(ocr_result[0], key=lambda x: (x[0][1], x[0][0]))
                
                for line in sorted_lines:
                    text_content = line[1][0]
                    confidence = line[1][1]
                    
                    if confidence > 0.6:
                        page_text.append(text_content)
            
            # Formatting
            full_text_parts.append(f"\n--- PAGE {i+1} ---\n")
            full_text_parts.append("\n".join(page_text))
            
        except Exception as e:
            logger.error(f"OCR Error on page {i+1}: {e}")
    
    result.text = "\n".join(full_text_parts)
    return result