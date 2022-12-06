import pandas as pd
from nrclex import NRCLex
import plotly.express as px 

""" Pandas is used for creating data frames
    NRCLex is used for Emotion Sentiment Analysis
    Plotly is used for creating figures """


##Create Dataframe by reading original file with headlines
mydf = pd.read_csv("./data/UkrainianConflict-headlines-labeled.csv", sep=",")

#Just slice 13 column which has headline 
my_list = mydf['headline'].tolist()


##Get Emotion score for each line in headlines and add it to headlineemotions []
headlineemotions = []
for headline in my_list:
    # Create headline_object for NRCLex processing 
    headline_object = NRCLex(headline)
    headlineemotions.append(headline_object.raw_emotion_scores)
    

#Changed dictionary to dataframe 
myheadlinedf = pd.DataFrame(headlineemotions)

##Clean up the NaN data with 0 
myheadlinedf = myheadlinedf.fillna(0)

##Merge original dataset with emotions as new columns
mergeddf = pd.concat([mydf, myheadlinedf], axis=1)
print(mergeddf)


##Get total counts from all the headlines
##https://medium.com/geekculture/simple-emotion-classification-in-python-40fb24692541
str_headline = ','.join(mergeddf['headline'])
headline_object = NRCLex(str_headline)
headlinedata = headline_object.raw_emotion_scores
print(headlinedata)


#Now, Create the graph for this
## https://medium.com/geekculture/simple-emotion-classification-in-python-40fb24692541
emotion_df = pd.DataFrame.from_dict(headlinedata, orient='index')
emotion_df = emotion_df.reset_index()
emotion_df = emotion_df.rename(columns={'index' : 'Emotion Classification' , 0: 'Emotion Count'})
emotion_df = emotion_df.sort_values(by=['Emotion Count'], ascending=False)
print(emotion_df)

fig_bar = px.bar(emotion_df, x='Emotion Count', y='Emotion Classification', color = 'Emotion Classification', title = "Ukraine War Reddit Sentiment Analysis", orientation='h', width = 800, height = 400)
#fig.show()
fig_pie = px.pie(emotion_df, values = "Emotion Count", names = "Emotion Classification", color = 'Emotion Classification', title = "Ukraine War Reddit Sentiment Analysis", width = 800, height = 400)
fig_pie.show()
fig_bar.show()
