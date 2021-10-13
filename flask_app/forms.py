from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional

class PostForm(FlaskForm):
    title = StringField('Title', validators=[Optional()])
    postType = SelectField(
        'Title',
        [DataRequired()],
        choices=[
            ('text', 'Standard Text Post'),
            ('quote', 'Quote'),
            ('idea', 'Idea'),
            ('link', 'Link'),
            ('image', 'Image'),
            ('measure', 'Measure')
        ]
    )
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
