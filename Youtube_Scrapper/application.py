from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
# from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo
import scrapetube
import pandas as pd
import os

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
#@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
#@cross_origin()

def index():
    if request.method == 'POST':

        # query to search for images
        channel_name = request.form['content'].replace(" ","")
        limit=request.form['num']

        url= f'https://www.youtube.com/@{channel_name}/videos'

        videos = scrapetube.get_channel(channel_url  = url,limit=limit)

        data = [] 
        for video in videos:
            # extracting url of videos
            url = video['videoId']
            urls = f'https://youtube.com/watch?v={url}'
            
            # extracting thumbnails of videos
            thumbs =video['thumbnail']['thumbnails'][-1]['url']
            
            # extracting titles of videos 
            title = video['title']['runs'][0]['text']
            
            # extracting number of views of videos 
            views = video['viewCountText']['simpleText'].split(' ')[0]
            
            #  extracting upload time of videos
            time = video['publishedTimeText']['simpleText']
            
            # appending all the data into list
            data.append((urls ,thumbs ,title ,views ,time))

        df=pd.DataFrame(data, columns=['Urls' ,'Thumbs' ,'Title' ,'Views' ,'Time'])

        #my_dic = df.to_dict()

        mydic = "youtube_data/"
        if not os.path.exists(mydic):
            os.makedirs(mydic)
        fy = df.to_csv()
        filepath = os.path.join(mydic, f'{channel_name}.csv' )
        with open (filepath , 'w',encoding='utf-8') as f:
            f.write(fy)

        reviews = []
        for i in range (int(limit)):
            mydict = {"channelname": channel_name , "Urls": data[i][0] ,"Thumbs" : data[i][1], "Title": data[i][2], "Views": data[i][3],"Time": data[i][4]}
            reviews.append(mydict)

        #mydata=[reviews,channel_name]
        return render_template("results.html",reviews=reviews)

        client = pymongo.MongoClient("mongodb+srv://arjunvermam:2758@cluster0.uqflnth.mongodb.net/?retryWrites=true&w=majority")
        db = client['image_scrap']

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8000, debug=True)
	app.run(debug=True)