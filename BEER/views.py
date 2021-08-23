from django.shortcuts import render
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import json

def index(request):
    return render(request, 'beer/index.html')

def ver1(request):
    beer_list = pd.read_csv('/home/lhb9431/SungKyunKwan/beerName.csv', engine='python', index_col=0)
    beer_year = pd.read_csv('/home/lhb9431/SungKyunKwan/averageAnnualRating.csv', engine='python', index_col=0)
    ratings = pd.read_csv('/home/lhb9431/SungKyunKwan/afterPreprocessing.csv', engine='python', index_col=0)
    cluster_3 = pd.read_csv('/home/lhb9431/SungKyunKwan/clusterRepresentative.csv', engine='python', index_col=0)
    cluster_all = pd.read_csv('/home/lhb9431/SungKyunKwan/clusterAllvalues.csv', engine='python', index_col=0)
    beer_data = pd.read_csv('/home/lhb9431/SungKyunKwan/beerCBFdata.csv', engine='python', index_col=0)
    beer_list = beer_list['beername']
    cluster_3 = cluster_3.values

    if request.method == 'POST':
        beer_name = request.POST.get('beer', '')
        detail = request.POST.get('detail', '')
        df_aroma = recomm_feature(ratings, 'Aroma')
        df_flavor = recomm_feature(ratings, 'Flavor')
        df_mouthfeel = recomm_feature(ratings, 'Mouthfeel')

        if detail == 'Aroma':
            df = df_aroma * 0.8 + df_flavor * 0.1 + df_mouthfeel * 0.1
        if detail == 'Flavor':
            df = df_aroma * 0.1 + df_flavor * 0.8 + df_mouthfeel * 0.1
        if detail == 'Mouthfeel':
            df = df_aroma * 0.1 + df_flavor * 0.1 + df_mouthfeel * 0.8

        result = recomm_beer(df, beer_name)
        result = result.index.tolist()

        # Cluster Result
        tmp_cluster = []
        category = []
        food = []
        for i in range(3):
            target = cluster_all[cluster_all['beername'] == result[i]]
            target = target[['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall']]
            target = target.values[0]
            tmp_cluster.append(target)

            try:
                category.append(beer_data[beer_data['beername'] == result[i]]['category'].values[0])
                food.append(beer_data[beer_data['beername'] == result[i]]['Food'].values[0])

            except:
                category.append('Not collected.')
                food.append('Not collected.')

        # Annual Rating Result
        tmp_year = []
        tmp_ratings = []
        for i in range(3):
            target = beer_year[beer_year['beername'] == result[i]]
            target_year = target['year'].tolist()
            target_rating = target['rating'].tolist()
            tmp_year.append(target_year)
            tmp_ratings.append(target_rating)

        # JSON Data Conversion
        targetdict = {
            'beer_name': result,
            'beer_cluster1': tmp_cluster[0].tolist(),
            'beer_cluster2': tmp_cluster[1].tolist(),
            'beer_cluster3': tmp_cluster[2].tolist(),
            'cluster1': cluster_3[0].tolist(),
            'cluster2': cluster_3[1].tolist(),
            'cluster3': cluster_3[2].tolist(),
            'tmp_year': tmp_year,
            'tmp_ratings': tmp_ratings
        }

        targetJson = json.dumps(targetdict)

        return render(request, 'beer/ver1_result.html', {'result': result, 'beer_list': beer_list, 'targetJson': targetJson, 'category': category, 'food': food})
    else:
        return render(request, 'beer/ver1.html', {'beer_list': beer_list})

def ver2(request):
    beer_list = pd.read_csv('/home/lhb9431/SungKyunKwan/beerName.csv', engine='python', index_col=0)
    beer_year = pd.read_csv('/home/lhb9431/SungKyunKwan/averageAnnualRating.csv', engine='python', index_col=0)
    ratings = pd.read_csv('/home/lhb9431/SungKyunKwan/afterPreprocessing.csv', engine='python', index_col=0)
    cluster_3 = pd.read_csv('/home/lhb9431/SungKyunKwan/clusterRepresentative.csv', engine='python', index_col=0)
    cluster_all = pd.read_csv('/home/lhb9431/SungKyunKwan/clusterAllvalues.csv', engine='python', index_col=0)
    beer_data = pd.read_csv('/home/lhb9431/SungKyunKwan/beerCBFdata.csv', engine='python', index_col=0)
    beer_list = beer_list['beername']
    cluster_3 = cluster_3.values

    if request.method == 'POST':
        name = request.POST.get('name', '')
        beer = []
        rating = []
        for i in range(1, 6):
            beer.append(request.POST.get('beer' + str(i), ''))
            rating.append((request.POST.get('rating' + str(i), '')))

        for i in range(len(beer)):
            tmp = []
            tmp.append(name)
            tmp.append(beer[i])
            tmp.append(float(rating[i]))
            tmp = pd.DataFrame(data=[tmp], columns=['ID', 'beername', 'rating'])
            ratings = pd.concat([ratings, tmp])

        username = name
        ratings_matrix = ratings.pivot_table('rating', index='ID', columns='beername')
        ratings_matrix = ratings_matrix.fillna(0)
        ratings_matrix_T = ratings_matrix.transpose()

        item_sim = cosine_similarity(ratings_matrix_T, ratings_matrix_T)
        item_sim_df = pd.DataFrame(data=item_sim, index=ratings_matrix.columns, columns=ratings_matrix.columns)

        # using the user similar to top-n
        ratings_pred = ratingPredictSim(ratings_matrix.values, item_sim_df.values, n=5)
        # remake dataframe by calculated predicted rating data
        ratings_pred_matrix = pd.DataFrame(data=ratings_pred, index=ratings_matrix.index, columns=ratings_matrix.columns)

        # the beername which the user didn't try
        not_tried = notTriedBeer(ratings_matrix, username)
        # item based knn
        recomm_beer = recommendBeerbyID(ratings_pred_matrix, username, not_tried, top_n=3)
        recomm_beer = pd.DataFrame(data=recomm_beer.values, index=recomm_beer.index, columns=['predict rating'])
        # the name of recommended result
        result = recomm_beer.index.tolist()

        # Cluster result
        tmp_cluster = []
        category = []
        food = []
        for i in range(3):
            target = cluster_all[cluster_all['beername'] == result[i]]
            target = target[['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall']]
            target = target.values[0]
            tmp_cluster.append(target)

            try:
                category.append(beer_data[beer_data['beername'] == result[i]]['category'].values[0])
                food.append(beer_data[beer_data['beername'] == result[i]]['Food'].values[0])
            except:
                category.append('Not collected.')
                food.append('Not collected.')

        # Annual Rating Result
        tmp_year = []
        tmp_ratings = []
        for i in range(3):
            target = beer_year[beer_year['beername'] == result[i]]
            target_year = target['year'].tolist()
            target_rating = target['rating'].tolist()
            tmp_year.append(target_year)
            tmp_ratings.append(target_rating)

        # JSON Data Conversion
        targetdict = {
            'beer_name': result,
            'beer_cluster1': tmp_cluster[0].tolist(),
            'beer_cluster2': tmp_cluster[1].tolist(),
            'beer_cluster3': tmp_cluster[2].tolist(),
            'cluster1': cluster_3[0].tolist(),
            'cluster2': cluster_3[1].tolist(),
            'cluster3': cluster_3[2].tolist(),
            'tmp_year': tmp_year,
            'tmp_ratings': tmp_ratings
        }

        targetJson = json.dumps(targetdict)

        return render(request, 'beer/ver2_result.html', {'result': result, 'beer_list': beer_list, 'targetJson': targetJson, 'category': category, 'food': food})

    else:
        return render(request, 'beer/ver2.html', {'beer_list': beer_list})


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

# ftn to calculate similarity after selecting attributes(Score, Aroma, Flavor, Mouthfeel)
def recomm_feature(df, col):
    feat = col
    rate = df[['ID', 'beername', feat]]

    # configure user-id matrix using pivot table
    ratings_matrix = rate.pivot_table(feat, index='ID', columns='beername')

    # delete NaN
    ratings_matrix = ratings_matrix.fillna(0)

    # since item-based, transpose it from user * beer to beer * user matrix
    ratings_matrix_T = ratings_matrix.transpose()

    # calculate cosine similarity
    sim = cosine_similarity(ratings_matrix_T, ratings_matrix_T)
    sim_df = pd.DataFrame(data=sim, index=ratings_matrix.columns, columns=ratings_matrix.columns)

    return sim_df

# select 3 beers about biggest similarity
def recomm_beer(sim_df, beer):
    return sim_df[beer].sort_values(ascending=False)[1:4]
