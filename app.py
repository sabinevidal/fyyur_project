# ----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSON
import sys
from sqlalchemy import desc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SECRET KEY'] = 'secret key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
db.create_all()

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable=True)
    genres = db.Column(JSON)
    seeking_talent = db.Column(db.Boolean, nullable=True)
    seeking_description = db.Column(db.String(200), nullable=True)
    upcoming_shows = db.Column(db.Integer, nullable=True)
    past_shows = db.Column(db.Integer, nullable=True)
    past_shows_count = db.Column(db.Integer)
    
    # created time
    created = db.Column(db.DateTime, default=datetime.now())
    
    # relationships between Venue and show
    show_ven = db.relationship('Show', backref='Venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(JSON)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    upcoming_shows = db.Column(db.Integer, nullable=True)
    past_shows = db.Column(db.Integer, nullable=True)

    # created time
    created = db.Column(db.DateTime, default=datetime.now())
    
    # relationships between Artist and Show
    show_art = db.relationship('Show', backref='Artist', lazy=True)

   
class Show(db.Model):
    __tablename__ = 'Show'

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
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
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/', methods=['GET', 'POST', 'DELETE'])
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # Getting list of states and cities
    venue_groups = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    print(venue_groups)
    result = []
    # Group venues by city and state
    for venue_group in venue_groups:
        city_name = venue_group[0]
        city_state = venue_group[1]
        filtered = db.session.query(Venue).filter(Venue.city == city_name, Venue.state == city_state)
        group = {
            "city": city_name,
            "state": city_state,
            "venues": []
        }
        venues = filtered.all()
        # List venues in the city/state group
        for venue in venues:
            print(venue.id)
            if venue.city == group['city'] and venue.state == group['state']:
                group['venues'].append({
                    "id": venue.id,
                    "name": venue.name,
            })
        result.append(group)
    return render_template('pages/venues.html', areas=result) 


#  Search Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Get users search input
    search_term = request.form.get('search_term', '')

    # Apply filter for name, city and state
    venues = db.session.query(Venue).filter(Venue.name.ilike('%{}%'.format(search_term))).all()
    # Appending details of searched venue to response
    response = {
        "count": 0,
        "data": []
    }
    # Iterates through venues and appends venue details to search response
    for venue in venues:
        # calculate upcoming shows for venue
        num_upcoming_shows = 0
        shows = Show.query.filter_by(venue_id=venue.id).all()
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1
        response['data'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })
     
    response['count'] = len(response['data'])
    return render_template('pages/search_venues.html', results=response, search_term=search_term)

#  Show Individual Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # Retrieve all venues
    venue = Venue.query.filter_by(id=venue_id).first()

    # Retrive all shows for a particular venue
    shows = Show.query.filter_by(venue_id=venue.id).all()

    # Return upcoming shows
    def upcoming_shows():
        upcoming = []
        # If show is in future, add details
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": str(show.start_time)
                })
        return upcoming
                
    # Return past shows
    def past_shows():
        past = []
        
        #If show in past, add details
        for show in shows:
            if show.start_time <= datetime.now():
                past.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": str(show.start_time)
                })
        return past
    
    # Details for given venue
    details = {           
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows())
    }

    return render_template('pages/show_venue.html', venue=details)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Create venue with user input
    # Return: If a venue is created redirect to home page and flash success message, 
    #   if fails then redirect to create form with fail message
    try:
        form = VenueForm()
        name = form.name.data
        city = form.city.data
        state = form.state.data
        address = form.address.data
        phone = form.phone.data
        facebook_link = form.facebook_link.data
        website = form.website.data
        genres = form.genres.data
        image_link = form.image_link.data
        # Checking if venue is seeking an artist
        seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        seeking_description = form.seeking_description.data

        # Create new venue from data
        venue = Venue(name=name,city=city, state=state, address=address, 
                        phone=phone, facebook_link=facebook_link, website=website,
                        genres=genres, image_link=image_link, 
                        seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
                
    except Exception as e:
        db.session.rollback()
        print(sys.exc_info())
        flash('A database insertion error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        print(e)
    finally:
        db.session.close()
       
    return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------
#TODO: Get button working
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try: 
        # get venue, delete it, commit
        venue = Venue.query.get(venue_id)
        name = Venue.name
        
        # if len(venue.shows) != 0:
        #     flash("Watch out, this venue has shows linked to it!")
        #     return redirect('/venues/<venue_id>/shows')
        # Venue.query.filter_by(id == venue_id).delete()
        print(venue)
        db.session.delete(venue)
        db.session.commit()
        
        #flash if successful
        flash('Venue ' + name + 'was successfully deleted.')
        return render_template('/venues/')
    except: 
        print("Oh dear! ", sys.exc_info()[0], "occured.")
        
        db.session.rollback()
        flash("An error occured. Venue " + name + "wasn't deleted.")
    finally:
        db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
 
    return redirect('/venues/')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = db.session.query(Artist).all()
    result = []
    for artist in artists:
        result.append({
            "id": artist.id,
            "name": artist.name
        })

    return render_template('pages/artists.html', artists=result)

#  Show Individual Artist
# ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Retrieve all artists
    artist = Artist.query.filter_by(id=artist_id).first()

    # Retrive all shows for a particular venue
    shows = Show.query.filter_by(artist_id=artist_id).all()

    # Return upcoming shows
    def upcoming_shows():
        upcoming = []
        # If show is in future, add details
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "start_time": str(show.start_time)
                })
        return upcoming
                
    # Return past shows
    def past_shows():
        past = []
        
        #If show in past, add details
        for show in shows:
            if show.start_time <= datetime.now():
                past.append({
                    "venue__id": show.venue__id,
                    "venue__name": show.venue_.name,
                    "start_time": str(show.start_time)
                })
        return past
    
    # Details for given artist
    details = {           
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows())
    }

    return render_template('pages/show_artist.html', artist=details)

#  Search artists
# ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # Get users search input
    search_term = request.form.get('search_term', '')

    # Apply filter for artist name
    artists = db.session.query(Artist).filter(Artist.name.ilike('%{}%'.format(search_term))).all()
    # Appending details of searched artist to response
    response = {
        "count": 0,
        "data": []
    }
    #
    for artist in artists:
        # calculate upcoming shows for artist
        num_upcoming_shows = 0
        shows = Show.query.filter_by(artist_id=artist.id).all()
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1
        response['data'].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows
        })
     
    response['count'] = len(response['data'])
 
    return render_template('pages/search_artists.html', results=response, search_term=search_term)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    
    try:
        form = ArtistForm()
        name = form.name.data 
        city = form.city.data
        state = form.state.data
        phone = form.phone.data
        facebook_link = form.facebook_link.data
        website = form.website.data
        genres = form.genres.data
        image_link = form.image_link.data
        # Checking if artist is seeking venue
        seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        seeking_description = form.seeking_description.data

        #create new artist from data
        artist = Artist(name=name, city=city, state=state, phone=phone, 
                            facebook_link=facebook_link, website=website, 
                            image_link=image_link, seeking_venue=seeking_venue, 
                            seeking_description=seeking_description, genres=genres)
    
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')   
                
    except Exception as e:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('A database insertion error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        print(sys.exc_info())
        print(e)
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    
    form = ArtistForm()
  
    # get artist by ID
    artist = Artist.query.filter_by(id=artist_id).first()
  
    # artist data
    artist={
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }
  
    # TODO: set placeholders in form to current data
    form.name.process_data(artist['name'])
    form.city.process_data(artist['city'])
    form.state.process_data(artist['state'])
    form.genres.process_data(artist['genres'])
    form.phone.process_data(artist['phone'])
    form.website.process_data(artist['website'])
    form.facebook_link.process_data(artist['facebook_link'])
    form.seeking_venue.process_data(artist['seeking_venue'])
    form.seeking_description.process_data(artist['seeking_description'])
    form.image_link.process_data(artist['image_link'])

  
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    try:
        form = ArtistForm()
        # get venue by ID
        artist = Artist.query.filter_by(id=artist_id).first()

        # load form data from user input
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.genres = form.genres.data
        artist.phone = form.phone.data
        artist.website = form.website.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        # commit changes, flash success message
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except: 
        db.session.rollback()
        flash('A post error occurred. Artist ' + request.form['name'] + ' couldn\'t be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try: 
        form = VenueForm()
  
        # get venue by ID
        venue = Venue.query.filter_by(id=venue_id).first()
    
        # venue data
        venue={
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link
        }
    
        # populate form with current values from venue with ID <venue_id>
        form.name.process_data(venue['name'])
        form.city.process_data(venue['city'])
        form.state.process_data(venue['state'])
        form.address.process_data(venue['address'])
        form.genres.process_data(venue['genres'])
        form.phone.process_data(venue['phone'])
        form.website.process_data(venue['website'])
        form.facebook_link.process_data(venue['facebook_link'])
        form.seeking_talent.process_data(venue['seeking_talent'])
        form.seeking_description.process_data(venue['seeking_description'])
        form.image_link.process_data(venue['image_link'])
    
    except:
        flash('A get error occurred. Venue ' + request.form['name'] + ' couldn\'t be updated.')
    
    return render_template('forms/edit_venue.html', form=form, venue=venue)



@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try: 
        form = VenueForm()
        # get venue by ID
        venue = Venue.query.filter_by(id=venue_id).first()

        # load form data from user input
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.genres = form.genres.data
        venue.phone = form.phone.data
        venue.website = form.website.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data
        # commit changes, flash success message
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except: 
        db.session.rollback()
        flash('A post error occurred. Venue ' + request.form['name'] + ' couldn\'t be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))




#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
    shows = db.session.query(Show).all()
    result = []
    
    # Get artist and venue info for each show
    for show in shows:
        result.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    return render_template('pages/shows.html', shows=result)

#  Create Shows
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # Create show with user input
    # Return: If a show is created redirect to home page and flash success message, 
    #   if fails then redirect to create form with fail message
    form = ShowForm(request.form)
    try:
        new_show = Show(
            artist_id=request.form.get("artist_id"),
            venue_id=request.form.get("venue_id"),
            start_time=request.form.get("start_time")
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
                
    except Exception as e:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
        print(sys.exc_info())
        print(e)
    finally:
        db.session.close()
       
    return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Most recent venues and artists
#----------------------------------------------------------------------------#

@app.route('/recent')
def recent_adds():
    
    #call artists
    artists = db.session.query(Artist).all()
    #create list of recent additions
    allrecent = []
    #Loop through artists and append result to allrecent list
    for artist in artists:
        allrecent.append({
             #select artists with the most recent creation times, limit at 5. 
            "recentArtist": artist.query.order_by(desc('created')).limit(5)
        })
    # return render_template('pages/home.html') 
   
    

# ----------------------------------------------------------------- 
# Error handlers
#  ----------------------------------------------------------------

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
