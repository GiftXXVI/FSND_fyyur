
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#SQL: CREATE TABLE venue(id integer PRIMARY KEY, name varchar, genres varchar(120), city varchar(120), state varchar(120),
# address varchar(120), phone varchar(120), website_link varchar(120), image_link varchar(120), facebook_link varchar(120),
# seeking_talent boolean NOT NULL, seeking_description varchar(120));

class Venue(db.Model):

    """
    A model class used to represent a Venue
    ...

    Attributes
    ----------
    id : int
        the venue's primary key
    name : str
        the name of the venue
    genres : str
        the list of genres preferred by the venue
    city : str
        the city where the venue is located
    state : str
        the state where the venue is located
    address : str
        the address where the venue is located
    phone : str
        the phone number of the venue
    state : str
        the state where the venue is located
    website_link : str
        the link to the venue's website
    image_link : str
        the link to an image of the venue
    facebook_link : str
        the link to the venue's facebook page
    seeking_talent : boolean
        indicator for whether the venue is seeking artists or not
    seeking_description:
        description of type of artists the venue is seeking
    """

    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    genres = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
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
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#SQL: CREATE TABLE artist(id integer PRIMARY KEY, name varchar, city varchar(120), state varchar(120), phone varchar(120),
# genres varchar(120), website_link varchar(120), image_link varchar(120), facebook_link varchar(120), seeking_venue boolean NOT NULL,
# seeking_description varchar);
class Artist(db.Model):
    
    """
    A model class used to represent an Artist
    ...

    Attributes
    ----------
    id : int
        the artist's primary key
    name : str
        the name of the artist
    genres : str
        the list of genres of the artist's music
    city : str
        the city where the artist resides
    state : str
        the state where the artist resides
    address : str
        the address where the artist resides
    phone : str
        the phone number of the artist
    state : str
        the state where the artist resides
    website_link : str
        the link to the artist's website
    image_link : str
        the link to an image of the artist
    facebook_link : str
        the link to the artist's facebook page
    seeking_talent : boolean
        indicator for whether the artist is seeking artists or not
    seeking_description:
        description of type of venues that the artist is seeking
    """

    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    website_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

#SQL: CREATE TABLE show(id integer PRIMARY KEY, artist_id integer, venue_id integer, start_time timestamp,
# CONSTRAINT show_artist FOREIGN KEY(artist_id) REFERENCES artist(id) ON DELETE CASCADE, 
# CONSTRAINT show_venue FOREIGN KEY(venue_id) REFERENCES venue(id) ON DELETE CASCADE);
class Show(db.Model):

    """
    A model class used to represent a Show
    ...

    Attributes
    ----------
    id : int
        the show's primary key
    artist_id : int
        the primary key of the artist
    venue_id : int
        the primary key of the venue
    start_time : datetime
        the show's starting time
    """

    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    db.UniqueConstraint(artist_id, venue_id, start_time, name='UX_Artist_Venue')