from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ChannelSearch(FlaskForm):
    name = StringField("Channel Name", validators=[DataRequired(), Length(max=50)])
    submit = SubmitField("Search")