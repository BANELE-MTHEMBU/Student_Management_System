from flask import Flask, render_template
app = Flask(__name__)

#defining route
@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')

@app.route('templates/auth/register',methods=['GET'])
def register():
    return render_template('auth/register.html')

@app.route('templates/auth/login',methods=['GET'])
def login():
    return render_template('auth/login.html')

if __name__ == "__main__":
    # any port # is acceptable as long it is not in use
    app.run(host = 'localhost', port = 1234, debug = True)
    
    
    