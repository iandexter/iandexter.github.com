from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def main():
    return redirect("https://www.iandexter.net/resume/", code=301)

if __name__ == '__main__':
    app.run(debug=True)
