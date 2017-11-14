import flask
import redis
import yaml

import warnings
import os

content_path = 'content/'
article_path = content_path + 'articles/'

app = flask.Flask(__name__)
db_login = {
    'host': 'db',  # host ip address
    'port': 6379,
    # 'password': 'password'
    'decode_responses': True
}


@app.route('/articles/<name>')
def show_article(name):
    db = get_db()
    title, author = db.hmget(name + ':metadata', 'title', 'author')
    text = db.get(name + ':text')
    return flask.render_template('article_layout.html',
                                 title=title, author=author, text=text)


def get_db():
    """Open a new database connection if one doesn't exist in app context"""
    if not hasattr(flask.g, 'redis_db'):
        flask.g.redis_db = redis.Redis(**db_login)
    return flask.g.redis_db


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
        yaml_it = iter(f.readline, '---\n')     # read until we reach separator
        metadata = yaml.load(''.join(yaml_it))  # parse yaml metadata
        text = f.read()                         # read rest of file

        if 'tags' in metadata:
            warnings.warn('Article tags not yet supported', stacklevel=2)
            del metadata['tags']

        return metadata, text


if __name__ == '__main__':
    with app.app_context():
        load_articles()

    app.run(
        host='0.0.0.0',
        port=5000
    )
