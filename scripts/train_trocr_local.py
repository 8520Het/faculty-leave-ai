import os
import sys
from pathlib import Path
import csv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import torch
from PIL import Image
from torch.utils.data import Dataset
from transformers import (
    TrOCRProcessor,
    VisionEncoderDecoderModel,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    default_data_collator,
)
import evaluate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "trocr_dataset"
IMAGES_DIR = DATASET_DIR / "images"
METADATA_FILE = DATASET_DIR / "metadata.csv"
OUTPUT_MODEL_DIR = PROJECT_ROOT / "backend" / "models" / "trocr-fine-tuned-faculty"

print("==================================================")
print("     TrOCR Local Fine-Tuning on RTX 4050          ")
print("==================================================")

if not torch.cuda.is_available():
    print("Warning: CUDA is not detected. Training will run on CPU.")
    device_name = "CPU"
    use_fp16 = False
else:
    device_name = torch.cuda.get_device_name(0)
    print(f"CUDA Device: {device_name}")
    print(f"Allocated VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    use_fp16 = True

# 1. Load CSV data
records = []
with open(METADATA_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        records.append(row)

print(f"Loaded {len(records)} training samples from {METADATA_FILE}")

# Train / Validation split (85% train, 15% validation)
split_idx = int(len(records) * 0.85)
train_records = records[:split_idx]
eval_records = records[split_idx:] if split_idx < len(records) else records[:2]

processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")

class FacultyDataset(Dataset):
    def __init__(self, data_list, img_dir, proc, max_target_length=40):
        self.data_list = data_list
        self.img_dir = img_dir
        self.proc = proc
        self.max_target_length = max_target_length

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx):
        item = self.data_list[idx]
        img_path = self.img_dir / item["file_name"]
        image = Image.open(str(img_path)).convert("RGB")

        pixel_values = self.proc(image, return_tensors="pt").pixel_values.squeeze(0)
        labels = self.proc.tokenizer(
            item["text"],
            padding="max_length",
            max_length=self.max_target_length,
            truncation=True,
            return_tensors="pt"
        ).input_ids.squeeze(0)

        # Ignore padding tokens in loss calculation
        labels[labels == self.proc.tokenizer.pad_token_id] = -100
        return {"pixel_values": pixel_values, "labels": labels}

train_dataset = FacultyDataset(train_records, IMAGES_DIR, processor)
eval_dataset = FacultyDataset(eval_records, IMAGES_DIR, processor)

# 2. Load Model
print("\nLoading base model weights: microsoft/trocr-base-handwritten...")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-handwritten")

# Set special tokens and generation settings
model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
model.config.pad_token_id = processor.tokenizer.pad_token_id
model.config.vocab_size = model.config.decoder.vocab_size
model.config.eos_token_id = processor.tokenizer.sep_token_id
model.config.max_length = 40
model.config.early_stopping = True
model.config.no_repeat_ngram_size = 3
model.config.length_penalty = 2.0
model.config.num_beams = 4

# 3. CER Metric
cer_metric = evaluate.load("cer")

def compute_metrics(pred):
    labels_ids = pred.label_ids
    pred_ids = pred.predictions
    pred_str = processor.batch_decode(pred_ids, skip_special_tokens=True)
    labels_ids[labels_ids == -100] = processor.tokenizer.pad_token_id
    label_str = processor.batch_decode(labels_ids, skip_special_tokens=True)
    return {"cer": cer_metric.compute(predictions=pred_str, references=label_str)}

# 4. RTX 4050 6GB Memory-Optimized Training Arguments
training_args = Seq2SeqTrainingArguments(
    output_dir="./trocr_faculty_checkpoints",
    predict_with_generate=True,
    eval_strategy="epoch",
    save_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=2,          # Optimized for 6GB VRAM
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=2,          # Effective batch size = 4
    num_train_epochs=10,
    fp16=use_fp16,                          # Tensor Core FP16 acceleration
    save_total_limit=1,
    logging_steps=5,
    load_best_model_at_end=True,
    metric_for_best_model="cer",
    greater_is_better=False,
    report_to="none"
)

trainer = Seq2SeqTrainer(
    model=model,
    tokenizer=processor.image_processor,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=default_data_collator,
)

print(f"\n[START] Training started for 10 epochs on {device_name}...")
trainer.train()

# 5. Save the fine-tuned model
OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)
trainer.save_model(str(OUTPUT_MODEL_DIR))
processor.save_pretrained(str(OUTPUT_MODEL_DIR))
print("\n==================================================")
print("[SUCCESS] Fine-tuned TrOCR model saved to:")
print(f"   {OUTPUT_MODEL_DIR}")
print("==================================================")
