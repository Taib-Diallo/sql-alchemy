import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route('/')
def home():
    return (
        f'Available Routes:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/&#139;start> (Make sure to put the date inplace of the start date. Format has to be year-month-day ex. 2016-05-24. Also, date cannot be after 2017-08-23)<br/>'
        f'/api/v1.0/&#139;start>/&#139;end> (Make sure to put the start date in place of start and the end date in place of end to get a range of data. Format has to be year-month-day ex. 2016-05-24. Also, date cannot be after 2017-08-23 )<br/>'
    )

@app.route('/api/v1.0/precipitation')
def prcp_results():
    # Create our session (link) from Python to the DB`      `
    session = Session(engine)

    # Query all prcp & date data for 1 year
    year_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Convert list of tuples into normal dictionary
    date_prcp = []
    for date, prcp in year_query:
        prcp_dict = {}
        prcp_dict[date] = prcp
        date_prcp.append(prcp_dict)

    #return jsonified dictionary
    return jsonify(date_prcp)



@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    # query of all station names
    station_names = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    session.close()

    #convert list of tuples into normal list
    station_list = []
    for id, station, name, latitude, longitude, elevation in station_names:
        station_dict = {}
        station_dict['id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        station_list.append(station_dict)

    return jsonify(station_list)



@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    # query for the date and temp for most active station 
    tobs_query = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()

    session.close()

    tobs_list = []
    for station, date, tobs1 in tobs_query:
        tobs_dict = {}
        tobs_dict['station'] = station
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs1
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    
    tobs1_query = session.query(Measurement.date, func.min (Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()


    session.close()
    tobs_list = []
    for date, min, max, avg in tobs1_query:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['TMIN'] = min
        tobs_dict['TMAX'] = max
        tobs_dict['TAVG'] = avg
        tobs_list.append(tobs_dict)
    
   
    
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>/<end>')
def range(start, end):
    session = Session(engine)
    
    tobs1_query = session.query(Measurement.date, func.min (Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()


    session.close()
    tobs_list = []
    for date, min, max, avg in tobs1_query:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['TMIN'] = min
        tobs_dict['TMAX'] = max
        tobs_dict['TAVG'] = avg
        tobs_list.append(tobs_dict)
    
   
    
    return jsonify(tobs_list)




    
if __name__ == '__main__':
    app.run(debug=True)