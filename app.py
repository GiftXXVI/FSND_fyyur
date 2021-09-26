#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import truediv
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import ERROR, Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
from datetime import datetime
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self) -> str:
        return f"<city {self.id}> {self.name}, {self.genres}, {self.city}, {self.state}, {self.address}, {self.phone}, {self.website_link}, {self.image_link}, {self.facebook_link}, {self.seeking_talent}, {self.seeking_description}"

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'))
    start_time = db.Column(db.DateTime, nullable=False)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    citystates = db.session.query(
        Venue.state, Venue.city).distinct(Venue.state, Venue.city).all()
    now = datetime.now()
    for cstate in citystates:
        venues = db.session.query(
            Venue.id, Venue.name).filter_by(city=cstate[1], state=cstate[0]).all()
        data.append({
            "city": cstate[1],
            "state": cstate[0],
            "venues": [{"id": venue.id, "name": venue.name, "num_upcoming_shows": Show.query.filter_by(venue_id=venue.id).filter(Show.start_time > now).count()} for venue in venues]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    error = True
    try:
        # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
        # search for Hop should return "The Musical Hop".
        # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
        venues = Venue.query.filter(Venue.name.ilike(
            '%{rsearch}%'.format(rsearch=request.form.get('search_term', ''))))
        data = []

        for venue in venues:
            data.append({"id": venue.id, "name": venue.name,
                         "num_upcoming_shows": 0})
        response = {
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        abort(500)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # show venue, venue shows and venue artist
    try:
        db_venue = Venue.query.filter_by(id=venue_id).first()
        venue = {
            "id": venue_id,
            "name": db_venue.name,
            "genres": db_venue.genres.split(','),
            "address": db_venue.address,
            "city": db_venue.city,
            "state": db_venue.state,
            "phone": db_venue.phone,
            "website_link": db_venue.website_link,
            "facebook_link": db_venue.facebook_link,
            "seeking_talent": db_venue.seeking_talent,
            "seeking_description": db_venue.seeking_description,
            "image_link": db_venue.image_link,
            "past_shows": [],
            "upcoming_shows": [],
            "past_shows_count": 0,
            "upcoming_shows_count": 0,
        }
        return render_template('pages/show_venue.html', venue=venue)
    except:
        abort(404)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    error = False
    try:
        name = request.form.get('name')
        genres = ','.join(request.form.getlist('genres'))
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        website_link = request.form.get('website_link')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        seeking_talent = True if request.form.get(
            'seeking_talent') == 'y' else False
        seeking_description = request.form.get('seeking_description')
        venue = Venue(name=name, genres=genres, city=city, state=state, address=address, phone=phone,
                      website_link=website_link, image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully created!')

        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        flash('An error occurred. Venue {rname} could not be listed.'.format(
            rname=request.form['name']))
        error = True
    finally:
        db.session.close()
        if error:
            abort(500)
        else:
            return redirect(url_for('venues'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    response = {'url': '', 'error': 0}
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    if not error:
        response['url'] = '/venues'
    else:
        response['error'] = 1
    return jsonify(response)
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    try:
        # TODO: replace with real data returned from querying the database
        artists = Artist.query.all()
        data = [{"id": artist.id, "name": artist.name} for artist in artists]
        return render_template('pages/artists.html', artists=data)
    except:
        abort(500)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    try:
        artists = Artist.query.filter(Artist.name.ilike(
            '%{rname}%'.format(rname=request.form.get('search_term', ''))))
        data = [{"id": artist.id, "name": artist.name, "num_upcoming_shows": 0}
                for artist in artists]
        # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
        # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
        # search for "band" should return "The Wild Sax Band".
        response = {
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        abort(500)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        # shows the artist page with the given artist_id
        # TODO: replace with real artist data from the artist table, using artist_id
        db_artist = Artist.query.filter_by(id=artist_id).first()

        data = {
            "id": db_artist.id,
            "name": db_artist.name,
            "genres": db_artist.genres.split(','),
            "city": db_artist.city,
            "state": db_artist.state,
            "phone": db_artist.phone,
            "website": db_artist.website_link,
            "facebook_link": db_artist.facebook_link,
            "seeking_venue": db_artist.seeking_venue,
            "seeking_description": db_artist.seeking_description,
            "image_link": db_artist.image_link,
            "past_shows": [{
                "venue_id": 1,
                "venue_name": "The Musical Hop",
                "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
                "start_time": "2019-05-21T21:30:00.000Z"
            }],
            "upcoming_shows": [],
            "past_shows_count": 1,
            "upcoming_shows_count": 0,
        }
        return render_template('pages/show_artist.html', artist=data)
    except:
        abort(404)
#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    error = False
    try:
        form = ArtistForm()
        db_artist = Artist.query.filter_by(id=artist_id).first()
        artist = {
            "id": db_artist.id,
            "name": db_artist.name,
            "genres": db_artist.genres.split(','),
            "city": db_artist.city,
            "state": db_artist.state,
            "phone": db_artist.phone,
            "website_link": db_artist.website_link,
            "facebook_link": db_artist.facebook_link,
            "seeking_venue": db_artist.seeking_venue,
            "seeking_description": db_artist.seeking_description,
            "image_link": db_artist.image_link
        }
        form.genres.data = artist['genres']
        form.state.data = artist['state']
    except:
        flash(f'An error occurred. Artist id {artist_id} could not be found.')
        error = True
    finally:
        if not error:
            # TODO: populate form with fields from artist with ID <artist_id>
            return render_template('forms/edit_artist.html', form=form, artist=artist)
        else:
            abort(404)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        # TODO: take values from the form submitted, and update existing
        # # artist record with ID <artist_id> using the new attributes
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = request.form['name']
        artist.genres = ','.join(request.form.getlist('genres'))
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.website_link = request.form['website_link']
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.seeking_venue = True if request.form.get(
            'seeking_venue') == "y" else False
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully modified!')
    except:
        db.session.rollback()
        error = True
        message = sys.exc_info()[1]
        flash('An error occured. Artist {rname} could not be modified.'.format(
            rname=request.form['name']))
    finally:
        db.session.close()
        if not error:
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    error = False
    try:
        form = VenueForm()
        # TODO: populate form with values from venue with ID <venue_id>
        db_venue = Venue.query.filter_by(id=venue_id).first()
        venue = {
            "id": venue_id,
            "name": db_venue.name,
            "genres": db_venue.genres.split(','),
            "address": db_venue.address,
            "city": db_venue.city,
            "state": db_venue.state,
            "phone": db_venue.phone,
            "website_link": db_venue.website_link,
            "facebook_link": db_venue.facebook_link,
            "seeking_talent": db_venue.seeking_talent,
            "seeking_description": db_venue.seeking_description,
            "image_link": db_venue.image_link
        }
        form.genres.data = venue['genres']
        form.state.data = venue['state']
    except:
        flash(f'An error occurred. Venue id {venue_id} could not be found.')
        error = True
    finally:
        if not error:
            return render_template('forms/edit_venue.html', form=form, venue=venue)
        else:
            abort(404)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = request.form.get('name')
        venue.genres = ','.join(request.form.getlist('genres'))
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.website_link = request.form.get('website_link')
        venue.image_link = request.form.get('image_link')
        venue.facebook_link = request.form.get('facebook_link')
        venue.seeking_talent = True if request.form.get(
            'seeking_talent') == "y" else False
        venue.seeking_description = request.form.get('seeking_description')
        db.session.commit()
        flash('Venue {rname} was successfully modified!'.format(
            rname=request.form['name']))
    except:
        db.session.rollback()
        error = True
        message = sys.exc_info()[1]
        flash('An error occured. Venue {rname} could not be modified.'.format(
            rname=request.form['name']))
    finally:
        db.session.close()
        if not error:
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            abort(500)

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        genres = ','.join(request.form.getlist('genres'))
        website_link = request.form['website_link']
        image_link = request.form['image_link']
        facebook_link = request.form['facebook_link']
        seeking_venue = True if request.form.get(
            'seeking_venue') == 'y' else False
        seeking_description = request.form.get('seeking_description')
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                        website_link=website_link, image_link=image_link, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
        db.session.refresh(artist)
        data = artist
        # on successful db insert, flash success
        flash(f'Artist {data.name} was successfully listed!')
    except:
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        message = sys.exc_info()[1]
        flash('An error occured. Artist {rname} was not created.'.format(
            rname=request.form['name']))
    finally:
        db.session.close()
    if not error:
        return render_template('pages/home.html')
    else:
        abort(500)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    try:
        # displays list of shows at /shows
        # TODO: replace with real venues data.
        shows = Show.query.join('artist').join('venue').all()
        data = []
        for show in shows:
            data.append({
                "venue_id": show.venue.id,
                "venue_name": show.venue.name,
                "artist_id": show.artist.id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")
            })
        return render_template('pages/shows.html', shows=data)
    except:
        abort(500)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        # called to create new shows in the db, upon submitting new show listing form
        # TODO: insert form data as a new Show record in the db, instead
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']
        show = Show(artist_id=artist_id, venue_id=venue_id,
                    start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
        if not error:
            # on successful db insert, flash success
            flash('Show was successfully listed!')
            return render_template('pages/home.html')
        else:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            flash('An error occured. The show was not created.')
            abort(500)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
