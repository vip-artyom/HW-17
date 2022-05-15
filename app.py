from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

db = SQLAlchemy(app)
api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")

        movies = db.session.query(Movie)
        if director_id:
            movies = movies.filter(Movie.director_id == director_id)
        if genre_id:
            movies = movies.filter(Movie.genre_id == genre_id)
        movies = movies.all()
        return movies_schema.dump(movies), 200

    def post(self):
        req_json = request.get_json()
        new_movie = Movie(**req_json)

        db.session.add(new_movie)
        db.session.commit()
        db.session.close()

        return "Фильм добавлен", 201


@movie_ns.route('/<int:mid>')
class MoviesView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return f"Нет фильма с  id {mid}", 404
        movies_by_id = Movie.query.filter(Movie.id == mid).all()
        return movies_schema.dump(movies_by_id), 200

    def put(self, mid):
        req_json = request.get_json()
        movie = Movie.query.get(mid)
        if not movie:
            return f"Нет фильма с  id {mid}", 404
        movie.id = req_json["id"]
        movie.title = req_json["title"]
        movie.description = req_json["description"]
        movie.trailer = req_json["trailer"]
        movie.year = req_json["year"]
        movie.rating = req_json["rating"]
        movie.genre_id = req_json["genre_id"]
        movie.director_id = req_json["director_id"]

        db.session.add(movie)
        db.session.commit()
        db.session.close()

        return "Фильм заменен", 204

    def delete(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return f"Нет фильма с  id {mid}", 404
        db.session.delete(movie)
        db.session.commit()
        db.session.close()
        return "Фильм удален из базы", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director).all()
        return directors_schema.dump(directors), 200

    def post(self):
        req_json = request.get_json()
        new_director = Director(**req_json)

        db.session.add(new_director)
        db.session.commit()
        db.session.close()

        return "Режиссер добавлен", 201


@director_ns.route('/<int:did>')
class DirectorsView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        if not director:
            return f"Нет режиссера с id {did}", 404
        directors_by_id = Director.query.filter(Director.id == did).all()
        return directors_schema.dump(directors_by_id), 200

    def put(self, did):
        req_json = request.get_json()
        director = Director.query.get(did)
        if not director:
            return f"Нет режиссера с id {did}", 404
        director.id = req_json["id"]
        director.name = req_json["name"]

        db.session.add(director)
        db.session.commit()
        db.session.close()
        return "Режиссер заменен", 204

    def delete(self, did):
        director = Director.query.get(did)
        if not director:
            return f"Нет режиссера с  id {did}", 404
        db.session.delete(director)
        db.session.commit()
        db.session.close()
        return "Режиссер удален из базы", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        genres = db.session.query(Genre).all()
        return genres_schema.dump(genres), 200

    def post(self):
        req_json = request.get_json()
        new_genre = Genre(**req_json)

        db.session.add(new_genre)
        db.session.commit()
        db.session.close()

        return "Жанр добавлен", 201


@genre_ns.route('/<int:gid>')
class GenresView(Resource):
    def get(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return f"Нет жанра с id {gid}", 404
        genres_by_id = Genre.query.filter(Genre.id == gid).all()
        return genres_schema.dump(genres_by_id), 200

    def put(self, gid):
        req_json = request.get_json()
        genre = Genre.query.get(gid)
        if not genre:
            return f"Нет жанра с id {gid}", 404
        genre.id = req_json["id"]
        genre.name = req_json["name"]

        db.session.add(genre)
        db.session.commit()
        db.session.close()
        return "Жанр заменен", 204

    def delete(self, gid):
        genre = Genre.query.get(gid)
        if not genre:
            return f"Нет жанра с id {gid}", 404
        db.session.delete(genre)
        db.session.commit()
        db.session.close()
        return "Жанр удален из базы", 204


if __name__ == '__main__':
    app.run(debug=True)
