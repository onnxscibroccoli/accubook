"""
Accubook core data layer.
Local-first CSV workspace. Feature-flagged. Owner-editable.
"""

import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import hashlib


class AccubookWorkspace:
    def __init__(self, root: str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.config_path = self.root / "config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {
            "enable_crews": False,
            "enable_inventory": False,
            "enable_recurring_services": True,
            "enable_change_orders": True,
            "enable_signatures": True,
            "enable_vehicles": False,
            "enable_measurements": False,
            "enable_pricebook": True,
            "field_order": ["customer", "property", "job_details", "lines", "photos", "signature"],
            "custom_fields": {},
            "onboarding_completed": False,
        }

    def save_config(self):
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)

    def feature_enabled(self, flag: str) -> bool:
        return self.config.get(flag, False)

    def _csv_path(self, name: str) -> Path:
        return self.root / f"{name}.csv"

    def load_csv(self, name: str) -> List[Dict[str, str]]:
        path = self._csv_path(name)
        if not path.exists():
            return []
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def save_csv(self, name: str, rows: List[Dict[str, Any]], fieldnames: Optional[List[str]] = None):
        path = self._csv_path(name)
        if not rows:
            return
        fieldnames = fieldnames or list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def pricebook_suggest(self, query: str, limit: int = 5) -> List[Dict]:
        if not self.feature_enabled("enable_pricebook"):
            return []
        pb = self.load_csv("pricebook")
        q = query.lower().strip()
        if not q:
            return []
        matches = []
        for item in pb:
            if q in item.get("item", "").lower() or q in item.get("trade_tag", "").lower():
                matches.append(item)
        return matches[:limit]

    def insert_pricebook_line(self, job_id: str, pricebook_id: str, qty: float = 1.0) -> Dict:
        pb = self.load_csv("pricebook")
        item = next((p for p in pb if p["id"] == pricebook_id), None)
        if not item:
            raise ValueError("Pricebook item not found")
        lines = self.load_csv("job_lines")
        next_order = max([int(l.get("order", 0)) for l in lines if l.get("job_id") == job_id], default=0) + 1
        new_line = {
            "id": str(int(datetime.now().timestamp() * 1000)),
            "job_id": job_id,
            "order": str(next_order),
            "description": item["item"],
            "qty": str(qty),
            "unit": item.get("unit", ""),
            "cost": item.get("cost", "0"),
            "sell_price": item.get("sell_price", "0"),
            "type": "billing",
            "source_pricebook_id": pricebook_id,
            "created": datetime.now().isoformat(),
        }
        lines.append(new_line)
        self.save_csv("job_lines", lines)
        return new_line

    def create_change_order(self, job_id: str, lines: List[Dict]) -> Dict:
        if not self.feature_enabled("enable_change_orders"):
            raise RuntimeError("Change orders disabled")
        cos = self.load_csv("change_orders")
        co_id = str(int(datetime.now().timestamp() * 1000))
        delta = sum(float(l.get("sell_price", 0)) * float(l.get("qty", 1)) for l in lines)
        co = {
            "id": co_id,
            "job_id": job_id,
            "status": "proposed",
            "delta_total": str(delta),
            "acknowledged_at": "",
            "signature_id": "",
            "created": datetime.now().isoformat(),
        }
        cos.append(co)
        self.save_csv("change_orders", cos)
        co_lines = self.load_csv("change_order_lines")
        for i, line in enumerate(lines):
            co_lines.append({
                "id": f"{co_id}-{i}",
                "change_order_id": co_id,
                "order": str(i + 1),
                **line,
            })
        self.save_csv("change_order_lines", co_lines)
        return co

    def acknowledge_change_order(self, co_id: str, signature_meta: Optional[Dict] = None):
        cos = self.load_csv("change_orders")
        for co in cos:
            if co["id"] == co_id:
                co["status"] = "acknowledged"
                co["acknowledged_at"] = datetime.now().isoformat()
                if signature_meta:
                    co["signature_id"] = signature_meta.get("id", "")
                break
        self.save_csv("change_orders", cos)

    def record_signature(self, entity_type: str, entity_id: str, signature_bytes: bytes, document_content: str, camera_frame_path: Optional[str] = None) -> Dict:
        if not self.feature_enabled("enable_signatures"):
            raise RuntimeError("Signatures disabled")
        sig_dir = self.root / "signatures" / entity_type
        sig_dir.mkdir(parents=True, exist_ok=True)
        sig_id = str(int(datetime.now().timestamp() * 1000))
        sig_path = sig_dir / f"{sig_id}.png"
        with open(sig_path, "wb") as f:
            f.write(signature_bytes)
        h = hashlib.sha256()
        h.update(document_content.encode())
        h.update(signature_bytes)
        meta = {
            "id": sig_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "path": str(sig_path.relative_to(self.root)),
            "timestamp": datetime.now().isoformat(),
            "hash": h.hexdigest(),
            "camera_frame": camera_frame_path or "",
        }
        metas = self.load_csv("signatures_meta")
        metas.append(meta)
        self.save_csv("signatures_meta", metas)
        return meta

    def set_next_due(self, job_id: str, interval_months: int):
        if not self.feature_enabled("enable_recurring_services"):
            return
        jobs = self.load_csv("jobs")
        for job in jobs:
            if job["id"] == job_id:
                job["next_service_due"] = (date.today().replace(day=1) + __import__("datetime").timedelta(days=30 * interval_months)).isoformat()
                job["recurring_interval_months"] = str(interval_months)
                break
        self.save_csv("jobs", jobs)

    def get_due_jobs(self) -> List[Dict]:
        if not self.feature_enabled("enable_recurring_services"):
            return []
        jobs = self.load_csv("jobs")
        today = date.today().isoformat()
        return [j for j in jobs if j.get("next_service_due") and j["next_service_due"] <= today]

    def reorder_lines(self, job_id: str, new_order: List[str]):
        lines = self.load_csv("job_lines")
        order_map = {lid: str(i + 1) for i, lid in enumerate(new_order)}
        for line in lines:
            if line.get("job_id") == job_id and line["id"] in order_map:
                line["order"] = order_map[line["id"]]
        self.save_csv("job_lines", lines)

    def search(self, query: str) -> Dict[str, List[Dict]]:
        q = query.lower()
        results = {"customers": [], "jobs": [], "lines": []}
        for c in self.load_csv("customers"):
            if any(q in str(v).lower() for v in c.values()):
                results["customers"].append(c)
        for j in self.load_csv("jobs"):
            if any(q in str(v).lower() for v in j.values()):
                results["jobs"].append(j)
        for ln in self.load_csv("job_lines"):
            if any(q in str(v).lower() for v in ln.values()):
                results["lines"].append(ln)
        return results


def demo():
    ws = AccubookWorkspace("/tmp/accubook-demo")
    print("Workspace ready. Features:", {k: ws.feature_enabled(k) for k in ["enable_pricebook", "enable_change_orders"]})
    suggestions = ws.pricebook_suggest("oil")
    print("Pricebook suggestions for 'oil':", suggestions)


if __name__ == "__main__":
    demo()
