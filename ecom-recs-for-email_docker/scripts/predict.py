import pickle

import numpy as np
import pandas as pd
from scripts.logger import Logger
from sklearn.neighbors import NearestNeighbors

log = Logger("predict_script", "predict_script.log")


def generate_item_recommendations_for_clients(
    fited_data_path,
    clients_path,
    items_path,
    exclude_path,
    result_path,
    k,
    chunk,
    n_neighbors,
):
    """
    This function takes in the path of the trained data, the path of the clients, items and exclude files,
    the path to save the results and the number of recommendations to return per client, the number of clients to process at a time and the number of neighbors to consider before filtering.
    It then loads the data, maps the clients and items to their respective ids, filters out the previous purchases,
    gets the recommendations for each chunk of clients, filters them to return only k recommendations per client and saves the results to the result_path.
    """
    log.info("Let's get item recommendations for clients")

    # load data
    with open(fited_data_path, "rb") as f:
        fited_data = pickle.load(f)

    clients = pd.read_csv(clients_path, usecols=[0])
    clients.columns = ["client_id"]
    items = pd.read_csv(items_path, usecols=[0])
    items.columns = ["item_id"]
    exclude = pd.read_csv(exclude_path, usecols=[0, 1])
    exclude.columns = ["client_id", "item_id"]
    exclude["purchased"] = 1

    clients_mapping = fited_data["clients_mapping"]
    items_mapping = fited_data["items_mapping"]

    items_embeddings = fited_data["items_embeddings"]
    client_embeddings = fited_data["client_embeddings"]

    log.info(
        f"Data loaded. I got {len(clients)} clients and {len(items)} items to predict and {exclude.shape[0]} previous purchases to exclude"
    )
    # map clients and items to their respective mappings
    clients_for_predicts = clients[clients.isin(list(clients_mapping.keys()))].squeeze()
    items_for_predicts = items[items.isin(list(items_mapping.keys()))].squeeze()

    # filter previous purchases to exclude that are in the clients and items to predict
    previous_purchased_items = exclude[
        exclude["client_id"].isin(clients_for_predicts)
        & exclude["item_id"].isin(items_for_predicts)
    ]
    # Initialize dataframe to store recommendations
    df_result = pd.DataFrame(columns=["client_id", "item_id", "rank"])

    mapped_target_items = items_for_predicts.map(items_mapping).values
    items_vectors = items_embeddings[mapped_target_items]

    # create index to search nearest neighbours
    sk_member_idx = NearestNeighbors(algorithm="brute", metric="cosine")
    sk_member_idx.fit(items_vectors)

    # number of neighbours to retrieve
    n_neighbors = min(n_neighbors, items_vectors.shape[0])

    # count chunks of clients
    chunk_count = int(clients_for_predicts.shape[0] / chunk) + 1

    log.info(
        f"Start predicting {n_neighbors} items (before filter to {k} items) for {clients_for_predicts.shape[0]} clients in {chunk_count} chunks"
    )

    # loop through chunks of clients
    for i, target_clients_chunk in enumerate(
        np.array_split(clients_for_predicts, chunk_count)
    ):
        log.info(f"Chunk {i+1} of {chunk_count}")
        temp_recs = get_temp_recs(
            target_clients_chunk,
            clients_mapping,
            client_embeddings,
            items_for_predicts,
            sk_member_idx,
            n_neighbors,
        )
        temp_recs = filter_temp_recs(temp_recs, previous_purchased_items, k)
        df_result = pd.concat(
            [df_result, temp_recs[["client_id", "item_id", "rank"]]], ignore_index=True
        )

    df_result["rank"] = df_result["rank"].astype("int32")
    df_result["item_id"] = df_result["item_id"].astype("int32")
    df_result["client_id"] = df_result["client_id"].astype("int32")

    log.info(f"Saving results to {result_path}")
    df_result.to_csv(result_path, index=False)


# helper function to get recommendations for chunk of clients
def get_temp_recs(
    target_clients_chunk,
    clients_mapping,
    client_embeddings,
    items_for_predicts,
    sk_member_idx,
    n_neighbors,
):
    """
    Generate temporary recommendations for a chunk of clients.
    
    Parameters:
        target_clients_chunk (pandas.Series): Chunk of client IDs for which recommendations are to be generated.
        clients_mapping (dict): Mapping of client IDs to their index in the client embeddings array.
        client_embeddings (numpy.ndarray): Embeddings of clients.
        items_for_predicts (pandas.Series): Items for which recommendations are to be generated.
        sk_member_idx (sklearn.neighbors.NearestNeighbors): NearestNeighbors index of items.
        n_neighbors (int): Number of nearest neighbors to retrieve for each client.
    
    Returns:
        temp_recs (pandas.DataFrame): Temporary recommendations for the chunk of clients.
    """
    mapped_target_clients = target_clients_chunk.map(clients_mapping).values
    clients_vectors = client_embeddings[mapped_target_clients]

    top_items = np.array(
        sk_member_idx.kneighbors(clients_vectors, n_neighbors=n_neighbors)
    )

    temp_recs = pd.DataFrame(
        {
            "client_id": target_clients_chunk.repeat(n_neighbors),
            "item_id": top_items[1].flatten(),
            "rank": np.tile(
                np.arange(1, n_neighbors + 1), target_clients_chunk.shape[0]
            ),
        }
    )

    target_items_dict = dict(
        zip(np.arange(len(items_for_predicts)), items_for_predicts)
    )
    temp_recs["item_id"] = temp_recs["item_id"].map(target_items_dict)

    return temp_recs


# helper function to filter out previously purchased items
def filter_temp_recs(temp_recs, previous_purchased_items, k):
    """
    Filters temp_recs by removing items that have been previously purchased by the client,
    and limiting the number of recommendations to k for each client.

    Parameters:
    - temp_recs (pd.DataFrame): DataFrame containing the current recommendations.
    - previous_purchased_items (pd.DataFrame): DataFrame containing previous purchases to exclude.
    - k (int): Maximum number of recommendations per client.

    Returns:
    - temp_recs (pd.DataFrame): DataFrame containing filtered recommendations.
    """
    temp_recs = pd.merge(
        temp_recs, previous_purchased_items, on=["client_id", "item_id"], how="left"
    )
    temp_recs["rank"] = (
        temp_recs[temp_recs["purchased"].isna()]
        .sort_values(by=["client_id", "rank"])
        .groupby(["client_id"])
        .cumcount()
        + 1
    )
    temp_recs = temp_recs[temp_recs["rank"] <= k]
    return temp_recs
