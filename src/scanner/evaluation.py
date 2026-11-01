"""
scanner/evaluation.py
Performance Evaluation and Benchmark Engine for PS-019.

Calculates Per-class and Macro-averaged Precision, Recall, and F1-score
against the manually labelled test dataset.
Generates confusion matrices, false positive / negative diagnostics,
and performance charts.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from .detection import PersonalDataDetector, DetectionResult
from .csv_scanner import CSVScanner
from .sqlite_scanner import SQLiteScanner


class Evaluator:
    """
    Evaluates detector predictions against ground-truth labels.
    """

    PREDEFINED_CLASSES = ["NAME", "EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID"]
    ALL_EVAL_CLASSES = PREDEFINED_CLASSES + ["NOT_PERSONAL"]

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = Path(data_dir) if data_dir else (Path(__file__).resolve().parent.parent / "data")
        self.ground_truth_path = self.data_dir / "labelled_test_data.csv"
        self.detector = PersonalDataDetector()
        self.csv_scanner = CSVScanner(detector=self.detector)
        self.sqlite_scanner = SQLiteScanner(detector=self.detector)

    def load_ground_truth(self) -> pd.DataFrame:
        """Loads and validates the manually labelled benchmark dataset."""
        if not self.ground_truth_path.exists():
            raise FileNotFoundError(f"Labelled test dataset not found at {self.ground_truth_path}")
        df = pd.read_csv(self.ground_truth_path)
        required_cols = ["source_type", "source_name", "table_name", "column_name", "true_class"]
        for c in required_cols:
            if c not in df.columns:
                raise ValueError(f"Labelled test dataset missing required column: '{c}'")
        df["table_name"] = df["table_name"].fillna("").astype(str)
        return df

    def run_benchmark_scan(self, sample_limit: int = 100) -> Dict[Tuple[str, str, str, str], DetectionResult]:
        """
        Scans all test files and SQLite tables present in data_dir,
        returning a map of (source_type, source_name, table_name, column_name) -> DetectionResult.
        """
        predictions_map: Dict[Tuple[str, str, str, str], DetectionResult] = {}

        # 1. Scan synthetic CSVs
        for csv_filename in ["customers.csv", "employees.csv", "support_tickets.csv"]:
            csv_path = self.data_dir / csv_filename
            if csv_path.exists():
                results = self.csv_scanner.scan_file(csv_path, sample_limit=sample_limit)
                for res in results:
                    key = ("csv", csv_filename, "", res.column_name)
                    predictions_map[key] = res

        # 2. Scan synthetic SQLite database
        db_path = self.data_dir / "privacy_demo.db"
        if db_path.exists():
            tables = self.sqlite_scanner.discover_tables(db_path)
            for tbl in tables:
                results = self.sqlite_scanner.scan_table(db_path, tbl, sample_limit=sample_limit)
                for res in results:
                    key = ("sqlite", "privacy_demo.db", tbl, res.column_name)
                    predictions_map[key] = res

        return predictions_map

    def evaluate(self, sample_limit: int = 100) -> Dict[str, Any]:
        """
        Performs full benchmark evaluation:
        1. Compares predictions against ground truth
        2. Computes per-class & macro Precision, Recall, F1
        3. Generates confusion matrix and error instances (FP, FN)
        """
        gt_df = self.load_ground_truth()
        preds_map = self.run_benchmark_scan(sample_limit=sample_limit)

        y_true: List[str] = []
        y_pred: List[str] = []
        detailed_records: List[Dict[str, Any]] = []

        false_positives: List[Dict[str, Any]] = []
        false_negatives: List[Dict[str, Any]] = []

        for _, row in gt_df.iterrows():
            source_type = str(row["source_type"]).strip()
            source_name = str(row["source_name"]).strip()
            table_name = str(row["table_name"]).strip()
            col_name = str(row["column_name"]).strip()
            true_cls = str(row["true_class"]).strip()

            key = (source_type, source_name, table_name, col_name)
            pred_res = preds_map.get(key)

            if pred_res:
                pred_cls = pred_res.detected_class or "NOT_PERSONAL"
                conf = pred_res.confidence_score
                evidence = pred_res.evidence_details
                is_ambig = pred_res.is_ambiguous
            else:
                pred_cls = "NOT_PERSONAL"
                conf = 0.0
                evidence = "Field not observed during scan"
                is_ambig = False

            y_true.append(true_cls)
            y_pred.append(pred_cls)

            is_correct = (true_cls == pred_cls)

            record = {
                "source_type": source_type,
                "source_name": source_name,
                "table_name": table_name,
                "column_name": col_name,
                "true_class": true_cls,
                "predicted_class": pred_cls,
                "confidence_score": conf,
                "is_correct": is_correct,
                "is_ambiguous": is_ambig,
                "evidence": evidence
            }
            detailed_records.append(record)

            # Categorize errors
            if not is_correct:
                if true_cls == "NOT_PERSONAL" and pred_cls != "NOT_PERSONAL":
                    false_positives.append({
                        **record,
                        "error_type": "False Positive (Non-PII flagged as PII)",
                        "reason": f"Non-personal field '{col_name}' was falsely flagged as {pred_cls} with confidence {conf:.2f}."
                    })
                elif true_cls in self.PREDEFINED_CLASSES and pred_cls == "NOT_PERSONAL":
                    false_negatives.append({
                        **record,
                        "error_type": "False Negative (PII missed)",
                        "reason": f"Ground-truth PII field '{col_name}' ({true_cls}) was missed (classified as NOT_PERSONAL)."
                    })
                else:
                    # Class confusion between two PII classes
                    false_positives.append({
                        **record,
                        "error_type": f"Class Confusion (Misclassified as {pred_cls})",
                        "reason": f"True {true_cls} field '{col_name}' was categorized as {pred_cls}."
                    })

        # Calculate metrics safely
        labels = self.PREDEFINED_CLASSES
        per_class_metrics: Dict[str, Dict[str, Any]] = {}

        for cls_name in labels:
            # Binary one-vs-rest per class
            bin_true = [1 if yt == cls_name else 0 for yt in y_true]
            bin_pred = [1 if yp == cls_name else 0 for yp in y_pred]

            support = sum(bin_true)
            pred_count = sum(bin_pred)

            p = precision_score(bin_true, bin_pred, zero_division=0)
            r = recall_score(bin_true, bin_pred, zero_division=0)
            f1 = f1_score(bin_true, bin_pred, zero_division=0)

            # True positives
            tp = sum(1 for bt, bp in zip(bin_true, bin_pred) if bt == 1 and bp == 1)
            fp = sum(1 for bt, bp in zip(bin_true, bin_pred) if bt == 0 and bp == 1)
            fn = sum(1 for bt, bp in zip(bin_true, bin_pred) if bt == 1 and bp == 0)

            status_note = ""
            if support == 0 and pred_count == 0:
                status_note = "Class not present in ground truth or predictions."
            elif support == 0:
                status_note = "No ground truth instances; positive predictions represent false alarms."
            elif pred_count == 0:
                status_note = "Scanner made zero positive predictions for this class."

            per_class_metrics[cls_name] = {
                "precision": round(float(p), 4),
                "recall": round(float(r), 4),
                "f1_score": round(float(f1), 4),
                "support": int(support),
                "predicted_count": int(pred_count),
                "true_positives": int(tp),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "status_note": status_note
            }

        # Macro averages across the 5 predefined classes
        macro_prec = float(np.mean([m["precision"] for m in per_class_metrics.values()]))
        macro_rec = float(np.mean([m["recall"] for m in per_class_metrics.values()]))
        macro_f1 = float(np.mean([m["f1_score"] for m in per_class_metrics.values()]))

        # Binary PII vs Non-PII overall metrics
        bin_overall_true = [1 if yt != "NOT_PERSONAL" else 0 for yt in y_true]
        bin_overall_pred = [1 if yp != "NOT_PERSONAL" else 0 for yp in y_pred]

        overall_pii_precision = round(float(precision_score(bin_overall_true, bin_overall_pred, zero_division=0)), 4)
        overall_pii_recall = round(float(recall_score(bin_overall_true, bin_overall_pred, zero_division=0)), 4)
        overall_pii_f1 = round(float(f1_score(bin_overall_true, bin_overall_pred, zero_division=0)), 4)

        # Confusion Matrix across all 6 classes
        conf_labels = self.ALL_EVAL_CLASSES
        cm = confusion_matrix(y_true, y_pred, labels=conf_labels)

        return {
            "total_evaluated_fields": len(detailed_records),
            "macro_precision": round(macro_prec, 4),
            "macro_recall": round(macro_rec, 4),
            "macro_f1": round(macro_f1, 4),
            "overall_pii_precision": overall_pii_precision,
            "overall_pii_recall": overall_pii_recall,
            "overall_pii_f1": overall_pii_f1,
            "per_class_metrics": per_class_metrics,
            "confusion_matrix": cm.tolist(),
            "confusion_matrix_labels": conf_labels,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "detailed_records": detailed_records
        }

    @staticmethod
    def plot_confusion_matrix(cm_data: List[List[int]], labels: List[str]):
        """
        Generates a clean Matplotlib figure of the confusion matrix.
        Returns the matplotlib.figure.Figure object.
        """
        import matplotlib.pyplot as plt

        cm_arr = np.array(cm_data)
        fig, ax = plt.subplots(figsize=(7, 5.5))
        cax = ax.matshow(cm_arr, cmap="Blues", alpha=0.85)

        # Add text values
        for i in range(cm_arr.shape[0]):
            for j in range(cm_arr.shape[1]):
                val = cm_arr[i, j]
                ax.text(
                    j, i, str(val),
                    va="center", ha="center",
                    color="white" if val > (cm_arr.max() / 2) else "black",
                    fontweight="bold"
                )

        fig.colorbar(cax)
        short_labels = [l.replace("_NUMBER", "_NO").replace("GOVERNMENT_", "GOVT_") for l in labels]
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(short_labels, rotation=45, ha="left", fontsize=9)
        ax.set_yticklabels(short_labels, fontsize=9)
        ax.set_xlabel("Predicted Class", fontweight="bold", labelpad=10)
        ax.set_ylabel("Ground Truth Class", fontweight="bold")
        ax.set_title("Detection Confusion Matrix", fontweight="bold", pad=20)
        plt.tight_layout()
        return fig
