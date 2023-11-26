from flask import Flask, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import create_engine

#Eigen
from models import User, Base
from Forms import LoginForm, RegisterForm

#Todo: Kommentare erstellen
class IPTV(Flask):
    def __init__(self, name):
        super().__init__(name)
        
        
        self.route('/', methods=['GET'])(self.start)

        self.route('/login', methods=['GET', 'POST'])(self.login)
        self.route('/register', methods=['GET', 'POST'])(self.register)

        self.route('/list_videos', methods=['GET'])(self.list_videos)
        self.route('/video/<video_name>', methods=['GET'])(self.video)

    def start(self): 
        return render_template('start.html')
        
    def login(self):
        form = LoginForm()
        
        if form.validate_on_submit():
            user = DB.session.query(User).filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                session['user_id'] = user.id
                return redirect(url_for('list_videos'))
            else:
                return "Invalid username or password"
        return render_template('login.html', form=form)
    

    def register(self):
        form = RegisterForm()   
        if form.validate_on_submit():
            
            user = DB.session.query(User).filter_by(username=form.username.data).first()
            
            if(form.password.data != form.password_confirm.data):
                error_message = "Passwörter stimmen nicht überein. Bitte erneut eingeben."
                return render_template('registrierung.html', form=form, error_message=error_message)
            if not user:
                new_user = User(username=form.username.data, password_hash=generate_password_hash(form.password.data))
                DB.session.add(new_user)
                DB.session.commit()

                session['user_id'] = new_user.id
                return redirect(url_for('list_videos'))
            else:
                return "Benutzername bereits vergeben"
        return render_template('registrierung.html', form=form)
    


    def list_videos(self):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        video_files = [f for f in os.listdir('static') if f.endswith('.mp4')]
        return render_template('video_list.html', video_files=video_files)

    def video(self, video_name):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return render_template('video.html', video_name=video_name)



if __name__ == '__main__':
    app = IPTV(__name__)

    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
    DB = SQLAlchemy(app)

    if(not os.path.isfile("instance/users.db")):
        engine = create_engine("sqlite:///instance/users.db", echo=False)
        Base.metadata.create_all(engine)
    
    app.run(port=5000)
    #app.run(host= "0.0.0.0", port=5000)