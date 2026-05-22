import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping
import os
import json

# =====================================
# DATASET PATHS
# =====================================

train_dir = "dataset/train"
valid_dir = "dataset/valid"

# =====================================
# IMAGE SETTINGS
# =====================================

img_size = 224
batch_size = 16

# =====================================
# DATA AUGMENTATION
# =====================================

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    shear_range=0.2,
    horizontal_flip=True,
    brightness_range=[0.8, 1.2]
)

valid_datagen = ImageDataGenerator(
    rescale=1./255
)

# =====================================
# TRAIN GENERATOR
# =====================================

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    class_mode='categorical'
)

# =====================================
# VALID GENERATOR
# =====================================

valid_generator = valid_datagen.flow_from_directory(
    valid_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    class_mode='categorical'
)

# =====================================
# SAVE CLASS NAMES
# =====================================

class_names = list(train_generator.class_indices.keys())

os.makedirs("model", exist_ok=True)

with open("model/class_names.json", "w") as f:

    json.dump(class_names, f)

# =====================================
# LOAD MOBILENETV2
# =====================================

base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)

# Freeze pretrained layers
base_model.trainable = True

for layer in base_model.layers[:-30]:
    layer.trainable = False

# =====================================
# BUILD MODEL
# =====================================

x = base_model.output

x = GlobalAveragePooling2D()(x)

x = Dropout(0.3)(x)

predictions = Dense(
    train_generator.num_classes,
    activation='softmax'
)(x)

model = Model(
    inputs=base_model.input,
    outputs=predictions
)

# =====================================
# COMPILE MODEL
# =====================================

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# =====================================
# EARLY STOPPING
# =====================================

early_stop = EarlyStopping(
    monitor='val_loss',
    patience=3,
    restore_best_weights=True
)

# =====================================
# TRAIN MODEL
# =====================================

history = model.fit(
    train_generator,
    validation_data=valid_generator,
    epochs=3,
    callbacks=[early_stop]
)

# =====================================
# SAVE MODEL
# =====================================

model.save("model/plant_disease_model.h5")

print("✅ Model Trained & Saved Successfully")