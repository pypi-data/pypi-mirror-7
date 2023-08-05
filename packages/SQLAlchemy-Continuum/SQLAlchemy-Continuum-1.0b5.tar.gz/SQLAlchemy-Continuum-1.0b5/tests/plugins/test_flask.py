from flask import Flask, url_for
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy, _SessionSignalEvents
from flexmock import flexmock

import sqlalchemy as sa
from sqlalchemy_continuum import make_versioned, remove_versioning
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_continuum.transaction import TransactionFactory
from tests import TestCase


class TestFlaskPlugin(TestCase):
    plugins = [FlaskPlugin()]
    transaction_cls = TransactionFactory()
    user_cls = 'User'

    def setup_method(self, method):
        TestCase.setup_method(self, method)
        self.app = Flask(__name__)
        self.app.secret_key = 'secret'
        self.app.debug = True
        self.setup_views()
        login_manager = LoginManager()
        login_manager.init_app(self.app)
        self.client = self.app.test_client()
        self.context = self.app.test_request_context()
        self.context.push()

        @login_manager.user_loader
        def load_user(id):
            return self.session.query(self.User).get(id)

    def teardown_method(self, method):
        TestCase.teardown_method(self, method)
        self.context.pop()
        self.context = None
        self.client = None
        self.app = None

    def login(self, user):
        """
        Log in the user returned by :meth:`create_user`.

        :returns: the logged in user
        """
        with self.client.session_transaction() as s:
            s['user_id'] = user.id
        return user

    def logout(self, user=None):
        with self.client.session_transaction() as s:
            s['user_id'] = None

    def create_models(self):
        TestCase.create_models(self)

        class User(self.Model):
            __tablename__ = 'user'
            __versioned__ = {
                'base_classes': (self.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)
        self.User = User

    def setup_views(self):
        @self.app.route('/')
        def index():
            article = self.Article()
            article.name = u'Some article'
            self.session.add(article)
            self.session.commit()
            return ''

    def test_versioning_inside_request(self):
        user = self.User(name=u'Rambo')
        self.session.add(user)
        self.session.commit()
        self.login(user)
        self.client.get(url_for('.index'))

        article = self.session.query(self.Article).first()
        tx = article.versions[-1].transaction
        assert tx.user.id == user.id


class TestFlaskPluginWithoutRequestContext(TestCase):
    plugins = [FlaskPlugin()]

    def create_models(self):
        TestCase.create_models(self)

        class User(self.Model):
            __tablename__ = 'user'
            __versioned__ = {
                'base_classes': (self.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)
        self.User = User

    def test_versioning_outside_request(self):
        user = self.User(name=u'Rambo')
        self.session.add(user)
        self.session.commit()


class TestFlaskPluginWithFlaskSQLAlchemyExtension(object):
    versioning_strategy = 'validity'

    def create_models(self):
        class User(self.db.Model):
            __tablename__ = 'user'
            __versioned__ = {
                'base_classes': (self.db.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255), nullable=False)

        class Article(self.db.Model):
            __tablename__ = 'article'
            __versioned__ = {
                'base_classes': (self.db.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))

        article_tag = sa.Table(
            'article_tag',
            self.db.Model.metadata,
            sa.Column(
                'article_id',
                sa.Integer,
                sa.ForeignKey('article.id'),
                primary_key=True,
            ),
            sa.Column(
                'tag_id',
                sa.Integer,
                sa.ForeignKey('tag.id'),
                primary_key=True
            )
        )

        class Tag(self.db.Model):
            __tablename__ = 'tag'
            __versioned__ = {
                'base_classes': (self.db.Model, )
            }

            id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)
            name = sa.Column(sa.Unicode(255))

        Tag.articles = sa.orm.relationship(
            Article,
            secondary=article_tag,
            backref='tags'
        )

        self.User = User
        self.Article = Article
        self.Tag = Tag

    def setup_method(self, method):
        # Mock the event registering of Flask-SQLAlchemy. Currently there is no
        # way of unregistering Flask-SQLAlchemy event listeners, hence the
        # event listeners would affect other tests.
        flexmock(_SessionSignalEvents).should_receive('register')

        self.db = SQLAlchemy()
        make_versioned()

        self.create_models()

        sa.orm.configure_mappers()

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.db.init_app(self.app)
        self.app.secret_key = 'secret'
        self.app.debug = True
        self.client = self.app.test_client()
        self.context = self.app.test_request_context()
        self.context.push()
        self.db.create_all()

    def teardown_method(self, method):
        remove_versioning()
        self.db.drop_all()
        self.context.pop()
        self.context = None
        self.client = None
        self.app = None

    def test_version_relations(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        self.db.session.add(article)
        self.db.session.commit()
        assert not article.versions[0].tags

    def test_single_insert(self):
        article = self.Article()
        article.name = u'Some article'
        article.content = u'Some content'
        tag = self.Tag(name=u'some tag')
        article.tags.append(tag)
        self.db.session.add(article)
        self.db.session.commit()
        assert len(article.versions[0].tags) == 1
