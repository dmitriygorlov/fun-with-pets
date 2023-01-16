# Easy recommendation system for e-commerce e-mail campaigns

Example of some business usefull ML project for e-commercs

## Problem 
Each online store has a sales history and almost all of them want tocommunicate with the client (for example, through e-mail campaigns). 

## Idea
Make an easy item recommendation system even for a person with zero programming knowledge

## Introduction
This project is a simple system for recommending items for clients for e-commerce e-mail campaigns. It uses a LightFM model to learn the client-item interactions from a sales data, and then recommends items for each client based on their nearest neighbors in the item embedding space. The system also allows for exclusion of previously purchased items, and returns a specified number of top recommendations for each client.

## How make it work
**Thanks to docker, it works on both Windows and Linux or Mac**

0. Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/) ~~and love it~~
1. Clone/download the repository and navigate to the project folder. [How?](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github/)
2. Change files in the `files` folder to your data:
   - Place your sales data as `client_item.csv`. The file should contain two columns, `client_id` and `item_id`, representing the clients and items respectively.
   - Place your clients for prediction as `clients.csv`. The file should contain one column, `client_id`, representing the clients. There may be fewer customers than in the sales file, but they must have the same id system. For clients missing in the sales file, predictions will not be made (system does,'t work with [cold start problem](https://en.wikipedia.org/wiki/Cold_start_(recommender_systems))
   - Place your items for prediction as `items.csv`. The file should contain one column, `item_id`, representing the items. There may be fewer items than in the sales file (for example, you can take only relevant files in stock)
   - Place your data for exclude from final recomendation as `exclude.csv`. The file should contain two columns, `client_id` and `item_id`, representing the clients and items respectively. As this file, you can copy a file with sales (we do not want to recommend customers already purchased items) or any other list with specific "anti" preferences.
3. Run `docker-compose up --force-recreate --build --remove-orphans` in terminal to build the Docker image and make recomendations. You need to run the script in the terminal while in the folder. [How?](https://www.groovypost.com/howto/open-command-window-terminal-window-specific-folder-windows-mac-linux/)
4. Wait a little bit, have a coffee (this may take a while, depending on the size of your data, but generally less than 30 minutes)
5. Main result file will be saved in the results folder with the name `predict_clients_items_rank.csv`. It contains `client_id` and `item_id` and `rank` from most recomended (1) to less. Some more results:
   - Logs are saved in `logs` folder
   - Embeddings and mappings from trained [LightFM](https://making.lyst.com/lightfm/docs/lightfm.html) model are saved in `mappings_embeddings` folder
6. Use data for e-mails or any other direct marketing 
7. You are amazing <3


### Some technic comments
- For example there are `client_item.csv` with 1 000 000 rows, `clients.csv` with 100 000, `items.csv` with 10 000, and `exclude.csv` as copy of `client_item.csv`.
- That is easy project, so model use only sales as iteractions without any features or custom weights and doesn't work for unknown clients/items.
- You can modify the `settings.py` file to adjust the parameters of the model and the number of recommendations.
- You can modify the `docker-compose.yml` file to change names of files.
- The `main.py` script loads the data, trains and saves the model, makes recommendations and saves the results.
- The `scripts` folder contains helper functions for data loading, recommendations and filtering.
- The `Dockerfile` and `docker-compose.yml` files are provided for running the project in a Docker container.
- If you want to run the project without using Docker, you can install the required packages and run python `main.py`.


## Conclusion
This project provides a simple yet effective way to generate item recommendations for e-commerce clients. It can easily be adapted to work with different types of data and can be extended to include other recommendation techniques or features. The use of Docker ensures a consistent environment and easy deployment. You can use this project as a starting point for your own recommendation system, and experiment with different parameters and models to improve the recommendations.

