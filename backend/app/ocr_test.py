from pathlib import Path

import torch
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel


# -------------------------------------------------
# Project paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ROW_DIR = BASE_DIR / "data" / "crops" / "clean_rows"

IMAGE_PATH = ROW_DIR / "assignment_row_1.jpg"


# -------------------------------------------------
# Check input
# -------------------------------------------------

if not IMAGE_PATH.exists():
    print("Image not found:")
    print(IMAGE_PATH)
    raise SystemExit


print("Testing image:")
print(IMAGE_PATH)


# -------------------------------------------------
# Device
# -------------------------------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("Using device:", device)


# -------------------------------------------------
# Load model
# -------------------------------------------------

MODEL_NAME = "microsoft/trocr-base-handwritten"

print("Loading TrOCR...")


processor = TrOCRProcessor.from_pretrained(
    MODEL_NAME
)

model = VisionEncoderDecoderModel.from_pretrained(
    MODEL_NAME
)

model.to(device)
model.eval()

print("Model loaded")


# -------------------------------------------------
# Load image
# -------------------------------------------------

image = Image.open(
    IMAGE_PATH
).convert("RGB")


print("Image size:", image.size)


# -------------------------------------------------
# Prepare input
# -------------------------------------------------

pixel_values = processor(
    images=image,
    return_tensors="pt"
).pixel_values.to(device)


# -------------------------------------------------
# OCR
# -------------------------------------------------

print("Running OCR...")


with torch.no_grad():

    generated_ids = model.generate(
        pixel_values,
        max_new_tokens=128,
        num_beams=4
    )


recognized_text = processor.batch_decode(
    generated_ids,
    skip_special_tokens=True
)[0]


# -------------------------------------------------
# Result
# -------------------------------------------------

print()
print("----------------------------------------")
print("OCR RESULT")
print("----------------------------------------")

print(recognized_text)

print("----------------------------------------")