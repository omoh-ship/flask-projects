from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


# DB MODEL
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)


# WTFORM
class RateMovieForm(FlaskForm):
    new_rating = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    new_review = StringField('Your Review')
    submit = SubmitField('Done')


class AddMovie(FlaskForm):
    movie_title = StringField("Movie Title")
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    # all_movies = db.session.query(Movie).all()
    all_movies = db.session.query(Movie).order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = RateMovieForm()
    present_movie_id = request.args.get('movie_id')
    movie_to_be_updated = Movie.query.get(present_movie_id)
    if request.method == 'POST' and form.validate_on_submit():
        movie_to_be_updated.rating = form.new_rating.data
        movie_to_be_updated.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_to_be_updated, form=form)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    present_movie_id = request.args.get('movie_id')
    movie_to_be_deleted = Movie.query.get(present_movie_id)
    db.session.delete(movie_to_be_deleted)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovie()
    movie_title = form.movie_title.data

    params = {
        'api_key': 'api key',
        'query': movie_title,
    }

    if request.method == 'POST':
        response = requests.get('https://api.themoviedb.org/3/search/movie', params=params)
        data = response.json()['results']
        return render_template('select.html', results=data)
    return render_template('add.html', form=form)


@app.route("/select", methods=['GET', 'POST'])
def details():
    movie_id = request.args.get('movie_id')
    movie_details_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    params = {
        'api_key': 'api key',
        'movie_id': movie_id,
    }
    response = requests.get(movie_details_url, params=params)
    data = response.json()
    print(data)
    db.create_all()
    movie = Movie(
        title=data['original_title'],
        year=data['release_date'][:4],
        description=data['overview'],
        img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}",
        rating=0,
        ranking=3,
        review="Eww")
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
