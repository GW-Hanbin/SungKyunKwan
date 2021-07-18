import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as po
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler

import warnings

# Find elbow point
def elbow(X):
    sse = []

    for i in range(1,11):
        km = KMeans(n_clusters=i)
        km.fit(X)
        sse.append(km.inertia_)

    fig = px.line(sse)
    fig.show()

# Visualize clustering
def show_cluster(result, name):
    categories = ['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall']
    color = ['pink', 'red', 'green', 'blue']

    target = result[result['맥주이름'] == name]
    cluster = target['Cluster'].iloc[0]
    target = target[categories]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r = c_result.values[0],
        theta = categories,
        fill='toself',
        name='Bad',
        line_color=color[0]
    ))

    fig.add_trace(go.Scatterpolar(
        r = c_result.values[1],
        theta = categories,
        fill='toself',
        name='SoSo',
        line_color=color[1]
    ))

    fig.add_trace(go.Scatterpolar(
        r = c_result.values[2],
        theta = categories,
        fill='toself',
        name='Good',
        line_color=color[2]
    ))

    fig.add_trace(go.Scatterpolar(
        r = target.values[0],
        theta = categories,
        fill='toself',
        name=name,
        line_color=color[3]
    ))

    fig.update_layout(
      polar=dict( radialaxis=dict(visible=True,)),
    )

    fig.show()

warnings.filterwarnings('ignore')
pd.set_option('display.max_rows', 100)
data = pd.read_csv('afterPreprocessing.csv', encoding='utf-8-sig', index_col=0)

tmp = data.copy()
tmp = tmp[['맥주이름']]

# Remove duplicated rows
tmp.drop_duplicates(keep='first', inplace=True)
cols = ['Aroma','Appearance','Flavor','Mouthfeel','Overall']

# Add 5 attributes
for col in cols:
    tmp[col] = ''

# Start for all the number of beer types
for i in range(len(tmp)):
    # get the name of beer
    beer = tmp['맥주이름'].iloc[i]

    # get the number of evaluating users
    length = len(data[data['맥주이름'] == beer])

    # calculate 5 attributes
    for col in cols:

        # sum
        col_sum = data[data['맥주이름'] == beer][col].sum()
        # avg
        tmp[col].iloc[i] = col_sum / length

# save the tmp to csv file
tmp.to_csv('Ratings_by_Beer_Types.csv', encoding='utf-8-sig')
beer_names = tmp[['맥주이름']]
beer_values = tmp[['Aroma','Appearance','Flavor','Mouthfeel','Overall']]

# standardize the values
scaler = MinMaxScaler()
scaler.fit(beer_values)
scaled = scaler.transform(beer_values)
print("standardize the values")
print(scaled)
# find elbow point: 3
#elbow(scaled)

# KMeans variable
km = KMeans(n_clusters=3).fit(scaled)
print("KMeans variable")
print(km.cluster_centers_)

# predict cluster variable
predict = pd.DataFrame(km.predict(scaled))
predict.columns = ['Cluster']

# resave dataframe
scaled = pd.DataFrame(data=scaled, columns=
        ['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall'])

# sort the index
beer_names.reset_index(inplace=True, drop=True)

# merge the scale, predicted clustering, and beer name
result = pd.concat([scaled, beer_names], axis=1).reset_index(drop=True)
result = pd.concat([result, predict], axis=1).reset_index(drop=True)
print("merge the scale, predicted clustering, and beer name")
print(result)

# properties of each cluster
c_result = km.cluster_centers_
c_result = pd.DataFrame(data=c_result)
c_result.columns = ['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall']
c_result.sort_values(by='Overall', inplace=True)
print("properties of each cluster")
print(c_result)

# example) Asahi Super Dry
show_cluster(result, 'Asahi Super Dry')

# save the result
result.to_csv('clusterAllvalues.csv', encoding='utf-8-sig')
c_result.to_csv('clusterRepresentative.csv', encoding='utf-8-sig')

