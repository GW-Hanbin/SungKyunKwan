from sklearn import preprocessing
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('afterPreprocessing.csv', engine='python', index_col=0)
data = df.groupby('beername').mean()

print(data.head())


newdata = data.drop(['Aroma', 'Appearance', 'Flavor', 'Mouthfeel'], axis=1)


# estimator = KMeans(n_clusters = 3)
# cluster_ids = estimator.fit_predict(newdata)
#
# plt.scatter(newdata['rating'], newdata['Overall'], c=cluster_ids)
# plt.xlabel("rating")
# plt.ylabel("Overall")

min_max_Scaler = preprocessing.MinMaxScaler()
newdata[['rating', 'Overall']] = min_max_Scaler.fit_transform(newdata[['rating', 'Overall']])

estimator = KMeans(n_clusters= 3)
cluster_ids = estimator.fit_predict(newdata)

plt.scatter(newdata['rating'], newdata['Overall'], c=cluster_ids)
plt.xlabel("rating")
plt.ylabel("Overall")

for beername, rating, Overall in newdata.itertuples():
     plt.annotate(beername, (rating, Overall))

modes = ['single', 'average', 'complete']

plt.figure(figsize=(20,5))
y_axis = None

for i, mode in enumerate(modes):
    # 서브플롯 추가, y축은 공유
    y_axis = plt.subplot(1, 4, i + 1, sharey=y_axis)

    # 레이블링
    plt.title('Dendrogram - linkage mode: {}'.format(mode))
    plt.xlabel('distance')
    plt.ylabel('beers')

    # 클러스터링
    clustering = linkage(newdata[['rating', 'Overall']], mode)

    # 덴드로그램
    dendrogram(clustering, labels=list(newdata.index), orientation='right')
plt.tight_layout()
plt.show()