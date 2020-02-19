from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)


migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(220)))
    image_link = db.Column(db.String(500), default='https://images.unsplash.com/photo-1543900694')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500), default='We are on the lookout for a local artist to play every two weeks. Please call us.')
    shows = db.relationship('Show', backref='venue', lazy=True)


    @property
    def venue_area(self):
      return {
        'city': self.city,
        'state': self.state,
      }

    @property
    def venue_obj(self):
      today = datetime.datetime.now()
      previous_shows = db.session.query(Show).filter(
        Show.start_time < today,
        Show.venue_id == self.id).all()
      past_shows = [
        {
          'artist_id': show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in previous_shows
      ]
      next_shows = db.session.query(Show).filter(
        Show.start_time > today,
        Show.venue_id == self.id).all()
      upcoming_shows =[
        {
          'artist_id': show.artist.id,
          'artist_name': show.artist.name,
          'artist_image_link': show.artist.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in next_shows
      ]
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'address': self.address,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
      }

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(220)))
    image_link = db.Column(db.String(500), default='https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80')
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(500), default='A rare talent who can do awesome stuff with musical instrument.')
    shows = db.relationship('Show', backref='artist', lazy=True)

    @property
    def artist_obj(self):
      today = datetime.datetime.now()
      previous_shows = db.session.query(Show).filter(Show.start_time < today, Show.artist_id == self.id).all()
      past_shows = [
        {
          'venue_id': show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in previous_shows
      ]
      next_shows = db.session.query(Show).filter(
        Show.start_time > today,
        Show.venue_id == self.id).all()
      upcoming_shows =[
        {
          'venue_id': show.venue.id,
          'venue_name': show.venue.name,
          'venue_image_link': show.venue.image_link,
          'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for show in next_shows
      ]
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
      }

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    start_time = db.Column(db.DateTime())

    @property
    def show_data(self):
      a = Artist.query.get(self.artist_id)
      v = Venue.query.get(self.venue_id)
      return {
        'artist_name': a.name,
        'artist_image_link': a.image_link,
        'venue_name': v.name,
        'venue_id': self.venue_id,
        'artist_id': self.artist_id,
        'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M")
      }
