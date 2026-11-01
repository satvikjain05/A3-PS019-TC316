"""
tests/test_evaluation.py
Unit tests for Evaluator, Precision/Recall calculations, and error analysis.
"""

import pytest
from scanner.evaluation import Evaluator


@pytest.fixture
def evaluator():
    return Evaluator()


def test_ground_truth_loads_correctly(evaluator):
    df = evaluator.load_ground_truth()
    assert len(df) >= 30
    assert "true_class" in df.columns
    assert "column_name" in df.columns


def test_evaluator_metrics_calculation(evaluator):
    res = evaluator.evaluate(sample_limit=50)

    assert "macro_precision" in res
    assert "macro_recall" in res
    assert "macro_f1" in res
    assert "per_class_metrics" in res
    assert "confusion_matrix" in res

    # Check bounds
    assert 0.0 <= res["macro_precision"] <= 1.0
    assert 0.0 <= res["macro_recall"] <= 1.0
    assert 0.0 <= res["macro_f1"] <= 1.0

    # Ensure all 5 classes are reported
    for cls_name in ["NAME", "EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID"]:
        assert cls_name in res["per_class_metrics"]
        m = res["per_class_metrics"][cls_name]
        assert "precision" in m
        assert "recall" in m
        assert "f1_score" in m
        assert "support" in m


def test_confusion_matrix_structure(evaluator):
    res = evaluator.evaluate(sample_limit=50)
    cm = res["confusion_matrix"]
    labels = res["confusion_matrix_labels"]
    assert len(labels) == 6  # 5 PII classes + NOT_PERSONAL
    assert len(cm) == 6
    assert len(cm[0]) == 6


def test_confusion_matrix_plot(evaluator):
    res = evaluator.evaluate(sample_limit=50)
    fig = evaluator.plot_confusion_matrix(res["confusion_matrix"], res["confusion_matrix_labels"])
    assert fig is not None
