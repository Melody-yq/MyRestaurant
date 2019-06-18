from app.exts import db
from datetime import datetime
class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    # title = db.Column(db.String(20),default="无标题")
    content=db.Column(db.Text(140))
    timestamp = db.Column(db.DateTime,default=datetime.utcnow())
    rid = db.Column(db.Integer,index=True,default=0)
    uid = db.Column(db.Integer,db.ForeignKey('user.id'))




