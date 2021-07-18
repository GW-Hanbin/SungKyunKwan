import pandas as pd
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

pd.set_option('display.max_rows', 100)
beer = pd.read_csv('afterPreprocessing.csv', encoding = 'utf-8-sig', index_col = 0)

# histogram
label = ['distplot']
histogram = [beer.평점]

fig = ff.create_distplot(histogram, label, bin_size=[.1])
fig.show()

# boxplot
fig = go.Figure()
fig.add_trace(go.Box(y=beer.Aroma, name="Aroma"))
fig.add_trace(go.Box(y=beer.Appearance, name="Appearance"))
fig.add_trace(go.Box(y=beer.Flavor, name="Flavor"))
fig.add_trace(go.Box(y=beer.Mouthfeel, name="Mouthfeel"))
fig.add_trace(go.Box(y=beer.Overall, name="Overall"))

fig.show()

tmp = beer.copy()
tmp['월'] = tmp['날짜'].apply(lambda x: x.split('-')[1])
tmp['년'] = tmp['날짜'].apply(lambda x: x.split('-')[2])

ttmp = tmp.copy()
print(ttmp['맥주이름'].value_counts().head(10))
