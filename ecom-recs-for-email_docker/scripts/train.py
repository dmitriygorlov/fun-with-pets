import datetime as dt
import pickle

import numpy as np
import pandas as pd
from lightfm import LightFM
from lightfm.data import Dataset as LFMDataset
from scripts.logger import Logger

log = Logger("train_script", "train_script.log")


def train_and_save_lightfm_model(data_path, no_components, learning_rate, loss, epochs):
    """
    Train a LightFM model using the provided data, model parameters and save the fitted data (client and item mappings and embeddings).

    Copy code
    Parameters:
    data_path (str): The path of the data to train the model on.
    no_components (int): The number of components for the model.
    learning_rate (float): The learning rate for the model.
    loss (str): The loss function for the model, can be "logistic", "bpr", "warp" or "warp-kos".
    epochs (int): The number of times to iterate over the data while training the model.

    Returns:
    str: The path of the saved fitted data.
    """

    log.info("Let's train LightFM model")

    # load data
    data = pd.read_csv(data_path, usecols=[0, 1])

    data.columns = ["client_id", "item_id"]

    log.info(
        f"Data loaded. I got {data.shape[0]} rows that includes {data['client_id'].nunique()} clients and {data['item_id'].nunique()} items"
    )

    # structure for model
    dataset = LFMDataset()

    # add features
    dataset.fit_partial(data["client_id"].unique(), data["item_id"].unique())

    # don't use different weights for different interactions
    train_interactions, _ = dataset.build_interactions(zip(*data.iloc[:, 0:2].values.T))

    # fit model with given parameters
    log.info(
        f"I train LightFM model with parameters: no_components={no_components}, learning_rate={learning_rate}, loss={loss}, epochs={epochs} "
    )
    model = LightFM(
        no_components=no_components,
        learning_rate=learning_rate,
        loss=loss,
    )

    model.fit(train_interactions, epochs=epochs, verbose=True)

    log.info("Model trained, now I prepare fited data")
    # normalize embeddings
    item_biases, item_embeddings = model.get_item_representations()
    item_embeddings = np.append(item_embeddings, item_biases.reshape(-1, 1), axis=1)
    item_norms = np.linalg.norm(item_embeddings, axis=1)
    max_item_norm = item_norms.max()
    extra_dimension = np.sqrt(max_item_norm**2 - item_norms**2)
    norm_item_data = np.append(
        item_embeddings, extra_dimension.reshape(item_norms.shape[0], 1), axis=1
    )

    client_biases, client_embeddings = model.get_user_representations()
    client_embeddings = np.append(
        client_embeddings, np.ones((client_biases.shape[0], 1)), axis=1
    )
    client_embeddings = np.append(
        client_embeddings, np.zeros((client_embeddings.shape[0], 1)), axis=1
    )

    # don't use features, so don't need to get them
    (
        clients_mapping,
        _,
        items_mapping,
        _,
    ) = dataset.mapping()

    fited_data = dict()

    fited_data["clients_mapping"] = clients_mapping
    fited_data["items_mapping"] = items_mapping

    fited_data["items_embeddings"] = norm_item_data
    fited_data["client_embeddings"] = client_embeddings

    train_LightFM_path = f"mappings_embeddings/fited_data_{dt.date.today()}.pkl"
    with open(train_LightFM_path, "wb") as fp:
        pickle.dump(fited_data, fp)

    log.info("End training LightFM model, saved it here {train_LightFM_path}")
    return train_LightFM_path
