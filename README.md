# SymptomX (Remade from Scratch)

- Offline, private, zero external downloads
- Minimal deps (Flask only)
- Clean UI with Dark Mode toggle
- Robust fallback (never shows "service unavailable")

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open the URL shown (e.g., http://127.0.0.1:5000).

## Data
Put your dataset at `data/diseases.json` (recommended). Each entry can have:
```json
{
  "disease": "Flu",
  "symptoms": "fever, cough, sore throat",
  "treatment": "rest, fluids"
}
```
Or include `normalized_symptoms_list` as an array; it will be used directly.
If no file is present, a small built-in set is used automatically.
