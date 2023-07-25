# Auto Sales Analysis

Example of some easy auto sales analysis with docker

## Problem 
Each business have it's own sales data and each business want to know more about it's customers and make more money. But not all businesses have data scientists or even programmers or doesn't want to share data with third parties. So, how to make some easy analysis on your own data without NDA break?

## Idea
Make "one command" solution for some easy analysis on your own data without NDA break.

## Introduction

## How make it work
**Thanks to docker, it works on both Windows and Linux or Mac**

0. Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/) ~~and love it~~
1. Clone/download the repository and navigate to the project folder. [How?](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github/)
2. Change file `sales` in the `data` folder to your sales report:
   - Please use this columns names and order: order_id, customer_id, product_id, date_order, product_price, quantity
3. Run `docker-compose up --force-recreate --build --remove-orphans` in terminal to build the Docker image and make excel files with analysis of your sales data. You need to run the script in the terminal while in the folder. [How?](https://www.groovypost.com/howto/open-command-window-terminal-window-specific-folder-windows-mac-linux/)
4. Wait a little bit, have a coffee (this may take a while, depending on the size of your data, but generally less than 5 minutes)
5. Main result file will be saved in the results folder wwith different names, depending on the type of analysis.
6. You are amazing <3


### Some technic comments
- For example there are `sales.csv` with 100 000 rows of sales data in the `data` folder.
- You can modify the `docker-compose.yml` file to change names of files.
- If you want to run the project without using Docker, you can install the required packages and run python `main.py`.


## Conclusion
This project provides a simple example of how to make some easy analysis on your own data without NDA break. It can be used as a template for more complex analysis.
