# Fine-Tuning Models

## What is Fine-Tuning?

Fine-tuning means retraining a pre-trained PaddleOCR model on **your specific document type** with labeled data. This improves accuracy for that document type.

**Example**: A model fine-tuned on 200 invoice samples will extract invoice fields more accurately than the general model.

## When to Fine-Tune

Fine-tune when:
- The general model misses important fields
- Document layout is specialized (invoices, medical forms, bank statements)
- You have 100+ labeled samples of your document type
- Accuracy needs to be >95%

## Dataset Preparation

### 1. Collect Images
- Gather 100-500+ sample documents for your document type
- Ensure variety: different layouts, fonts, quality levels

### 2. Annotate Images
Use PaddleOCR's annotation tools or external services:
- Draw bounding boxes around text regions
- Label each text box with correct text
- Supported formats: COCO, VOC, YOLO

**Popular annotation tools:**
- Labelimg (free, open-source)
- CVAT (free, professional)
- Roboflow (cloud-based, has free tier)

### 3. Organize Dataset
```
datasets/invoice/
├── images/
│   ├── invoice_001.jpg
│   ├── invoice_002.jpg
│   └── ...
└── labels/
    ├── invoice_001.txt
    ├── invoice_002.txt
    └── ...
```

## Training Process

### 1. Set Up Training Environment
```bash
# Install training dependencies
pip install paddlepaddle paddleocr paddlex opencv-python

# Clone PaddleOCR repo for training code
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR
```

### 2. Configure Training
Create `configs/my_invoice_config.yml`:
```yaml
Global:
  epoch_num: 100
  log_smooth_window: 20
  print_batch_step: 50
  save_model_dir: ./models/invoice
  save_epoch_step: 5

Train:
  dataset_dir: ./datasets/invoice
  batch_size: 32
  
Eval:
  dataset_dir: ./datasets/invoice
```

### 3. Run Training
```bash
python tools/train.py -c configs/my_invoice_config.yml
```

### 4. Convert to Inference Model
```bash
python tools/export_model.py -c configs/my_invoice_config.yml -o Global.pretrained_model=models/invoice/best_accuracy
```

## Integration with App

Once trained:

1. Copy model files to `models/invoice/`
2. Update `src/core/ocr.py` to load custom models:
```python
def load_custom_model(self, model_path):
    self.ocr = PaddleOCR(model_path=model_path, lang='en')
```

3. The app automatically uses the fine-tuned model!

## Quick Alternative: Result Formatting

If you only have 1-2 samples and want custom output:

This is **NOT fine-tuning** - it's **post-processing**:
- Adjust how results are displayed
- Add custom parsing rules for your document type
- Format output into tables or structured fields

Edit `src/ui/app.py`'s `format_ocr_results()` function to customize output for your needs.

**Fine-tuning** = retraining the model with 100+ labeled samples
**Post-processing** = formatting the output of the existing model

## Resources

- [PaddleOCR Training Guide](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/quickstart_en.md)
- [Annotation Tools](https://github.com/heartexlabs/label-studio)
- [Dataset Preparation](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/custom_ocr_en.md)
