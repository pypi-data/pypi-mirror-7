tg2ext.express
==============

This is a CRUD controller which helps you to exposure your database tables via a HTTP RESTful interface quickly on TurboGears2,
helps you make your WEB pages access your database quickly via Ajax.

# For example

## With the following code in your TG app:

    from tg2ext.express import ExpressController

    class Writer(DeclarativeBase):
        __tablename__ = 'db_writers'
        #{ Columns
        id = Column(Integer, primary_key=True)
        firstname = Column(Unicode(64), nullable=False)
        lastname = Column(Unicode(64), nullable=False)
        gender = Column(Enum('Male', 'Female', name='wrtier_gender'), default='Male')
        birthday = Column(Date, nullable=True)
        description = Column(Text, nullable=True)
        created = Column(DateTime, default=func.NOW())
        #}
        fullname = column_property(firstname + " " + lastname)


    class Article(DeclarativeBase):
        __tablename__ = 'db_articles'

        #{ Columns
        id = Column(Integer, primary_key=True)
        title = Column(Unicode(256), nullable=False)
        keys = Column(Unicode(256), nullable=True)
        content = Column(Text, nullable=True)
        writer_id = Column(Integer, ForeignKey('db_writers.id'), nullable=False)
        created = Column(DateTime, default=func.NOW())
        #}
        writer = relation('Writer', backref='articles')


    class Comment(DeclarativeBase):
        __tablename__ = 'db_comments'
        #{ Columns
        id = Column(Integer, primary_key=True)
        comment = Column(Unicode(256), nullable=False)
        article_id = Column(Integer, ForeignKey('db_articles.id'), nullable=False)
        created = Column(DateTime, default=func.NOW())
        #}
        db_articles = relation('Article', backref='comments')

    class RootController(BaseController):
        # ...
        writer = ExpressController(model=model.Writer, dbsession=DBSession)
        article = ExpressController(model=model.Article, dbsession=DBSession)
        comment = ExpressController(model=model.Comment, dbsession=DBSession)

        # ...

## You will get your HTTP APIs for access writers, articles, comments:

### Writers:
        /writer/{$id|_schema|_aggregate}[?query&controles]
### Articles:
        /article/{$id|_schema|_aggregate}[?query&controles]
### Comments:
        /comment/{$id|_schema|_aggregate}[?query&controles]

### For get articles with writer_id==2:

GET /article/?writer_id=2&__include_fields=title,keys,created&__extend_fields=writer.firstname,writer.lastname

        {
          "__count": 2,
          "__limit": 50,
          "__model": "Article",
          "__ref": "/article/",
          "Article": [
            {
              "keys": "note,another",
              "writer": {
                "lastname": "SHEN",
                "id": 2,
                "firstname": "Fangze"
              },
              "title": "Test note2",
              "id": 3,
              "created": "2014-02-26 13:36:18"
            },
            {
              "keys": "test",
              "writer": {
                "lastname": "SHEN",
                "id": 2,
                "firstname": "Fangze"
              },
              "title": "Test note4",
              "id": 4,
              "created": "2014-02-26 13:36:18"
            }
          ],
          "__begin": 0,
          "__total": 2
        }

### For getting writer table schema:

GET /writer/_schema

        {
          "relationships": {
            "articles": {
              "field": [
                "db_articles.writer_id"
              ],
              "direction": "ONETOMANY",
              "target": "Article"
            }
          },
          "table": "Writer",
          "fields": {
            "description": {
              "primary_key": false,
              "nullable": true,
              "default": null,
              "doc": null,
              "unique": null,
              "type": "TEXT"
            },
            "firstname": {
              "primary_key": false,
              "nullable": false,
              "default": null,
              "doc": null,
              "unique": null,
              "type": "VARCHAR(64)"
            },
            "created": {
              "primary_key": false,
              "nullable": true,
              "default": "ColumnDefault(<sqlalchemy.sql.functions.Function at 0x528bb00; NOW>)",
              "doc": null,
              "unique": null,
              "type": "DATETIME"
            },
            "lastname": {
              "primary_key": false,
              "nullable": false,
              "default": null,
              "doc": null,
              "unique": null,
              "type": "VARCHAR(64)"
            },
            "birthday": {
              "primary_key": false,
              "nullable": true,
              "default": null,
              "doc": null,
              "unique": null,
              "type": "DATE"
            },
            "gender": {
              "primary_key": false,
              "nullable": true,
              "default": "ColumnDefault('Male')",
              "doc": null,
              "unique": null,
              "type": "VARCHAR(6)"
            },
            "id": {
              "primary_key": true,
              "nullable": false,
              "default": null,
              "doc": null,
              "unique": null,
              "type": "INTEGER"
            }
          }
        }

### For aggregations:

GET /article/_aggregate?__count=id&__group_by=writer_id

        {
          "__count": 2,
          "__model": "Article",
          "__ref": "/article/_aggregate",
          "__type": "Aggregation",
          "Article": [
            {
              "__count_id": 2,
              "writer_id": 1
            },
            {
              "__count_id": 2,
              "writer_id": 2
            }
          ],
          "__total": 2
        }

# HTTP API:

### Controle Params:

    __begin:
    __limit:
    __include_fields:
    __extend_fields:

### Query Lookups: ${field_name}__${lookup}=${value(s)}

    not
    contains
    startswith
    endswith
    in
    range
    lt
    lte
    gt
    gte
    year
    month
    day
    hour
    minute
    dow

### Aggregation functions:

    __count:
    __sum:
    __avg:
    __min:
    __max: