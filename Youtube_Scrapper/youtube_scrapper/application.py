from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import pymongo
import scrapetube
import pandas as pd
import os
import logging


logging.basicConfig(filename= 'youtube.log', level=logging.INFO, format= '%(asctime)s, %(name)s, %(message)s')

application = Flask(__name__) # initializing a flask app
app=application

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()

def index():
    if request.method == 'POST':

        try:
        
            # query to search for images
            channel_name = request.form['content'].replace(" ","")
            limit = request.form['num']
            
            logging.info(f'Name of the channel = {channel_name}')

            url= f'https://www.youtube.com/@{channel_name}/videos'

            videos = scrapetube.get_channel(channel_url  = url, limit=int(limit))

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
                mydict = {"channelname": channel_name , "Urls": urls ,"Thumbs" : thumbs, "Title": title, "Views": views,"Time": time}
                data.append(mydict)

            # creating dataframe to convert data into csv & dict
            df=pd.DataFrame(data)
            fy = df.to_csv() 
            my_dict = df.to_dict('records') 

            logging.info('Checking csv file')

            # creating folder & path
            path = "youtube_data/"
            if not os.path.exists(path):
                os.makedirs(path) 
            
            # joining filepaths
            filepath = os.path.join(path, f'{channel_name}.csv' )
            with open (filepath , 'w',encoding='utf-8') as f:
                f.write(fy)

            logging.info('Saving data in mongoDB')

            client = pymongo.MongoClient("mongodb+srv://naman7374:naman7374@cluster0.ehmrlj9.mongodb.net/?retryWrites=true&w=majority")
            db=client['youtube_scrap']
            youtube_scrap_data = db['youtube_scrap_data']
            youtube_scrap_data.insert_many(my_dict)

            return render_template("results.html", reviews=data)
        
        except Exception as e:
            print('Exeeption message', e)
            return 'Somthing Is Wrong'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8000, debug=True)
        #app.run(debug=True)
    app.run(host="0.0.0.0")