from flask import Flask
from flask import render_template, flash, redirect, request
from config import Config
from form import ProjectForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

@app.route("/")
def hello():
    user = {'username': 'Juli'}
    return render_template('index.html', title='Home', user=user)

@app.route("/form", methods=['GET', 'POST'])
def submit():
    form = ProjectForm()
    if form.validate_on_submit():
        result = request.form
        labels = ['name','city','type','area','email', 'link']
        data = []
        for key,value in result.items():
            if key in labels:
                data.append(value)
        return render_template('/thanks.html', data=data, result=result, labels=labels)
    return render_template('form.html', title='Contribute', form=form)

if __name__ == "__main__":
    app.run()
