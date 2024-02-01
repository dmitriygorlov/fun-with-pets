# Probability Endurance Visualizer

Visualizing the cumulative success probability with increasing attempts, inspiring persistence through an interactive Streamlit app.

## Problem

In endeavors like job applications or dating, initial success rates can be discouragingly low, making it easy to overlook the power of persistence. Understanding the statistical likelihood of success through repeated attempts can be abstract and non-intuitive.

## Idea

Develop an interactive tool that visually and numerically demonstrates how repeated efforts increase the overall probability of success, even if the chance of success in any single attempt is low. The tool aims to motivate users by quantitatively showing the benefits of perseverance.

## Introduction

This project utilizes Python, Streamlit, and Plotly to create an engaging web application that allows users to input their success rate for a single attempt and the number of attempts they're willing to make. The app then calculates and visually displays the cumulative probability of achieving at least one success across those attempts, reinforcing the message that "if at first you don't succeed, try, try again."

## How to Make It Work

### Via Streamlit live demo
**No installation required.**
Just visit the [live demo]() to access the Streamlit app.

### Locally with Docker
**Docker ensures it works seamlessly across different environments.**
0. Install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).
1. Clone/download the repository and navigate to the project folder. [How?](https://sites.northwestern.edu/researchcomputing/resources/downloading-from-github/)
2. Build the Docker image and run the container by running `docker build -t fortis-fortuna-adiuvat . && docker run -p 8501:8501 fortis-fortuna-adiuvat` in the terminal. 
3. After a short wait for the container to initialize, access the Streamlit app by going to `http://localhost:8501` in your web browser.

## Features

- **Interactive Inputs**: Choose between sliders, manual entry, or fractional input to define your success rate and number of attempts.
- **Dynamic Visualization**: Instantly view the updated cumulative success probability curve as you adjust the inputs.
- **Motivational Insights**: Get personalized statistics on how your chances improve with persistence, including the number of attempts needed to reach a 95% success rate.

## Conclusion

The Success Probability Visualizer serves as a practical and motivational tool, encouraging users to persist in their efforts by providing a clear visual and numerical representation of how persistence increases the odds of success. It's a vivid reminder that sometimes, success is just a matter of trying one more time.
