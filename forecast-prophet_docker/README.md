# Sales Forecasting with Prophet

Leveraging Facebook's Prophet for time series forecasting in e-commerce, encapsulated within Docker for ease of use.

## Problem

In the dynamic world of e-commerce, understanding future sales dynamics is crucial for inventory management, marketing, and financial planning. Traditional forecasting methods can be complex, time-consuming, and often require advanced statistical knowledge.

## Idea

To provide a straightforward, "one-command" solution that automates sales data forecasting using Prophet, with the added capability to incorporate holidays and custom forecast periods, all within a Dockerized environment for simplicity and portability.

## Introduction

This project utilizes the Prophet library, developed by Facebook, to forecast time series data. It's designed to be user-friendly, handling data with strong seasonal effects and several seasons of historical data. The project is Dockerized, meaning all dependencies are packaged together, ensuring that it works seamlessly across different environments.

## How to Make It Work
**Docker ensures compatibility with Windows, Linux, and Mac**

0. Install [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).
1. Clone/download this repository and navigate to the project folder. [How?](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github/)
2. Copy `.env.example` to `.env` and configure the environment variables as needed (country for holidays, forecast period, etc.).
3. Place your sales data CSV in the `/data` directory, following the format as shown in `example.csv` (date and sales columns).
4. Execute `docker-compose up --force-recreate --build --remove-orphans` in the terminal within the project directory to build and start the services. [How?](https://www.groovypost.com/howto/open-command-window-terminal-window-specific-folder-windows-mac-linux/)
5. Allow some time for initialization, especially on the first run, as it sets up the necessary services.
6. The forecast results and visualizations will be available in the `/results` directory after the process completes.

## Outcomes

Upon successful execution, the project generates four key outputs in the `/results` directory:

1. `forecast_summary.csv`: A CSV file containing the essential forecast data, including dates and predicted sales, for easy reference and further analysis.
2. `forecast_full.csv`: A detailed CSV file providing an extensive forecast breakdown, including trends, seasonality components, and confidence intervals, offering deeper insights into the forecasted sales patterns.
3. `forecast.png`: A PNG visualization depicting the historical sales data alongside the forecasted sales, highlighting the model's predictions in the context of past performance.
4. `forecast_components.png`: A PNG file that breaks down the forecast into its components (trend, yearly seasonality, weekly seasonality, and holidays, if applicable), offering a comprehensive view of the factors influencing the forecast.

### Input Data Handling

- The system is designed to be flexible with input data formats. You can supply a CSV file with more than two columns in the `/data` directory; the system will automatically consider only the first two columns, assuming they represent date and sales figures, respectively.
- If your sales data is more granular than daily (e.g., hourly or transactional), the system will aggregate it to daily totals. This preprocessing step ensures that the forecast is generated at a daily level, making it applicable for a wide range of e-commerce planning needs.


### Some Technical Comments
- The project is structured to be modular, making it easy to integrate additional data sources or forecasting methods.
- Adjustments to service configurations can be made in the `docker-compose.yml` file.
- The system is designed for simplicity and ease of use, requiring minimal setup from the user's side.

## Conclusion

This project simplifies the process of sales forecasting in e-commerce, making advanced time series analysis accessible to non-experts. It's a practical tool for businesses looking to gain insights into future sales trends without delving into the complexities of statistical modeling. The Dockerized setup ensures a smooth and consistent user experience across different platforms.

