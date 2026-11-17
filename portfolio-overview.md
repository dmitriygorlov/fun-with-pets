# Portfolio overview

This catalog describes checked-in implementations, not future improvements. All seven projects are personal work. Evaluation methods in the [README](README.md) are proposed, not measured outcomes.

## Recommendations: limited experiment

[Training](ecom-recs-for-email_docker/scripts/train.py) reads the first two columns of `files/client_item.csv` as customer and item IDs, builds unweighted interactions and trains LightFM with WARP loss. [Prediction](ecom-recs-for-email_docker/scripts/predict.py) reads the first column of `clients.csv` and `items.csv`, and the first two columns of `exclude.csv`, to retrieve candidates and exclude purchases. Inputs are under [files](ecom-recs-for-email_docker/files/).

Output: `results/predict_clients_items_rank.csv` with `client_id`, `item_id`, `rank`; embeddings and mappings go under `mappings_embeddings/`. [Settings](ecom-recs-for-email_docker/settings.py) request up to 10 recommendations after filtering, not a guarantee of 10 items per customer.

Source-review limits: the DataFrame mask can retain unknown IDs as missing values; squeezing a single target can change its shape. No temporal holdout, popularity baseline, cold-start policy or online evaluation is implemented. Check IDs, exclusions and output coverage before evaluating ranking quality. This module was not changed for the catalog.

## Sales analytics: local example

[ABC](auto-sales-analytics_docker/scripts/abc_analysis.py) multiplies `product_price` by `quantity`, aggregates by `product_id`, sorts by revenue and assigns categories at cumulative percentages of 80 and 95. A product crossing a boundary goes into the next category. [XYZ](auto-sales-analytics_docker/scripts/xyz_analysis.py) computes the coefficient of variation of transaction revenue per product and uses the 33rd and 66th percentiles to classify products. This is not regular-period demand variability.

The [sample CSV](auto-sales-analytics_docker/data/sales.csv) is included; no commercial representativeness or provenance is asserted. The writer produces `ABC.xlsx` and `XYZ.xlsx`, each with statistics and classification sheets.

From the repository root in PowerShell with Python available:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r auto-sales-analytics_docker/requirements.txt
New-Item -ItemType Directory -Force local-results | Out-Null
@'
import sys
sys.path.insert(0, 'auto-sales-analytics_docker')
from scripts.abc_analysis import perform_abc
from scripts.xyz_analysis import perform_xyz
from scripts._common import save_to_excel
for name, analyze in [('ABC', perform_abc), ('XYZ', perform_xyz)]:
    save_to_excel(analyze('auto-sales-analytics_docker/data/sales.csv'), name, 'local-results/')
'@ | .\.venv\Scripts\python -
```

This calls existing functions with a local output directory; `main.py` uses container paths. Outputs are local artifacts, not committed portfolio results.

## Forecasting: learning prototype

[Preparation](forecast-prophet_docker/scripts/data_preparation.py) reads the first two CSV columns as date and sales, renames them `ds` and `y`, and sums sales by observed date. [Training](forecast-prophet_docker/scripts/model_training.py) fits Prophet with country holidays. The [example configuration](forecast-prophet_docker/.env.example) supplies the input path, country and horizon.

[Export](forecast-prophet_docker/scripts/forecasting.py) writes `results/forecast_summary.csv` (date and rounded prediction) and `results/forecast_full.csv` (including components). Both include historical dates as well as the future horizon. [Visualization](forecast-prophet_docker/scripts/visualization.py) writes `forecast.png` and `forecast_components.png`. These are output paths, not supplied demo artifacts.

No rolling backtest, baseline comparison or accuracy report is present. Missing calendar days are not filled: zero-sales days and missing observations need separate treatment. Image export depends on Plotly/Kaleido runtime requirements; container execution was not verified here.

## Container entry points

The commands match checked-in paths, Compose services and Dockerfile entry points. They are **source-checked instructions, not successful container-run claims**. Docker's client and Compose were available, but the Linux daemon was unavailable. Dependencies are not fully locked across the repository.

Run each block independently from the repository root, with Docker running:

```powershell
cd auto-sales-analytics_docker
docker compose up --build --abort-on-container-exit
```

```powershell
cd ecom-recs-for-email_docker
docker compose up --build --abort-on-container-exit
```

```powershell
cd forecast-prophet_docker
# Only copy if you do not already have .env; review its settings before running.
Copy-Item .env.example .env
docker compose up --build --abort-on-container-exit
```

Compose mounts input and output directories. Review the recommendation limitations before attempting that pipeline.

For the [probability visualizer](probability-endurance_streamlit/main.py):

```powershell
cd probability-endurance_streamlit
docker build -t probability-endurance .
docker run --rm -p 8501:8501 probability-endurance
```

The Dockerfile exposes port 8501. Hosted demo availability was not verified. Use `0 < p < 1`: the current 95%-threshold calculation fails at 0 and 1; fractional input can also exceed 1.

The [translation](Is-it-simple_bot/README.md), [GPT bot](gpt_helper_bot/README.md) and [Airflow](jokes-aside_airflow/README.md) instructions are integration references, not verified quick starts. They require external services and credentials; no messages or emails were sent during review. The translation folder's exact case is `Is-it-simple_bot`. The GPT bot logs passwords and prompts and uses a legacy API call; it is not a secure production assistant. Airflow requires the `jokes_conn` database connection and email configuration.

## Verification record

Review baseline: `7fb0f48322976d8189b1b009e982b7b8d84b53c8`.

- Inspected all seven project entry points and commerce processing code; no repository `AGENTS.md` was present.
- Ran the sales walkthrough's function calls on the supplied CSV in an isolated Python 3.13 environment (pandas 3.1.1, NumPy 2.5.5, SciPy 1.18.1, openpyxl 3.1.5), with outputs outside the checkout. Both Excel files were written and read back; sheet names, product coverage and classification counts matched, and ABC revenue reconciled to the input. This checks sample execution, not business effectiveness or the Python 3.10 container.
- All relative links and heading anchors in these two documents passed local checks. Sales and recommendation Compose configurations passed `docker compose ... config --quiet`, with warnings about the obsolete `version` key.
- Container execution, external services, hosted demos and business impact were not verified.

A **local example** exercises analytical functions on supplied input; a **learning prototype** implements a workflow without outcome validation; a **limited experiment** additionally has concrete integration or input-handling constraints. None implies production readiness.
