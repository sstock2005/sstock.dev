from flask import Flask, render_template, send_from_directory, send_file, session, request, redirect
import random
import json
import uuid
import os
import re

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

# ---- misc functions ----
def isValidURL(str):
    
    regex = ("((http|https)://)(www.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")

    p = re.compile(regex)
 
    if (str == None):
        return False
    
    if(re.search(p, str)):
        return True
    else:
        return False

# ---- sstock.dev ----
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/assets/<path:name>')
def assets_imgs(name):
    return send_from_directory('assets', name, as_attachment=True)

# ---- sillycats.me ----
@app.route('/cat')
def cats():
    noise = random.choice(["meow!", "meowwww", "grrr!", "miaow", "mrruh", "prrrup", "mrow", "mrrrrrr"])
    return render_template('cat.html', noise=noise)

@app.route('/cat/image')
def cat_image():
    if 'last_cat' not in session:
        session['last_cat'] = None
    picture = random.choice(os.listdir("./pictures"))
    while picture == session['last_cat']:
        picture = random.choice(os.listdir("./pictures"))
    session['last_cat'] = picture
    return send_file("pictures/{}".format(picture), "image/png", False)

@app.route('/cat/noise')
def cat_noise():
    return random.choice(["meow!", "meowwww", "grrr!", "miaow", "mrruh", "prrrup", "mrow", "mrrrrrr"]), 200, {'Content-Type': 'text/plain'}

# ---- url shortener ----
@app.route('/short', methods=['GET', 'POST'])
def short():
    if request.method == "GET":
        return render_template('url.html')
    if request.method == "POST":
        url = request.json['url']

        if isValidURL(url) == False:
            return 'invalid url', 403
        
        uid = str(uuid.uuid4())[:5]

        if os.path.isfile("short_url.db") == False:
            with open("short_url.db", 'a'):
                os.utime("short_url.db", None)
                
        if os.path.isfile('short_url.db'):
            with open("short_url.db","r") as db_file:
                db_plain = db_file.read()
                try:
                    db = json.loads(db_plain)
                except:
                    db = json.loads("{\"pairs\":[[]]}")

            if len(db_plain) > 5:
                for pair in db['pairs']:
                    db_short_url = pair[0]
                    db_long_url = pair[1]

                    if url == db_long_url:
                        return f"https://sstock.dev/short/{db_short_url}", 200
                    if uid == db_short_url:
                        uid = str(uuid.uuid4())[:5]
                        continue

                db['pairs'].append((uid, url))
            else:
                db['pairs'][0] = (uid, url)

            with open("short_url.db", "w") as db_file:
                db_file.write(json.dumps(db))

            return f"https://sstock.dev/short/{uid}", 200
        else:
            return "could not connect to db", 500
        
@app.route('/short/<hash>')
def short_route(hash):
    if os.path.isfile("short_url.db"):
        with open("short_url.db", "r") as db_file:
            db_plain = db_file.read()
            try:
                db = json.loads(db_plain)
            except:
                return 'could not connect to db', 500
            
            for pair in db['pairs']:
                if pair[0] == hash:
                    return redirect(pair[1])

            return redirect('/short')
        
if __name__ == '__main__':
    app.run("127.0.0.1", 8080, True, threaded=True)