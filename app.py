import flask
import redis
import os

app = flask.Flask('prime')
article_path = 'articles/'
db_login = {
    'host': 'localhost', # host ip address
    'port': 6379,
    'password': 'password' # secure password choice
}


def main():
    db = redis.Redis(**db_login)


if __name__ == '__main__':
    main()

