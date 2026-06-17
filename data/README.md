# Data Directory

## Structure

```
data/
├── raw/           ← Original CSV from dataset (gitignored if >50MB)
├── processed/     ← Cleaned Parquet + cached graph (gitignored)
└── mock/          ← 500-row mock CSV for dev without the full dataset ✅
```

## Files

| File | What it is | In git? |
|------|-----------|---------|
| `raw/violations.csv` | Full 298K-row dataset | ❌ gitignored (too large) |
| `processed/violations_clean.parquet` | Cleaned + CIS-scored | ❌ gitignored |
| `processed/blr_graph.pkl` | OSM road graph cache | ❌ gitignored |
| `mock/violations_mock.csv` | 500-row synthetic mock | ✅ committed |

## Getting the Real Data

1. Download the dataset CSV from the hackathon portal.
2. Place it at `data/raw/violations.csv`.
3. Run the EDA notebook: `notebooks/01_eda.ipynb`
4. Cleaned Parquet will be written to `data/processed/`.

## Mock Data

`mock/violations_mock.csv` is always available for local development.
The backend auto-loads it if no Parquet file is found.
