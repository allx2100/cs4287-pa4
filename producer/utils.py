import pickle

def unpickle(file):
    with open(file, 'rb') as fo:
        dict = pickle.load(fo, encoding='bytes')
    return dict

def save_data(data, file):
    with open(file, 'wb') as f:
        pickle.dump(data, f)