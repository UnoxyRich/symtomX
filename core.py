# core.py — brand new, offline, pure-Python diagnosis core
from __future__ import annotations
import json, os, logging, re
from typing import List, Dict, Any, Tuple

# Logging
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "core.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("core")

class SymptomCore:
    """Self-contained diagnosis without external downloads.

    - Loads diseases from data/diseases.json (or CSV fallback) if present.

    - If no data found, uses a tiny built-in set so the app always works.

    - Scores via token/phrase overlap; returns deterministic results.

    """
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.diseases: List[Dict[str, Any]] = []
        self.vocab: List[str] = []
        self._load_data()

    def _load_data(self) -> None:
        # Priority: diseases.json -> diseases.csv -> built-in sample
        json_path = os.path.join(self.data_dir, "diseases.json")
        csv_path  = os.path.join(self.data_dir, "diseases.csv")
        loaded = False
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list) and data:
                    self.diseases = self._normalize(data)
                    loaded = True
                    logger.info("Loaded %d diseases from %s", len(self.diseases), json_path)
            except Exception as e:
                logger.error("Failed to parse %s: %s", json_path, e)
        if not loaded and os.path.exists(csv_path):
            try:
                # Simple CSV reader without pandas
                import csv
                rows = []
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for r in reader:
                        rows.append(r)
                if rows:
                    self.diseases = self._normalize(rows)
                    loaded = True
                    logger.info("Loaded %d diseases from %s", len(self.diseases), csv_path)
            except Exception as e:
                logger.error("Failed to parse %s: %s", csv_path, e)
        if not loaded:
            # Built-in minimal fallback (always available)
            self.diseases = self._normalize([
                {
                    "disease": "Common Cold",
                    "symptoms": "sneezing, runny nose, sore throat, mild cough, congestion",
                    "treatment": "rest, hydration, decongestants, throat lozenges"
                },
                {
                    "disease": "Influenza (Flu)",
                    "symptoms": "fever, dry cough, sore throat, headache, muscle aches, fatigue",
                    "treatment": "rest, fluids, OTC pain relievers; antivirals when prescribed"
                },
                {
                    "disease": "Migraine",
                    "symptoms": "headache, nausea, light sensitivity, sound sensitivity, aura",
                    "treatment": "rest in dark room, hydration, triptans/NSAIDs per guidance"
                }
            ])
            logger.warning("Using built-in fallback dataset: %d diseases", len(self.diseases))
        self._build_vocab()

    def _normalize(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normed = []
        for row in items:
            disease = str(row.get("disease") or row.get("name") or "Unknown").strip()
            treatment = str(row.get("treatment") or row.get("care") or "").strip()
            if isinstance(row.get("normalized_symptoms_list"), list):
                syms = [str(x).strip().lower() for x in row["normalized_symptoms_list"] if str(x).strip()]
            else:
                text = str(row.get("symptoms_normalized") or row.get("symptoms") or "").lower()
                parts = [s.strip() for s in re.split(r",|;|/|\n", text) if s.strip()]
                syms = parts if parts else ([w.strip() for w in re.split(r"\s+", text) if w.strip()] if text else [])
            normed.append({"disease": disease, "treatment": treatment, "normalized_symptoms_list": syms})
        return normed

    def _build_vocab(self) -> None:
        seen = set()
        vocab = []
        for row in self.diseases:
            for p in row.get("normalized_symptoms_list", []):
                if p and p not in seen:
                    seen.add(p); vocab.append(p)
        self.vocab = vocab
        logger.info("Vocab built: %d phrases", len(self.vocab))

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        text = (text or "").lower()
        # phrases are matched with substring containment; tokens are used for light weight scoring
        tokens = re.findall(r"[a-z0-9]+(?:'[a-z0-9]+)?", text)
        return tokens

    def diagnose(self, user_text: str, top_k: int = 5) -> Dict[str, Any]:
        """Return a dict with primary + others. Never raises for normal inputs."""
        user_text = (user_text or "").strip()
        if not user_text:
            return {"primary": None, "possible": [], "message": "Please enter your symptoms."}

        utext = user_text.lower()
        tokens = set(self._tokenize(utext))

        scored: List[Tuple[float, Dict[str, Any], List[str]]] = []
        for row in self.diseases:
            phrases = [p for p in row.get("normalized_symptoms_list", []) if p]
            # phrase hits (substring match) + token overlap
            phrase_hits = [p for p in phrases if p in utext]
            token_hits = [t for t in tokens if any(t in p or p in t for p in phrases)]
            # score: weighted combo of phrase hits and token hits, normalized
            ph = len(phrase_hits)
            th = len(set(token_hits))
            denom = max(len(phrases), 1)
            score = (0.7 * (ph / denom)) + (0.3 * (th / (len(tokens) or 1)))
            scored.append((score, row, phrase_hits))
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:max(1, top_k)]

        def to_item(score: float, row: Dict[str, Any], hits: List[str]) -> Dict[str, Any]:
            return {
                "disease": row.get("disease", "Unknown"),
                "treatment": row.get("treatment", ""),
                "confidence": round(100.0 * max(0.0, min(1.0, score)), 1),
                "matched": hits
            }
        items = [to_item(s, r, h) for (s, r, h) in top]
        primary = items[0] if items else None
        return {"primary": primary, "possible": items[1:]}
