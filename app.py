import logging, os, ConfigParser, sys
from flask import Flask, url_for, request
from quotes import Quote
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import simplejson as json
import random

# Setup Logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
filehandler = logging.FileHandler("hoggy-search.log")
filehandler.setLevel(logging.INFO)
streamhandler = logging.StreamHandler()

log.addHandler(filehandler)
log.addHandler(streamhandler)

# Read config
log.debug("Reading config")
env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')))
config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])
log.info("Config loaded")

# Setup DB 
log.debug("Loading database")
config_folder = os.path.dirname(os.path.realpath(sys.argv[1]))
if config.get('db','type') != 'mysql':
    sqlite_file = os.path.join(config_folder, config.get('db', 'file'))
    engine = create_engine('sqlite:///%s' % sqlite_file)
log.info("Database loaded")

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    body = Column(String(200))

    @classmethod
    def get(cls, id):
        return session.query(cls).get(id)

    @classmethod
    def get_random(cls):
        rand = random.randrange(1, session.query(cls).count());
        return session.query(cls).get(rand)

    @classmethod
    def list(cls, search):
        if search:
            return session.query(cls).filter(cls.body.like('%' + search + '%')).all()
        else:
            return session.query(cls).all()

    @classmethod
    def search(cls, search):
        return session.query(cls).filter(cls.body.like('%' + search + '%')).all()


app = Flask(__name__, static_folder='static')
app.debug = False

@app.route("/")
def index():
    quote = Quote.get_random()
    tmpl = env.get_template('main.html')
    return tmpl.render(id=quote.id, body=quote.body)


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        quotes = Quote.list(request.args.get('query'))
        tmpl = env.get_template('search.html')
        return tmpl.render(quotes=quotes)
    else:
        term = request.form['query']
        results = Quote.search(term)
        to_return = []
        for result in results:
            to_return.append({
                "id":result.id,
                "body": result.body
            })
        return json.dumps(to_return)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
