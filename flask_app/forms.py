from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

class PostForm(FlaskForm):
    title = StringField('Title', validators=[Optional()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
