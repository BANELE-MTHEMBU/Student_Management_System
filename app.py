from flask import Flask, render_template
app = Flask(__name__)

#defining route
@app.route('/',methods=['GET'])
def home():
    return render_template('index.html')


if __name__ == "__main__":
    # any port # is acceptable as long it is not in use
    app.run(host = 'localhost', port = 1234, debug = True)
    