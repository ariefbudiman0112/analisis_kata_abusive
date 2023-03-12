from flask import Flask, jsonify, render_template, request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
from api import cleansing_text
import pandas as pd
import re
import sqlite3

app = Flask(__name__)

###############################################################################################################
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
    info = {
        'title': LazyString(lambda:'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda:'1.0.0'),
        'description': LazyString(lambda:'Dokumentasi API untuk Data Processing dan Modeling')
        }, host = LazyString(lambda: request.host)
    )

swagger_config = {
        "headers":[],
        "specs":[
            {
            "endpoint":'docs',
            "route":'/docs.json'
            }
        ],
        "static_url_path":"/flasgger_static",
        "swagger_ui":True,
        "specs_route":"/docs/"
    }

swagger = Swagger(app, template=swagger_template, config=swagger_config)
###############################################################################################################

def db_connection():
    #Connecting to database
    conn = sqlite3.connect('sql.db', check_same_thread=False)
    c = conn.cursor()
    #Defining and executing the query for table data if it not available
    conn.execute('''CREATE TABLE IF NOT EXISTS tweet_library (id INTEGER PRIMARY KEY AUTOINCREMENT, tweet varchar(255), new_tweet varchar(255));''')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = db_connection()
    posts = conn.execute('SELECT * FROM tweet_library').fetchall()
    conn.close()
    return render_template("index.html", posts = posts)

@swag_from("docs/delete_all.yml", methods = ['GET'])
@app.route('/delete_all', methods = ['GET'])
def delete_all():
    conn = db_connection()
    conn.execute('''DELETE FROM tweet_library;''')
    conn.commit()
    conn.close()
    json_response = {
        'status_code' : 200,
        'description' : "Delete process is success",
        'data' : "Delete all",
    }
    
    return jsonify(json_response)

@swag_from("docs/get.yml", methods = ['GET'])
@app.route('/get_all', methods = ['GET'])
def get_all():
    conn = db_connection()
    sql_query = pd.read_sql_query ('''
                               SELECT
                               *
                               FROM tweet_library
                               ''', conn)
    conn.close()
    df = pd.DataFrame(sql_query, columns = ['id','tweet', 'new_tweet'])
    df = df.to_dict('records')

    response_data = jsonify(df)
    return response_data
    
@swag_from("docs/post.yml", methods = ['POST'])
@app.route('/manual_input', methods = ['POST'])
def manual_input():
    input_json = request.get_json(force=True)
    original_text = input_json['Tweet']
    
    old_tweet = input_json['Tweet']

    cleaned_text = cleansing_text(original_text)
    
    conn = db_connection()
    conn.execute('''INSERT INTO tweet_library(tweet, new_tweet) VALUES (? , ?);''', (old_tweet, cleaned_text))
    conn.commit()
    conn.close()
    
    finalresult = {'Old tweet' : old_tweet,'New Tweet' : cleaned_text}
    
    return jsonify(finalresult)

@swag_from('docs/upload.yml', methods=['POST'])
@app.route('/upload', methods=['POST'])
def uploadDoc():
    file = request.files['file']

    try:
        data = pd.read_csv(file, encoding='iso-8859-1', error_bad_lines=False)
    except:
        data = pd.read_csv(file, encoding='utf-8', error_bad_lines=False)

    cleaned_text = []
    
    conn = db_connection()
    for text in data['Tweet']:
        new_text = cleansing_text(text)
        
        conn.execute('''INSERT INTO tweet_library(tweet, new_tweet) VALUES (? , ?);''',(text, new_text))
        conn.commit()
            
        cleaned_text.append(new_text)
    conn.close()
      
    data['Tweet_New'] = cleaned_text
    data = data[['Tweet_New','Tweet']]
    
    data = data.to_dict('records')
        
    return jsonify(data)

if __name__ == '__main__':
    app.run()

### run flask otomatis debug
# flask --app test_demo_swag --debug run