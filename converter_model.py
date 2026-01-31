import tensorflow as tf
import os

# 1. Load your best model
model_path = "best_disease_model.h5" # Or plant_disease_model.h5
print(f"🔄 Loading {model_path}...")
model = tf.keras.models.load_model(model_path)

# 2. Convert to TFLite (The "Lite" version for the App)
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# 3. Save the TFLite file
output_path = "crop_disease.tflite"
with open(output_path, 'wb') as f:
    f.write(tflite_model)
print(f"✅ Success! Saved as {output_path}")

# 4. CRITICAL: Try to find the class order
# (This works if you used ImageDataGenerator)
print("\n⚠️ CHECK YOUR ai_engine.py LIST AGAINST THIS ORDER:")
print("---------------------------------------------------")
# Usually, Keras doesn't save class names inside the h5.
# BUT, standard practice is ALPHABETICAL.
# If you know the folder names you trained on, list them alphabetically here:
print("If you trained using folders, the model uses ALPHABETICAL order.")
print("Example: ['Aphids...', 'Bacterial...', 'Fungal...', 'Healthy...']")
print("You MUST update DISEASE_CLASSES in ai_engine.py to match this alphabetical order.")
print("---------------------------------------------------")