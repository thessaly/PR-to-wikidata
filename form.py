from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField, SelectField, BooleanField
from wtforms import validators, ValidationError
from wtforms.validators import DataRequired, URL

class ProjectForm(FlaskForm):
    name = TextField('Name of the project', validators=[DataRequired()])
    city = StringField('City of origin', validators=[DataRequired()])
    type = SelectField('Which option describes this item better?', choices=[('project', 'project'), ('organization', 'organization'), ('business', 'business'), ('nonprofit', 'nonprofit'), ('university research group', 'university research group'),('community', 'community'),('other', 'other')])
    area = SelectField('Field of Work', choices = [('Education','Education'),('Education','Art'),('Education','Social innovation'),('D','Community Science'),('Education','Academic research')])
    link = StringField('Link to website or repository', validators=[URL(), DataRequired()])
    coords = StringField('Geocoordinates', validators=[DataRequired()])
    gosh = SelectField('Is part of GOSH community?', choices=[('yes', 'yes'), ('no','no')])
    submit = SubmitField('Submit')
