# Run this file once to set up configurations once
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ADMIN_DIR = os.path.join(BASE_DIR, "Admin")
DATASET_DIR = os.path.join(ADMIN_DIR, "Dataset")
HEALTHY_DIR = os.path.join(DATASET_DIR, "Healthy")
PARKINSON_DIR = os.path.join(DATASET_DIR, "Parkinson")
if not os.path.exists(DATASET_DIR):
    os.mkdir(DATASET_DIR)
if not os.path.exists(HEALTHY_DIR):
    os.mkdir(HEALTHY_DIR)
if not os.path.exists(PARKINSON_DIR):
    os.mkdir(PARKINSON_DIR)