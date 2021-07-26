import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error

import warnings

# ftn to filter out beer and users who have left more than n data reviews
def preProcessing(data, n):
    min_id = data['아이디'].value_counts() >= n
    min_id = min_id[min_id].index.to_list()
    data = data[data['아이디'].isin(min_id)]

    min_beer = data['맥주이름'].value_counts() >= n
    min_beer = min_beer[min_beer].index.to_list()
    data = data[data['맥주이름'].isin(min_beer)]

    return data

# ftn to predict rating
def ratingPredict(ratings_arr, item_arr):
    rating = ratings_arr.dot(item_arr) / np.array([np.abs(item_arr).sum(axis=1)])
    return rating

# ftn to calculate MSE by difference of predicted and real ratings
def getMSE(pred, actual):
    pred = pred[actual.nonzero()].flatten()
    actual = actual[actual.nonzero()].flatten()
    return mean_squared_error(pred, actual)

# ftn to calculate similarity by top rating
def ratingPredictSim(ratings_arr, item_arr, n=20):
    pred = np.zeros(ratings_arr.shape)

    for col in range(ratings_arr.shape[1]):
        # return the idx by Desc
        top_n_items = [np.argsort(item_arr[:, col])[:-n-1:-1]]
        for row in range(ratings_arr.shape[0]):
            pred[row, col] = item_arr[col,:][top_n_items].dot(
            ratings_arr[row, :][top_n_items].T)
            pred[row, col] /= np.sum(item_arr[col,:][top_n_items])

    return pred

# ftn to exclude the already drunked beer
def notTriedBeer(ratings_matrix, user_id):
    user_rating = ratings_matrix.loc[user_id, :]
    tried = user_rating[user_rating>0].index.tolist()
    beer_list = ratings_matrix.columns.tolist()
    not_tried = [beer for beer in beer_list if beer not in tried]

    return not_tried

# ftn to sort thd beer name by highest overall value
def recommendBeerbyID(pred_df, user_id, not_tried, top_n):
    beer = pred_df.loc[user_id, not_tried].sort_values(ascending=False)[:top_n]
    return beer


warnings.filterwarnings('ignore')

data = pd.read_csv('afterPreprocessing.csv', encoding='utf-8-sig', index_col=0)
tmp = data.copy()

for i in range(0,10):
    tmp = preProcessing(tmp, 10)
    print(tmp.shape)

# before: 60,000 after: 26859
tmp.to_csv('Refined_data.csv', encoding='utf-8-sig')

# cosine similarity
n_data = pd.read_csv('Refined_data.csv', encoding='utf-8-sig', index_col=0)
ratings = n_data.copy()

# configure user-id matrix using pivot table
ratings_matrix = ratings.pivot_table('평점', index='아이디', columns='맥주이름')

# delete NaN
ratings_matrix = ratings_matrix.fillna(0)
# 1838 users, 40 beer types
print(ratings_matrix)

# since item-based, transpose it from user * beer to beer * user matrix
ratings_matrix_T = ratings_matrix.transpose()
print(ratings_matrix_T)

# calculate cosine similarity
sim = cosine_similarity(ratings_matrix_T, ratings_matrix_T)
sim_df = pd.DataFrame(data= sim, index= ratings_matrix.columns, columns= ratings_matrix.columns)

# select 3 beers like 'Budweiser'
print(sim_df['Budweiser'].sort_values(ascending=False)[:4])

# calculate the predicted rating value
pred_rating = ratingPredict(ratings_matrix.values, sim_df.values)
pred_rating_matrix = pd.DataFrame(data= pred_rating, index= ratings_matrix.index, columns= ratings_matrix.columns)

print(pred_rating_matrix)
print("Nearest Neighbors MSE: ", getMSE(pred_rating, ratings_matrix.values))

# select 5 biggest similarity about 3 beers
top_n_items = [np.argsort(sim_df.values[:,3])[:-5:-1]]
print(top_n_items)

sim_pred_rating = ratingPredictSim(ratings_matrix.values, sim_df.values, n=10)
sim_pred_rating_matrix = pd.DataFrame(data=sim_pred_rating, index=ratings_matrix.index, columns=ratings_matrix.columns)
print("Nearest Neighbors TOP-Sim: ", getMSE(sim_pred_rating, ratings_matrix.values))
print(sim_pred_rating_matrix)

# random username in .csv
username1 = '00cobraR(1,103)'
username2 = 'zvikar(11,503)'

# calculate the beer which did not been drunk
no_tried = notTriedBeer(ratings_matrix, username2)

ratings_pred = ratingPredictSim(ratings_matrix.values, sim_df.values, n=5)

# recreate predicted data to dataframe
ratings_pred_matrix = pd.DataFrame(data=ratings_pred, index=ratings_matrix.index, columns=ratings_matrix.columns)

# not tried beer by USERNAME
not_tried = notTriedBeer(ratings_matrix, username2)

# recommend beer by Highest overall
beer = recommendBeerbyID(ratings_pred_matrix, username2, not_tried, top_n=3)
beer = pd.DataFrame(data=beer.values, index=beer.index, columns=['예측평점'])
print(beer)
