import numpy as np
from scipy.ndimage import gaussian_filter
from utils import *

def load_data(data_file):
    data = unpickle(data_file)
    images = data['images']
    labels = data['labels']
    filenames = data['filenames']
    label_names = data['label_names']

    return images, labels, filenames, label_names

def sample_image(images, labels, filenames):
    index = np.random.randint(0, len(images))
    return index, add_noise_and_scale(images[index]), labels[index], filenames[index]

def add_noise_and_scale(image):
    mean_vector = np.array([[0.4914], [0.4822], [0.4465]])
    std_vector = np.array([[0.2471], [0.2435], [0.2616]])

    new_image = image.reshape((3,1024)).astype(dtype=np.float32)
    new_image = (new_image - np.mean(new_image, axis=1, keepdims=True)) / np.std(new_image, axis=1, keepdims=True)
    new_image = new_image * std_vector + mean_vector
    new_image = new_image.flatten()
    return gaussian_filter(new_image, sigma=1e-20)