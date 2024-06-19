
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing import image

# Функция для загрузки и предобработки изображения
def load_and_preprocess_image(image_path):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.
    return img_array

# Загрузка обученной модели
model = tf.keras.models.load_model('tumor11.h5')

# Загрузка и предобработка новых изображений
image_paths = ['gg (4).jpg', 'image (56).jpg', 'gg (417).jpg', 'gg (316).jpg']
for image_path in image_paths:
    img = load_and_preprocess_image(image_path)

    # Предсказание класса
    predictions = model.predict(img)
    predicted_class = np.argmax(predictions)

    # Вывод результата
    print(f'Image: {image_path}, Predicted class: {predicted_class}')