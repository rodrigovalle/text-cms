import flask
import redis
import yaml
import markdown
import markdown.extensions.toc as toc

import warnings
import os

content_path = 'content/'

app = flask.Flask(__name__)
db_login = {
    'host': 'db',  # host ip address
    'port': 6379,
    # 'password': 'password'
    'decode_responses': True
}

toc_extension = toc.TocExtension(baselevel=2)
markdown_parser = markdown.Markdown(
    extensions=[toc_extension, 'markdown.extensions.smarty'],
    output_format='html5'
)


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

    subdirs = [e.path for e in os.scandir(content_path) if e.is_dir()]

    for subdir in subdirs:
        with os.scandir(subdir) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith('.md'):
                    load_article(entry.path)


def load_article(filepath):
    db = get_db()

    metadata, md = parse_yaml(filepath)
    html = parse_markdown(md)
    article_name, _ = os.path.basename(filepath).rsplit('.', 1)
    db.set(article_name + ':html', html)
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


def parse_markdown(text):
    return markdown_parser.convert(text)


if __name__ == '__main__':
    with app.app_context():
        load_articles()

    app.run(
        host='0.0.0.0',
        port=5000
    )
