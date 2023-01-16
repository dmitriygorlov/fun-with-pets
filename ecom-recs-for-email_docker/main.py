import os

from scripts.predict import generate_item_recommendations_for_clients
from scripts.train import train_and_save_lightfm_model
from settings import Settings

if __name__ == "__main__":
    """
    Entry point of the script.
    This script:
    1. loads the data paths from environment variables
    2. model training and save
    3. generates item recommendations for clients
    """

    # Load data paths
    data_path = os.environ.get("DATA_PATH")
    clients_path = os.environ.get("CLIENTS_PATH")
    items_path = os.environ.get("ITEMS_PATH")
    exclude_path = os.environ.get("EXCLUDE_PATH")
    result_path = os.environ.get("RESULT_PATH")

    # Train LightFM model and save embeddings and mappings
    fited_data_path = train_and_save_lightfm_model(
        data_path,
        Settings.NO_COMPONENTS,
        Settings.LEARNING_RATE,
        Settings.LOSS,
        Settings.EPOCHS,
    )

    # Generate item recommendations for clients
    generate_item_recommendations_for_clients(
        fited_data_path,
        clients_path,
        items_path,
        exclude_path,
        result_path,
        Settings.K,
        Settings.CHUNK,
        Settings.K_SPARE,
    )
