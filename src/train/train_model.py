from ultralytics import YOLO
import os
from dotenv import load_dotenv

load_dotenv()


def main():
    """Loading the data.yaml file and training the model."""
    model = YOLO("yolo11n.pt")
    model.train(
        data=os.getenv("MODEL_TRAIN_DATA"),
        epochs=int(os.getenv("MODEL_TRAIN_EPOCHS")),
        imgsz=int(os.getenv("MODEL_TRAIN_IMGSZ")),
        device=os.getenv("MODEL_TRAIN_DEVICE"),
        workers=int(os.getenv("MODEL_TRAIN_WORKERS")),
        batch=int(os.getenv("MODEL_TRAIN_BATCH")),
        name=os.getenv("MODEL_TRAIN_NAME"),
        exist_ok=bool(os.getenv("MODEL_TRAIN_EXIST_OK")),
    )


if __name__ == "__main__":
    main()
