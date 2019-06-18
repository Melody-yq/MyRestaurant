from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import DataRequired, Length


class PostForm(FlaskForm):
    # 如果要设置指定的属性 可以写 render_kw
    # title =StringField('',render_kw={'placeholder':'请著明标题'},validators=[DataRequired(),Length(5,30,message="标题长度请保持在5-20之间")])
    content = TextAreaField('', render_kw={'placeholder': '这一刻你想说什么'},
                            validators=[DataRequired(), Length(10, 140, message="内容请保持在10-140字长")])
    submit = SubmitField("发表")
