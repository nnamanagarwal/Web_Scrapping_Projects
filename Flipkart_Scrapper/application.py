from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pymongo

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
            searchString = request.form['content'].replace(" ","")
            flip_url = "https://www.flipkart.com/search?q=" + searchString
            url_opened = urlopen(flip_url).read()
            code_beautify = bs(url_opened,'html.parser')
            bigbox = code_beautify.find_all("div",{"class":"_13oc-S"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

            allurl=[]
            for i in bigbox:
                a=("https://www.flipkart.com" + i.div.div.a["href"])
                allurl.append(a)


            rating = []
            short_com = []
            main_com = []
            name = []
            reviews=[]

            for j in allurl:
                opener =  requests.get(j)
                opener.encoding='utf-8'
                product_link_code_bs = bs(opener.text,'html.parser')
                rating1 = product_link_code_bs.find_all("div",{"class":["col _2wzgFH","t-ZTKy _1QgsS5"]})
                shortlong_comm = product_link_code_bs.find_all("div",{"class":"_6K-7Co"})
                short = product_link_code_bs.find_all("p",{"class":"_2-N8zT"})
                comment = product_link_code_bs.find_all("div",{"class":"t-ZTKy"})
                name_tag = product_link_code_bs.find_all("div",{"class":"row _3n8db9"})
        

                try:
                    for i in rating1:
                        b = (i.div.div.text)
                        rating.append(b)
                except:
                    b = "No rating"

                try:
                    for s in name_tag:
                        u = (s.div.p.text)
                        name.append(u)
                except:
                    u = "No Name"
                    

                try:        
                    for y in short:
                        c = (y.text)
                        short_com.append(c)
                    if len(short_com) != len(rating):
                        for k in shortlong_comm:
                            c = (k.text)
                            short_com.append(c)
                except:
                    c = "No Short Comment"
                    

                try:
                    for l in shortlong_comm:
                        d = (l.text)
                        main_com.append(d)
                    if len(main_com) != len(rating):
                        for l in comment:
                            d =(l.div.div.text)
                            main_com.append(d)
                except:
                    d = "No Long Comment"
                    


            for i in range (len(rating)):
                mydict = {"Search Term": searchString ,"Name" : name[i], "Rating": rating[i], "CommentHead": short_com[i],"Comment": main_com[i]}
                reviews.append(mydict)

            client = pymongo.MongoClient("mongodb+srv://naman7374:naman7374@cluster0.ehmrlj9.mongodb.net/?retryWrites=true&w=majority")
            db = client['review_scrap']
            review_col = db['review_scrap_data']
            review_col.insert_many(reviews)

            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0")
	#app.run(debug=True)
