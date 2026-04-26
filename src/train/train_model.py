from ultralytics import YOLO

def main():
    # Load a model
    model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)

    # Train the model
    model.train(
        data="input/data.yaml", 
        epochs=100, 
        imgsz=640, 
        device='cpu',
        worker=2,
        batch=4, 
        name="boa_ocr_model"
    )

if __name__ == "__main__":
    main()