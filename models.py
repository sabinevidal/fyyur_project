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
from datetime import datetime
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
    
    # relationships between Venue and show
    show_ven = db.relationship('Show', cascade="all,delete", backref='Venue', lazy=True)

    ## created time for recent entries attempt
    #created = db.Column(db.DateTime, default=datetime.now())


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(JSON)
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(200), nullable=True)
    upcoming_shows = db.Column(db.Integer, nullable=True)
    past_shows = db.Column(db.Integer, nullable=True)
    
    # relationships between Artist and Show
    show_art = db.relationship('Show', cascade="all,delete", backref='Artist', lazy=True)

    ## created time for recent entries attempt
    # created = db.Column(db.DateTime, default=datetime.now())

   
class Show(db.Model):
    __tablename__ = 'Show'

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False) 

