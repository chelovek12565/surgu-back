from .__all_models import *
from sqlalchemy.orm import Session



def new_user(db_sess: Session, data):
    user = User()
    user.username = data['username']
    user.email = data['email']
    user.password = data['password']
    db_sess.add(user)
