from setuptools import setup, find_packages

setup(
    name="eye_tracking",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy==1.24.3',
        'opencv-python==4.8.0.74',
        'mediapipe==0.10.8',
        'dlib-binary==19.24.1',
        'pandas==2.0.3',
        'matplotlib==3.7.1',
        'scikit-learn==1.3.0',
        'flask==2.3.3',
        'flask-cors==4.0.0',
        'flask-socketio==5.3.6',
        'python-socketio==5.8.0',
        'python-engineio==4.8.0',
        'eventlet==0.33.3'
    ]
) 