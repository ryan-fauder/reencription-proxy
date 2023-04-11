from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
    
    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='')
    
    from Model import db
    migrate = Migrate(app, db)
    db.init_app(app)
    return app



app = create_app(config_filename="config")
if __name__=="__main__":
    app.run(debug=True)
