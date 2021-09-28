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
import models
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
# from https://stackoverflow.com/questions/9692962/flask-sqlalchemy-import-context-issue/9695045#9695045
db.init_app(app)
migrate = Migrate(app, db)


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
    now = datetime.now()
    # also db.desc(), from https://github.com/pallets/flask-sqlalchemy/issues/451
    artists = Artist.query.order_by(Artist.id.desc()).limit(10).all()
    # SQL: SELECT * FROM artist LIMIT 10 ORDER BY id DESC;
    venues = Venue.query.order_by(Venue.id.desc()).limit(10).all()
    # SQL: SELECT * FROM venue LIMIT 10 ORDER BY id DESC;
    artist_data = [{"id": artist.id, "name": artist.name}
                   for artist in artists]
    venue_data = [{"id": venue.id, "name": venue.name, "num_upcoming_shows": Show.query.filter_by(
        venue_id=venue.id).filter(Show.start_time > now).count()} for venue in venues]
    # SQL: SELECT COUNT(*) FROM show WHERE venue_id={VENUE_ID} AND start_time={START_TIME};
    return render_template('pages/home.html', artist_data=artist_data, venue_data=venue_data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    citystates = db.session.query(
        Venue.state, Venue.city).distinct(Venue.state, Venue.city).all()
    # SQL: SELECT DISTINCT state, city FROM venue;
    now = datetime.now()
    for cstate in citystates:
        venues = db.session.query(
            Venue.id, Venue.name).filter_by(city=cstate[1], state=cstate[0]).all()
        # SQL: SELECT id, name FROM venue WHERE city='{CITY}' AND state={STATE};
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
        # from https://stackoverflow.com/questions/40535547/flask-sqlalchemy-filter-by-value-or-another/40546355
        
        if len(str(request.form.get('search_term','')).split(',')) > 1:
            rsearch = str(request.form.get('search_term','')).split(',')
            csearch = f'%{rsearch[0]}%'
            ssearch = f'%{rsearch[1]}%'
            venues = Venue.query.filter(Venue.city.ilike(csearch) | Venue.state.ilike(ssearch)).all()
        else:
            param = f'%{request.form.get('search_term', '')}%'
            venues = Venue.query.filter(Venue.name.ilike(
            param) | Venue.city.ilike(param) | Venue.state.ilike(param)).all()
        
        # SQL: SELECT * FROM venue WHERE name LIKE '%{SEARCH}%';
        data = []
        now = datetime.now()
        data = [{"id": venue.id, "name": venue.name, "num_upcoming_shows": Show.query.filter_by(
            venue_id=venue.id).filter(Show.start_time > now).count()} for venue in venues]
        # SQL: SELECT * FROM show WHERE venue_id={VENUE_ID} AND start_time > NOW();
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
        now = datetime.now()
        past_shows = Show.query.filter_by(
            venue_id=venue_id).filter(Show.start_time < now).join('artist').all()
        # SQL: SELECT * FROM show WHERE venue_id={VENUE_ID} AND start_time < NOW();
        upcoming_shows = Show.query.filter_by(
            venue_id=venue_id).filter(Show.start_time > now).join('artist').all()
        # SQL: SELECT * FROM show WHERE venue_id={VENUE_ID} AND start_time > NOW();
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
            "past_shows": [{"artist_id": show.artist.id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link, "start_time": show.start_time} for show in past_shows],
            "upcoming_shows": [{"artist_id": show.artist.id, "artist_name": show.artist.name, "artist_image_link": show.artist.image_link, "start_time": show.start_time} for show in past_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
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
    form = VenueForm()
    error = False

    try:
        if form.validate():
            name = form.name.data
            genres = ','.join(form.genres.data)
            city = form.city.data
            state = form.state.data
            address = form.address.data
            phone = form.phone.data
            website_link = form.website_link.data
            image_link = form.image_link.data
            facebook_link = form.facebook_link.data
            seeking_talent = form.seeking_talent.data
            seeking_description = form.seeking_description.data
            venue = Venue(name=name, genres=genres, city=city, state=state, address=address, phone=phone,
                          website_link=website_link, image_link=image_link, facebook_link=facebook_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
            # SQL: INSERT INTO venue (name, genres, city, state, address, phone, website_link, image_link, facebook_link, seeking_talent, seeking_description)
            # VALUES({NAME},{GENRES},{CITY},{STATE},{ADDRESS},{PHONE},{WEBSITE_LINK},{IMAGE_LINK},{FACEBOOK_LINK},{SEEKING_TALENT},{SEEKING_DESCRIPTION})
            db.session.add(venue)
            db.session.commit()
            db.session.refresh(venue)
            data = venue
            flash(f'Venue {data.name} was successfully created!')
        else:
            flash(f'The input had the following errors: {form.errors}')
            error = True
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    except:
        db.session.rollback()
        if Venue.query.filter_by(name=form.name.data).count() > 0:
            flash(f'{form.name.data} already exists.')
        else:
            flash(f'Venue {form.name.data} could not be listed.')
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
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    response = {'url': '', 'error': 0}
    try:
        Venue.query.filter_by(id=venue_id).delete()
        # SQL: DELETE FROM venue WHERE id={ID};
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

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
        # SQL: SELECT * FROM artist;
        data = [{"id": artist.id, "name": artist.name} for artist in artists]
        return render_template('pages/artists.html', artists=data)
    except:
        abort(500)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    try:
        if len(str(request.form.get('search_term','')).split(',')) > 1:
            rsearch = str(request.form.get('search_term','')).split(',')
            csearch = f'%{rsearch[0]}%'
            ssearch = f'%{rsearch[1]}%'
            artists = Artist.query.filter(Artist.city.ilike(csearch) | Artist.state.ilike(ssearch)).all()
        else:
            param = f'%{request.form.get('search_term', '')}%'
            artists = Artist.query.filter(Artist.name.ilike(
                param) | Artist.city.ilike(param) | Artist.state.ilike(param)).all()
        # SQL: SELECT * FROM artist WHERE name LIKE '%{SEARCH}%';
        now = datetime.now()
        data = [{"id": artist.id, "name": artist.name, "num_upcoming_shows": Show.query.filter_by(artist_id=artist.id).filter(Show.start_time > now).count()}
                for artist in artists]
        # SQL: SELECT * FROM show WHERE artist_id={ARTIST_ID} AND start_time > NOW();

        response = {
            "count": len(data),
            "data": data
        }
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        abort(500)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    try:
        db_artist = Artist.query.filter_by(id=artist_id).first()
        # SQL: SELECT * FROM artist WHERE id={ID} LIMIT 1;
        now = datetime.now()
        past_shows = Show.query.filter_by(artist_id=artist_id).filter(
            Show.start_time < now).join('venue').all()
        # SQL: SELECT * FROM show INNER JOIN venue ON show.venue_id = venue.id WHERE artist_id = {ARTIST_ID} AN start_time < NOW();
        upcoming_shows = Show.query.filter_by(artist_id=artist_id).filter(
            Show.start_time > now).join('venue').all()
        # SQL: SELECT * FROM show INNER JOIN venue ON show.venue_id = venue.id WHERE artist_id = {ARTIST_ID} AN start_time > NOW();

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
            "past_shows": [{"venue_id": show.venue.id, "venue_name": show.venue.name, "venue_image_link": show.venue.image_link, "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")} for show in past_shows],
            "upcoming_shows": [{"venue_id": show.venue.id, "venue_name": show.venue.name, "venue_image_link": show.venue.image_link, "start_time": show.start_time.strftime("%Y-%m-%dT%H:%M:%S")} for show in upcoming_shows],
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }
        return render_template('pages/show_artist.html', artist=data)
    except:
        abort(404)
#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    error = False
    try:
        form = ArtistForm()
        db_artist = Artist.query.filter_by(id=artist_id).first()
        # SQL: SELECT * FROM artist WHERE id={ID} LIMIT 1;
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
            return render_template('forms/edit_artist.html', form=form, artist=artist)
        else:
            abort(404)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm()
    try:
        if form.validate():
            artist = Artist.query.filter_by(id=artist_id).first()
            # SQL: SELECT * FROM artist WHERE id={ARTIST_ID} LIMIT 1;
            artist.name = form.name.data
            artist.genres = ','.join(form.genres.data)
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website_link = form.website_link.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            # UPDATE artist SET name={NAME}, genres={GENRES}, city={CITY}, state={STATE}, phone={PHONE},website_link={WEBSITE_LINK},
            # facebook_link={FACEBOOK_LINK}, image_link={IMAGE_LINK}, seeking_venue={SEEKING_VENUE}, seeking_description={SEEKING_DESCRIPTION}
            # WHERE id={ID};
            db.session.commit()
            flash(f'Artist {form.name.data} was successfully modified!')
        else:
            flash(f'The input had the following errors: {form.errors}')
            error = True
    except:
        db.session.rollback()
        error = True
        flash(f'Artist {form.name.data} could not be modified.')
    finally:
        db.session.close()
        if not error:
            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            abort(500)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    error = False
    try:
        form = VenueForm()
        db_venue = Venue.query.filter_by(id=venue_id).first()
        # SQL: SELECT * FROM venue WHERE id={ID} LIMIT 1;
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
        flash(f'Venue id {venue_id} could not be found.')
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
    form = VenueForm()
    try:
        if form.validate():
            venue = Venue.query.filter_by(id=venue_id).first()
            # SQL: SELECT * FROM venue WHERE id={ID} LIMIT 1;
            venue.name = form.name.data
            venue.genres = ','.join(form.genres.data)
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.website_link = form.website_link.data
            venue.image_link = form.image_link.data
            venue.facebook_link = form.facebook_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            # UPDATE venue SET name={NAME}, genres={GENRES}, city={CITY}, state={STATE}, address={ADDRESS}, phone={PHONE},
            # website_link={WEBSITE_LINK}, image_link={IMAGE_LINK}, facebook_link={FACEBOOK_LINK}, seeking_talent={SEEKING_TALENT},
            # seeking_description = {SEEKING_DESCRIPTION} WHERE id={ID};
            db.session.commit()
            flash(f'Venue {form.name.data} was successfully modified!')
        else:
            flash(f'The input had the following errors: {form.errors}')
            error = True
    except:
        db.session.rollback()
        error = True
        flash(f'Venue {form.name.data} could not be modified.')
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
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    form = ArtistForm()
    try:
        if form.validate():
            name = form.name.data
            city = form.city.data
            state = form.state.data
            phone = form.phone.data
            genres = ','.join(form.genres.data)
            website_link = form.website_link.data
            image_link = form.image_link.data
            facebook_link = form.facebook_link.data
            seeking_venue = form.seeking_venue.data
            seeking_description = form.seeking_description.data
            artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                            website_link=website_link, image_link=image_link, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
            db.session.add(artist)
            # SQL: INSERT INTO artist(name, city, state, phone, genres, website_link, image_link, facebook_link, seeking_venue, seeking_description)
            # VALUES({NAME},{CITY},{STATE},{PHONE},{GENRES},{WEBSITE_LINK},{IMAGE_LINK},{FACEBOOK_LINK},{SEEKING_VENUE},{SEEKING_DESCRIPTION});
            db.session.commit()
            db.session.refresh(artist)
            data = artist

            # on successful db insert, flash success
            flash(f'Artist {data.name} was successfully listed!')
        else:
            flash(f'The input had the following errors: {form.errors}')
            error = True
    except:
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

        if Artist.query.filter_by(name=form.name.data).count() > 0:
            flash(f'{form.name.data} already exists.')
        else:
            flash(
                f'An error occurred. Artist {form.name.data} could not be listed.')
    finally:
        db.session.close()
    if not error:
        return redirect(url_for('artists'))
    else:
        abort(500)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    try:
        shows = Show.query.join('artist').join('venue').all()
        # SQL: SELECT * FROM show INNER JOIN artist ON show.artist_id = artist.id INNER JOIN venue ON show.venue_id = venue.id;
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
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False
    form = ShowForm()
    try:
        if form.validate():
            artist_id = form.artist_id.data
            venue_id = form.venue_id.data
            start_time = form.start_time.data
            show = Show(artist_id=artist_id, venue_id=venue_id,
                        start_time=start_time)
            db.session.add(show)
            # SQL: INSERT INTO show(artist_id, venue_id, start_time) VALUES({ARTIST_ID}, {VENUE_ID}, {START_TIME});
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        else:
            flash(f'The input had the following errors: {form.errors}')
            error = True
    except:
        db.session.rollback()
        error = True
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('An error occured. The show was not created.')
    finally:
        db.session.close()
        if not error:
            return redirect(url_for('shows'))
        else:
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
