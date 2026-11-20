# Stat-Project-TCG — TCGA-BRCA

Reproducible notebooks for Phase 1 and Phase 2 of the Statistics course project (Path B). The project uses clinical data and one prespecified RNA-expression feature at the patient level.

## Setup

1. Clone the repository.
2. Create an environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Put the source data files in `data/` as described in [`data/README.md`](data/README.md). Data files are intentionally excluded from Git.
4. Launch Jupyter from the repository root: `jupyter notebook`.
5. Run `notebooks/phase1.ipynb` from top to bottom, then `notebooks/phase2.ipynb`.

## Reproducibility notes

- All paths are repository-relative; no `E:\...` paths are used.
- Phase 1 maps TCGA sample/case barcodes to the 12-character patient barcode and explicitly aggregates repeated records/samples.
- The same selected gene (`A1BG_RNA` by default) is used in both phases. Change it only once and consistently in both notebooks.
- Phase 2's binomial exercise is an IID Bernoulli model-based simulation, not a partition of one shuffled finite cohort.
- Figures are saved under `figures/phase1/` and `figures/phase2/`; intermediate patient-level output is written to ignored `processed/`.

## Current limitation

The source data are not included. The numerical outputs and final report claims must be regenerated/verified after the original data are placed in `data/`. Record the exact source URL, release and download date before final submission.


## Molecular identifier troubleshooting

Phase 1 now selects the molecular identifier column by counting actual TCGA barcode matches, rather than choosing the first column whose name contains `id`. If no candidate contains a TCGA barcode, the notebook stops and prints sample values from candidate columns. Do not proceed to Phase 2 until the molecular-to-clinical patient join has a non-zero cohort and the identifier mapping has been verified.

Run notebooks from top to bottom after restarting the kernel. The join and descriptive-statistics cells now raise explicit errors if upstream variables are missing.


## Stage-conflict policy (Phase 1)

Blank values and explicit placeholders (`--`, `-`, `Unknown`, `Not Reported`, etc.) are treated as missing. The patient-level binary stage group is assigned only when all valid recorded stages for that patient agree on the Early/Advanced group. If valid records span both groups, `stage_group` is left missing and the conflict is listed in `processed/phase1_stage_conflicts.csv`. This avoids resolving clinically meaningful conflicts by an arbitrary mode.
