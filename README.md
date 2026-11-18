# Fun With Pets — Applied / Product Data Science

Personal projects by Dmitriy Gorlov: turning a business question into an analytical output and defining how to evaluate it. Start with product selection, assortment analysis and sales planning below.

These are independent pet projects and learning experiments, not client engagements or production deployments. No measured revenue lift or online experiment results are claimed. Online evaluation methods below are proposed checks. The recommendation benchmark reports reproducible synthetic offline metrics, not business impact.

## Commerce projects

| Project / question | Input → implemented output | Current limits | How to check usefulness |
| --- | --- | --- | --- |
| [Email recommendations](ecom-recs-for-email_docker/) — which products might interest a customer? | Timestamped synthetic purchases → popularity/co-purchase comparison and ranked CSV; a separate legacy path trains LightFM. Neither sends email. | Offline example has temporal evaluation and cold-user fallback; its tiny designed data do not validate LightFM quality or business impact. | Inspect the reproducible Precision/Recall/NDCG@K and coverage report; validate on real temporal windows before a randomized campaign test with unsubscribe guardrails. |
| [Sales analytics](auto-sales-analytics_docker/) — which products contribute revenue and how variable are their transactions? | Product ID, unit price and quantity → ABC contribution and XYZ variation tables in Excel. | Local analytical example. XYZ uses transaction revenue variation, not regular-period demand; thresholds depend on this dataset. | Reconcile revenue and product counts. Before inventory use, aggregate regular periods and compare stockouts and inventory cost against the current policy. |
| [Sales forecasting](forecast-prophet_docker/) — what sales trajectory could inform planning? | Date and sales CSV, country and horizon → Prophet forecast CSVs and plots. | Learning prototype: no backtest or baseline; missing dates are not filled. | Rolling time splits against a seasonal-naive baseline; compare MAE and bias, then the cost of over/under-planning. |

See the [portfolio overview](portfolio-overview.md) for exact inputs, outputs, commands and verification boundaries.

## Other experiments

| Project | Input → output / purpose | Limits and proposed check |
| --- | --- | --- |
| [Probability visualizer](probability-endurance_streamlit/) | Probability and trial count → curve for at least one success, `1 - (1-p)^n`. | Educational prototype assuming independent trials and constant probability. Boundary inputs are validated; offline UI tests cover zero, one and invalid fractions. Check formula and comprehension, not real-world success predictions. |
| [Translation bot](Is-it-simple_bot/) | Telegram text → Russian → Turkish → Russian translation. | Limited external-service experiment. Round-trip similarity is not translation quality; use human review of representative phrases. |
| [GPT helper bot](gpt_helper_bot/) | Telegram prompts → API responses, conversation history and usage records. | Limited integration experiment with async API calls and no password/prompt logging. Local history still contains sensitive text; review data retention; evaluate task completion and cost on a fixed prompt set. |
| [Airflow jokes pipeline](jokes-aside_airflow/) | Public joke API → PostgreSQL → email task. | Educational orchestration prototype requiring database/email configuration. Check retries, duplicates and delivery in a controlled environment. |

## Start here

Use the [local sales walkthrough](portfolio-overview.md#sales-analytics-local-example) for a small example, or inspect the [container entry points](portfolio-overview.md#container-entry-points). Each project has independent dependencies; there is no shared platform or universal setup command.

[MIT license](LICENSE)
