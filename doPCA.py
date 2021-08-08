from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv('afterPreprocessing.csv', engine='python', index_col=0)
beer_list = pd.read_csv('beerName.csv', engine='python', index_col=0)
beer_list = beer_list['beername']
names=['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall', 'beername']
df = df[names]
newname = df.reset_index(drop=False, inplace=False)

x = df.drop(['beername'], axis=1).values
y = df['beername'].values

x = StandardScaler().fit_transform(x)
feat = ['Aroma', 'Appearance', 'Flavor', 'Mouthfeel', 'Overall']

pca = PCA(n_components=2)
principalComponents = pca.fit_transform(x)
principalDF = pd.DataFrame(data=principalComponents, columns = ['Principal Component 1', 'Principal Component 2'])

fig = plt.figure(figsize = (20, 20))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('Principal Component 1', fontsize = 15)
ax.set_ylabel('Principal Component 2', fontsize = 15)
ax.set_title('2 component PCA', fontsize=20)

finalDF = pd.concat([principalDF, newname[['beername']]], axis=1)

colors =['green', 'red', 'navy']
i = 17
for target, color in zip(beer_list[3*(i-1):3*(i)], colors):
    indicesToKeep = finalDF['beername'] == target
    ax.scatter(principalDF.loc[indicesToKeep, 'Principal Component 1'], principalDF.loc[indicesToKeep, 'Principal Component 2'], c = color, s = 50)
    ax.legend(beer_list[3*(i-1):3*(i)])
    ax.grid()

url = "./PCA" + str(i) + ".jpg"
plt.savefig(url)
