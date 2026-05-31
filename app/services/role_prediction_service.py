"""
Role Prediction Service — Deep Learning inference using the Keras model.

Inference pipeline (mirrors Notebook Section 17):
  skills list
    → join to string
    → tokenizer.texts_to_sequences()
    → pad_sequences()
    → model.predict()
    → argmax()
    → decode label
"""
from __future__ import annotations

import numpy as np

from app.ai.model_loader import ModelService
from app.core.logger import logger


def predict_role(skills: list[str]) -> tuple[str, float]:
    """
    Predict the industry role from a list of skills.

    Returns:
        Tuple of (role_name, confidence_score)
    """
    # Join skills into a single string (matching training pre-processing)
    skills_text = " ".join(skills)
    logger.debug(f"Role prediction input text: {skills_text!r}")

    # Tokenize
    sequences = ModelService.texts_to_sequences([skills_text])

    # Pad
    padded = ModelService.pad_sequences(sequences)

    # Predict
    model = ModelService.get_model()
    predictions = model.predict(padded, verbose=0)  # shape: (1, num_classes)

    # Decode
    pred_index = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][pred_index])

    label_classes = ModelService.get_label_classes()
    role = label_classes[pred_index]

    logger.info(f"Predicted role: {role!r} with confidence {confidence:.4f}")
    return role, round(confidence, 4)
