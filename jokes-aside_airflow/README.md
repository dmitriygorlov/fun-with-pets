# Airflow Jokes Pipeline

Automating the retrieval, storage, and distribution of jokes using Apache Airflow with Docker.

## Problem 

In a world full of data, everyone loves a moment of laughter. However, manually searching for jokes, storing them, and sharing with friends can be tedious. Additionally, setting up a data pipeline can be daunting for those without extensive coding experience or those new to Apache Airflow.

## Idea

Create a "one command" solution that automates the process of fetching a random joke, storing it in a database, and sharing it via email, all packaged in a Docker environment.

## Introduction

This project uses Apache Airflow to set up a workflow that automatically fetches a joke from a public API, stores it in a PostgreSQL database, and then sends it out by email. Docker-compose is used to simplify the setup and execution of Airflow and PostgreSQL.

## How to Make It Work
**Thanks to Docker, it works on both Windows, Linux, and Mac**

0. Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).
1. Clone/download the repository and navigate to the project folder. [How?](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github/)
2. Copy `.env.example` to `.env` and adjust the environment variables (SMTP settings for email sending, etc.) as needed.
3. Run `docker-compose up --force-recreate --build --remove-orphans` in terminal to build and start the services. You need to run the command in the terminal while in the project folder. [How?](https://www.groovypost.com/howto/open-command-window-terminal-window-specific-folder-windows-mac-linux/)
4. Give it a moment to initialize, especially on the first run, as it sets up the services.
5. Access the Airflow UI by visiting `http://localhost:8080` in your web browser, and you'll see the DAG for the jokes pipeline.
6. Trigger the DAG and then check the email of the recipient specified in the DAG file to see the joke.

### Some Technical Comments
- The project is set up in a modular way, so it's easy to add more tasks or change the data source.
- You can modify the `docker-compose.yml` file to change service settings.
- If you want to run the project without using Docker, you would need to set up an Airflow environment, PostgreSQL, and set the necessary environment variables or connections in Airflow.

## Conclusion

This project provides an easy way to get started with Apache Airflow while enjoying a bit of humor. It serves as a practical introduction to setting up data pipelines in Airflow, and can be expanded or modified for more serious applications. All this is done while ensuring a smooth setup process through Docker.
