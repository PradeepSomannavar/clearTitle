"""
Pipeline stage state machine.

Pure logic. No I/O, no imports beyond stdlib — safe to use from any layer.
"""

from enum import IntEnum


class Stage(IntEnum):
    UPLOADED = 0
    PREPROCESSING = 1
    PREPROCESSED = 2
    OCR_IN_PROGRESS = 3
    OCR_DONE = 4
    MERGING = 5
    MERGED = 6
    CLASSIFYING = 7
    CLASSIFIED = 8

    # Terminal/Error states - negative values to keep clean from comparison
    FAILED = -1
    CLASSIFICATION_FAILED = -2
    SKIPPED = -3


def stage_from_status(status: str) -> Stage:
    if not status:
        return Stage.UPLOADED
    status_lower = status.lower()
    mapping = {
        "uploaded": Stage.UPLOADED,
        "preprocessing": Stage.PREPROCESSING,
        "preprocessed": Stage.PREPROCESSED,
        "ocr_in_progress": Stage.OCR_IN_PROGRESS,
        "ocr_done": Stage.OCR_DONE,
        "merging": Stage.MERGING,
        "merged": Stage.MERGED,
        "classifying": Stage.CLASSIFYING,
        "classified": Stage.CLASSIFIED,
        "classification_failed": Stage.CLASSIFICATION_FAILED,
        "failed": Stage.FAILED,
        "skipped": Stage.SKIPPED,
        "complete": Stage.CLASSIFIED,
        "processing": Stage.PREPROCESSING,
        "pending_retry": Stage.UPLOADED,
    }
    return mapping.get(status_lower, Stage.UPLOADED)


def already_past(status: str, target: Stage) -> bool:
    curr = stage_from_status(status)
    if curr in (Stage.FAILED, Stage.CLASSIFICATION_FAILED):
        return False
    if curr == Stage.SKIPPED:
        return True
    return curr >= target
