import flask
import redis
import yaml

import warnings
import os

app_name = 'prime'
content_path = 'content/'
article_path = content_path + 'articles/'

app = flask.Flask(app_name)
db_login = {
    'host': 'localhost', # host ip address
    'port': 6379,
    #'password': 'password'
    'decode_responses': True
}


@app.route('/articles/<name>')
def show_article(name):
    db = get_db()
    title, author = db.hmget(name + ':metadata', 'title', 'author')
    text = db.get(name + ':text')
    return '<h1>{}</h1>\n<h3>by {}</h3>\n{}'.format(title, author, text)


def get_db():
    """Open a new database connection if one doesn't exist in our app context"""
    if not hasattr(flask.g, 'redis_db'):
        flask.g.redis_db = redis.Redis(**db_login)
    return flask.g.redis_db


@app.cli.command('load')
def load_articles():
    """Load our articles into Redis"""
    db = get_db()

    with os.scandir(path=article_path) as it:
        for entry in it:
            if entry.is_file() and entry.name.endswith('.md'):
                metadata, text = parse_yaml(entry.path)
                article_name, _ = entry.name.rsplit('.', 1)
                db.set(article_name + ':text', text)
                db.hmset(article_name + ':metadata', metadata)


def parse_yaml(filepath):
    """Parse an article file and return (metadata, text)"""
    filename = os.path.basename(filepath)

    with open(filepath) as f:
        documents = yaml.load_all(f)
        metadata = next(documents)
        text = next(documents)

        if type(metadata) is not dict or type(text) is not str:
            raise SyntaxError('Malformed article \'{}\''.format(filename))

        if 'tags' in metadata:
            warnings.warn('Article tags not yet supported', stacklevel=2)
            del metadata['tags']

        try:
            # this should fail
            # a properly formatted article has only two YAML documents
            next(documents)
        except StopIteration:
            return metadata, text

        raise SyntaxError('Malformed article \'{}\''.format(filename))
