import sqlalchemy as sa
from sqlalchemy_utils import dependent_objects, get_referencing_foreign_keys
from tests import TestCase


class TestDependentObjects(TestCase):
    def create_models(self):
        class User(self.Base):
            __tablename__ = 'user'
            id = sa.Column(sa.Integer, primary_key=True)
            first_name = sa.Column(sa.Unicode(255))
            last_name = sa.Column(sa.Unicode(255))

        class Article(self.Base):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, primary_key=True)
            author_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
            owner_id = sa.Column(
                sa.Integer, sa.ForeignKey('user.id', ondelete='SET NULL')
            )

            author = sa.orm.relationship(User, foreign_keys=[author_id])
            owner = sa.orm.relationship(User, foreign_keys=[owner_id])

        class BlogPost(self.Base):
            __tablename__ = 'blog_post'
            id = sa.Column(sa.Integer, primary_key=True)
            owner_id = sa.Column(
                sa.Integer, sa.ForeignKey('user.id', ondelete='CASCADE')
            )

            owner = sa.orm.relationship(User)

        self.User = User
        self.Article = Article
        self.BlogPost = BlogPost

    def test_returns_all_dependent_objects(self):
        user = self.User(first_name=u'John')
        articles = [
            self.Article(author=user),
            self.Article(),
            self.Article(owner=user),
            self.Article(author=user, owner=user)
        ]
        self.session.add_all(articles)
        self.session.commit()

        deps = list(dependent_objects(user))
        assert len(deps) == 3
        assert articles[0] in deps
        assert articles[2] in deps
        assert articles[3] in deps

    def test_with_foreign_keys_parameter(self):
        user = self.User(first_name=u'John')
        objects = [
            self.Article(author=user),
            self.Article(),
            self.Article(owner=user),
            self.Article(author=user, owner=user),
            self.BlogPost(owner=user)
        ]
        self.session.add_all(objects)
        self.session.commit()

        deps = list(
            dependent_objects(
                user,
                (
                    fk for fk in get_referencing_foreign_keys(self.User)
                    if fk.ondelete == 'RESTRICT' or fk.ondelete is None
                )
            ).limit(5)
        )
        assert len(deps) == 2
        assert objects[0] in deps
        assert objects[3] in deps


class TestDependentObjectsWithCompositeKeys(TestCase):
    def create_models(self):
        class User(self.Base):
            __tablename__ = 'user'
            first_name = sa.Column(sa.Unicode(255), primary_key=True)
            last_name = sa.Column(sa.Unicode(255), primary_key=True)

        class Article(self.Base):
            __tablename__ = 'article'
            id = sa.Column(sa.Integer, primary_key=True)
            author_first_name = sa.Column(sa.Unicode(255))
            author_last_name = sa.Column(sa.Unicode(255))
            __table_args__ = (
                sa.ForeignKeyConstraint(
                    [author_first_name, author_last_name],
                    [User.first_name, User.last_name]
                ),
            )

            author = sa.orm.relationship(User)

        self.User = User
        self.Article = Article

    def test_returns_all_dependent_objects(self):
        user = self.User(first_name=u'John', last_name=u'Smith')
        articles = [
            self.Article(author=user),
            self.Article(),
            self.Article(),
            self.Article(author=user)
        ]
        self.session.add_all(articles)
        self.session.commit()

        deps = list(dependent_objects(user))
        assert len(deps) == 2
        assert articles[0] in deps
        assert articles[3] in deps
