from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from sqlalchemy import create_engine

#Eigene Python Datein
from models import User, Base
from Forms import LoginForm, RegisterForm

class IPTV(Flask):
    ###Konstruktor
    def __init__(self, name):
        #Der Konstruktor der Parent Class wird ausgeführt 
        super().__init__(name)
        
        
        ##Die Routen werden definiert und die funktionen werden deklariert 
        #Startfenster
        self.route('/', methods=['GET'])(self.start)
        self.route('/#', methods=['GET'])(self.start_Loggedin)
        
        #sonderfunktionen 
        self.route('/Reload', methods=['GET'])(self.reload)
        self.route('/search', methods=['GET'])(self.search)

        #Anmelden,Registrierung, Abmelden
        self.route('/Login', methods=['GET', 'POST'])(self.login)
        self.route('/Registrierung', methods=['GET', 'POST'])(self.register)
        self.route('/Abmelden', methods=['GET'])(self.Abmelden)

        #video_player
        self.route('/video', methods=['GET'])(self.video_player)

    ### Zusatz Funktionen
    ## Videos und die bilder werden in einem geordneten Dictionary kombiniert 
    def video_imgae_loader(self):
        #Die videos und die bilder werden in listen gespeichert und mit .split(".")[0] werden die . endungen entfernt
        video_images = {}
        video_files = [video.split(".")[0] for video in os.listdir('static/Videos') if video.endswith(".mp4")]
        images = [image.split(".")[0] for image in os.listdir('static/Videos/Image_Videos')]
        #Videos und Bilder werden zu einem Dictionary zusammengefasst und die endungen werden wieder hinzugefügt
        for i in range(len(video_files)):
            if video_files[i] in images:
                image_index = images.index(video_files[i])
                video_images[str(video_files[i]) + ".mp4"] = "static/Videos/Image_Videos/" + str(images[image_index]) + ".JPG"
            else:
                video_images[str(video_files[i])  + ".mp4"] = "static/Videos/Image_Videos/None.png"

        return video_images


    ###Die funktionen der Routen werden Definiert
    ##Funktion für das Startfenster 
    def start(self): 
        if 'user_id' in session:
            return redirect(url_for('start_Loggedin'))

        video_images = self.video_imgae_loader()
        return render_template('Home.html', data=video_images)
    
    ##Funktion wenn man bereits angemeldet ist 
    def start_Loggedin(self):
        video_images = self.video_imgae_loader()
        return render_template("Home_logged_in.html", data=video_images)

    ##Die Funktionalität der Abmelden seite wird Definiert
    #Der Benutzer wird Abgemeldet und es wird die Start seite geladen
    def Abmelden(self):
        session.pop('user_id')
        return redirect(url_for('start'))

    ##Die Funktionalität der Login seite wird Definiert  
    #Die Anmeldedaten werden mit der Datenbank verglichen; Bei einem Erfolgreichen Anmelden wird eine session erstellt
    #Bei einem Falschen Passwort oder benutzernamen wird ein Fehler ausgeben
    def login(self):
        form = LoginForm()
        
        if form.validate_on_submit():
            user = DB.session.query(User).filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                session['user_id'] = user.id
                return redirect(url_for('start'))
            else:
                error_message = "Das Password oder der Benutzername ist Falsch"
                return render_template('Login.html', form=form, error_message=error_message)
        return render_template('Login.html', form=form)
    

    ##Die Funktionalität der Registrierung seite wird Definiert  
    #Die Anmeldedaten werden in die Datenbank eingetragen
    #Wenn das Password nicht übereinstimmt oder wenn der benutzernamen schon vorhanden ist wird ein fehler ausgegeben
    def register(self):
        form = RegisterForm()   
        if form.validate_on_submit():
            
            user = DB.session.query(User).filter_by(username=form.username.data).first()

            #Überprüfung ob die Passwörter übereinstimmen
            if(form.password.data != form.password_confirm.data):
                error_message = "Passwörter stimmen nicht überein. Bitte erneut eingeben."
                return render_template('Registrierung.html', form=form, error_message=error_message)
            
            #Überprüfung ob der Benutzernamen schon vorhanden ist
            if not user:
                new_user = User(username=form.username.data, password_hash=generate_password_hash(form.password.data))
                DB.session.add(new_user)
                DB.session.commit()

                session['user_id'] = new_user.id
                return redirect(url_for('start'))
            else:
                error_message = "Benutzername bereits vergeben"
                return render_template('Registrierung.html', form=form, error_message=error_message)
        return render_template('Registrierung.html', form=form)
    

    ##Die Funktionalität um die Videos abzuspielen wird Definiert
    #Es wird die variable die in der URL steht ausgelsen und das Video wird abgespielt
    def video_player(self):
        if 'user_id' not in session:
            return redirect(url_for('start'))
        #Damit wird die Variable die man auf der startseite gesetzt hat ausgelesen
        video_name = request.args.get('video_name')
        return render_template('video.html', video_name="static/Videos/"+str(video_name))
    
    ##Die Funktionalität um die Start seite neu zu laden wird Definiert
    #Es wird die seite neu geladen
    def reload(self):
        return redirect(url_for('start'))

    ##Die Funktionalität für die Suchfunktion wird Definiert
    #Es wird die Variable aus der URl ausgelsen und die Videos werden dem entsprechend angepasst
    def search(self):
        video_images = self.video_imgae_loader()
        query = request.args.get("query")
        search_video_images = {key: value for key, value in video_images.items() if key.startswith(query)}
        if 'user_id' in session:
            return render_template("Home_logged_in.html", data=search_video_images,query_value= query)
        return render_template('Home.html', data=search_video_images, query_value= query)

###Start das Hauptprogramms
if __name__ == '__main__':
    app = IPTV(__name__)

    #Zur Random verschlüsselung der derzeitigen Session
    app.config['SECRET_KEY'] = os.urandom(24)
    #Flask verbindung mit der Datenbank
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
    DB = SQLAlchemy(app)

    #Erstellung der Datenbank wenn diese noch nicht vorhanden ist
    #Datenbank Model in models.py
    if(not os.path.isfile("instance/users.db")):
        engine = create_engine("sqlite:///instance/users.db", echo=False)
        Base.metadata.create_all(engine)
    
    #Anwendung wird auf dem Lokal host auf Port 5000 freigegben
    app.run(port=5000)
    #app.run(host= "0.0.0.0", port=5000)