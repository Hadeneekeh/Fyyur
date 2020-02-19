#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  venue_areas = [a_venue.venue_area for a_venue in Venue.query.distinct(Venue.city, Venue.state).all()]
  for venue_area in venue_areas:
    venue_area['venues'] = [
      a_venue.venue_obj for a_venue in Venue.query.filter_by(city=venue_area['city'], state=venue_area['state']).all()
    ]
    data = venue_areas
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  all_venue = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  total_venue = len(all_venue)
  response={
    "count": total_venue,
    "data": all_venue
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  a_venue = Venue.query.get(venue_id)
  data = a_venue.venue_obj
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    data = request.form  #enteries from form
    a_venue = Venue(
      name=data['name'],
      city=data['city'],
      state=data['state'],
      address=data['address'],
      phone=data['phone'],
      genres=data.getlist('genres'),
      facebook_link=data['facebook_link']
    )
    existing_venue = Venue.query.filter_by(name=data['name'], city=data['city'], state=data['state']).all()
    if existing_venue:
      flash('Venue ' + data['name'] + ' already exist in ' + data['city'] + '.')
    else:
      db.session.add(a_venue)
      db.session.commit()
      flash('Venue ' + data['name'] + ' was successfully listed!')
  except expression as identifier:
     flash('An error occurred. Venue ' + data[name] + ' could not be listed.')
     db.session.rollback()
     print(sys.exc_info())
  finally:
    db.session.close()  
  return render_template('pages/home.html')
  
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.get(id=get_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  all_artist = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  total_artist = len(all_artist)
  response={
    "count": total_artist,
    "data": all_artist
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  an_artist = Artist.query.get(artist_id)
  data = an_artist.artist_obj
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist_detail = Artist.query.get(artist_id)
  artist={
    "id": artist_id,
    "name": artist_detail.name,
    "genres": artist_detail.genres,
    "city": artist_detail.city,
    "state": artist_detail.state,
    "phone": artist_detail.phone,
    "facebook_link": artist_detail.facebook_link
  }
  form = ArtistForm(**artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  try:
    artist.name = form.name.data,
    artist.genres = request.form.getlist('genres'),
    artist.city = form.city.data,
    artist.state = form.state.data,
    artist.phone = form.phone.data,
    artist.facebook_link = form.facebook_link.data
    db.session.commit()
    flash('Artist was successfully added')
  except expression as identifier:
    flash('Something went wrong')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_detail = Venue.query.get(venue_id)
  venue={
    "id": venue_id,
    "name": venue_detail.name,
    "genres": venue_detail.genres,
    "address": venue_detail.address,
    "city": venue_detail.city,
    "state": venue_detail.state,
    "phone": venue_detail.phone,
    "facebook_link": venue_detail.facebook_link
  }
  form = VenueForm(**venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  try:
    venue.name = form.name.data,
    venue.genres = form.genres.data,
    venue.address = form.address.data,
    venue.city = form.city.data,
    venue.state = form.state.data,
    venue.phone = form.phone.data,
    venue.facebook_link = form.facebook_link.data
    db.session.commit()
    flash('Venue was successfully added')
  except expression as identifier:
    flash('Something went wrong')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    data = request.form  #enteries from form
    an_artist = Artist(
      name=data['name'],
      genres=data.getlist('genres'),
      city=data['city'],
      state=data['state'],
      phone=data['phone'],
      facebook_link=data['facebook_link']
    )
    existing_artist = Artist.query.filter_by(name=data['name'], city=data['city'], state=data['state']).all()
    if existing_artist:
      flash('Artist ' + data['name'] + ' already exist in ' + data['city'] + '.')
    else:
      db.session.add(an_artist)
      db.session.commit()
      flash('Artist ' + data['name'] + ' was successfully listed!')
  except expression as identifier:
     flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
     db.session.rollback()
     print(sys.exc_info())
  finally:
    db.session.close()  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = [s.show_data for s in Show.query.all()]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    data = request.form  #enteries from form
    a_show = Show(
      artist_id=data['artist_id'],
      venue_id=data['venue_id'],
      start_time=data['start_time']
    )
    db.session.add(a_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except expression as identifier:
     flash('An error occurred. Show could not be listed.')
     db.session.rollback()
     print(sys.exc_info())
  finally:
    db.session.close()  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
