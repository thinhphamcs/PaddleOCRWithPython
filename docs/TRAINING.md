# How to train the model locally

## Installation

### 1. Install labelImg and Run it

In the terminal
```bash
sudo apt-get install libxcb-cursor0
sudo apt-get install libqt5gui5 libqt5core5a libqt5widgets5 libqt5dbus5
```

In the python project
```bash
pip install labelImg
```
```bash
export QT_QPA_PLATFORM=xcb
labelImg
```

### 2. Debuging

Once the program starts, it is easy crashed. Modified python file mentioned in the error log:
canvas.py | line 526, line 530, and 531 | wraps the variables with int()

### 3. Preperation before trainning

After UI pop up a window, make sure to add the directory and before saving the label make sure switching to YOLO instead of PascalVOC because YOLO gives you .txt whereas PascalVOC gives you .xml

Create a new file named data.yaml in the input/ folder.

```bash
path: # Use your actual path
train: train/images
val: train/images

nc: # Depending on how many labels you have, in my case 7
names: ['name of your label', 'etc']
```

### 4. Training

Run the training script

```bash
python src/train/train_model.py
```

Which will generated the .pt file, move the fil to data/output/