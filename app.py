from flask import Flask, render_template, request
import tweepy
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:PGycombinator@localhost:5432/Twitter_Test'
    #https://stackoverflow.com/questions/62688256/sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy-dialectspostgre
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy (app)

class Twitter_Test (db.Model) :
    __tablename__ = 'Tweets'
    id = db.Column(db.Integer)
    tweet_id = db.Column(db.BigInteger,primary_key=True)
    date = db.Column(db.String(300))
    tweet_text = db.Column(db.String(400))

    def __init__(self,tweet_id,date,tweet_text):
        self.tweet_id = tweet_id
        self.date = date
        self.tweet_text = tweet_text


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods =['POST'])
def submit():
    if request.method =='POST' :
        auth = tweepy.OAuthHandler ("6Dd5YJQcWGYYAsst9HLgvmyf7","wPkxLc3gZQf0b0hdh4bHtr9zUSroBhiZTYXATRMMGagDRiJpD8")

        auth.set_access_token ("332065343-A2wv1pLBHeMsm4PZFvkX7Ko2tqIylf7Ez1bKIcEG", "7r6oEHespSU3pojOOLXem8bPWgeB3DGWRux4KgeQm5xkq")

        api = tweepy.API (auth)

        count = 0

        try :
            api.verify_credentials()
            print("Authentication OK")

        except: 
            print ("Authentication failed")

        username = "manas_saloi"

        tweets = api.user_timeline(screen_name=username,count = 10, tweet_mode='extended', exclude_replies= True,include_entities = True) #entities includes the expanded url, tweet_mode allows for >140 characters - see Tweepy docs for more

        for tweet in tweets : 
            try :   
                urls = tweet.entities['urls']
                Expanded_URL = urls[0]['expanded_url'] #See the Twitter JSON response to understand why this format is used to get to expanded URL.
                Normal_URL = urls[0]['url']
                if hasattr(tweet, "retweeted_status"):
                  updated_text = tweet.retweeted_status.full_text.replace(Normal_URL, Expanded_URL)
                else:
                  updated_text = tweet.full_text.replace(Normal_URL, Expanded_URL)
                if db.session.query (Twitter_Test).filter(Twitter_Test.tweet_id == tweet.id).count() == 0:
                    data = Twitter_Test(tweet.id,tweet.created_at.strftime('%d %m %y'),updated_text)
                    db.session.add(data)
                    db.session.commit()
            except :
                if hasattr(tweet, "retweeted_status"):
                  if db.session.query (Twitter_Test).filter(Twitter_Test.tweet_id == tweet.id).count() == 0:
                    data = Twitter_Test(tweet.id,tweet.created_at.strftime('%d %m %y'),tweet.retweeted_status.full_text)
                    db.session.add(data)
                    db.session.commit()
                else:
                  if db.session.query (Twitter_Test).filter(Twitter_Test.tweet_id == tweet.id).count() == 0:
                    data = Twitter_Test(tweet.id,tweet.created_at.strftime('%d %m %y'),tweet.full_text)
                    db.session.add(data)
                    db.session.commit()
        
    tweets_html = Twitter_Test.query.all()
    return render_template ('success.html',tweets = tweets_html)        


if __name__ =='__main__':
    app.run ()