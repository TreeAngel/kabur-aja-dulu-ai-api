"""
ModelService — Singleton that loads all AI artifacts once at startup.
Never reload per-request to avoid memory and latency overhead.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import settings
from app.core.logger import logger


class ModelService:
    """Singleton wrapper for the Keras model and tokenizer."""

    _model: Any = None
    _tokenizer: dict | None = None
    _label_classes: list[str] | None = None
    _industry_skills: dict | None = None
    _loaded: bool = False

    # Tokenizer config (must match training — model input shape is [null, 200])
    MAX_LEN: int = 200

    @classmethod
    def load(cls) -> None:
        """Load all artifacts. Called once at application startup."""
        if cls._loaded:
            logger.info("ModelService already loaded — skipping.")
            return

        logger.info("Loading AI artifacts...")

        # ── Keras model ──────────────────────────────────────────
        try:
            import tensorflow as tf  # type: ignore

            model_path = settings.model_path
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found at: {model_path}")

            cls._model = tf.keras.models.load_model(str(model_path))
            logger.info(f"Model loaded from {model_path}")
        except Exception as exc:
            logger.error(f"Failed to load Keras model: {exc}")
            raise RuntimeError(f"Model load error: {exc}") from exc

        # ── Tokenizer ────────────────────────────────────────────
        try:
            tok_path = settings.tokenizer_path
            with open(tok_path, encoding="utf-8") as f:
                cls._tokenizer = json.load(f)
            logger.info(f"Tokenizer loaded from {tok_path}")
        except Exception as exc:
            logger.error(f"Failed to load tokenizer: {exc}")
            raise RuntimeError(f"Tokenizer load error: {exc}") from exc

        # ── Label classes ────────────────────────────────────────
        try:
            lc_path = settings.label_classes_path
            with open(lc_path, encoding="utf-8") as f:
                cls._label_classes = json.load(f)
            logger.info(f"Label classes loaded from {lc_path}: {cls._label_classes}")
        except Exception as exc:
            logger.error(f"Failed to load label classes: {exc}")
            raise RuntimeError(f"Label classes load error: {exc}") from exc

        # ── Industry skills ──────────────────────────────────────
        try:
            is_path = settings.industry_skills_path
            with open(is_path, encoding="utf-8") as f:
                cls._industry_skills = json.load(f)
            logger.info(f"Industry skills loaded from {is_path}")
        except Exception as exc:
            logger.error(f"Failed to load industry skills: {exc}")
            raise RuntimeError(f"Industry skills load error: {exc}") from exc

        cls._loaded = True
        logger.info("All AI artifacts loaded successfully.")

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._loaded

    @classmethod
    def get_model(cls) -> Any:
        if cls._model is None:
            raise RuntimeError("Model not loaded. Call ModelService.load() first.")
        return cls._model

    @classmethod
    def get_tokenizer(cls) -> dict:
        if cls._tokenizer is None:
            raise RuntimeError("Tokenizer not loaded.")
        return cls._tokenizer

    @classmethod
    def get_label_classes(cls) -> list[str]:
        if cls._label_classes is None:
            raise RuntimeError("Label classes not loaded.")
        return cls._label_classes

    @classmethod
    def get_industry_skills(cls) -> dict:
        if cls._industry_skills is None:
            raise RuntimeError("Industry skills not loaded.")
        return cls._industry_skills

    @classmethod
    def texts_to_sequences(cls, texts: list[str]) -> list[list[int]]:
        """
        Replicate Keras Tokenizer.texts_to_sequences() using the saved
        word_index from tokenizer.json.

        The Keras tokenizer saves word_index as a JSON-encoded string
        inside the 'config' key, so we need to parse it.
        """
        import json as _json

        tok = cls.get_tokenizer()
        config = tok.get("config", {})

        # word_index is stored as a JSON-encoded string in the Keras tokenizer format
        word_index_raw = config.get("word_index", "{}")
        if isinstance(word_index_raw, str):
            word_index: dict[str, int] = _json.loads(word_index_raw)
        else:
            word_index = word_index_raw

        sequences = []
        oov_index = word_index.get("<OOV>", 1)
        for text in texts:
            seq = [
                word_index.get(word.lower(), oov_index)
                for word in text.lower().split()
            ]
            sequences.append(seq)
        return sequences

    @classmethod
    def pad_sequences(cls, sequences: list[list[int]]) -> np.ndarray:
        """Post-pad or truncate sequences to MAX_LEN."""
        result = np.zeros((len(sequences), cls.MAX_LEN), dtype=np.int32)
        for i, seq in enumerate(sequences):
            trunc = seq[: cls.MAX_LEN]
            result[i, : len(trunc)] = trunc
        return result
