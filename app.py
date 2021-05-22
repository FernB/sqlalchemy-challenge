# Dependancies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
# Base route welcome and list available routes

def welcome():
    """List all available api routes."""
    return (
        "<h1>Welcome to the Hawaii Weather Sation API</h1><br><br>"
        "Available Routes:<br/>"
        "<ul>"
        "<li>/api/v1.0/precipitation</li>"
        "- for the last 12 months of precipitation data in all stations"
        "<li>/api/v1.0/stations</li>"
        " - for a list of active stations"
        "<li>/api/v1.0/tobs</li>"
        "- for a list of temperature observations from the most active station"
        "<li>/api/v1.0/< start ></li>"
        "- for the minimum, maxmimum and average temperature observations prior to the start date as yyyymmdd"
        "<li>/api/v1.0/< start >/< end ></li>"
        "- for the minimum, maxmimum and average temperature observations betwen the start and end dates as yyyymmdd"
        "</ul>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session from Python to hawaii db
    session = Session(engine)

    # Query to find last date of data set
    lastdate = session.query(func.max(Measurement.date))
    enddate = dt.datetime.strptime(lastdate[0][0], '%Y-%m-%d').date()
    # Get start date as 1 year prior to end date
    startdate = enddate.replace(enddate.year - 1)
    #Query to get precipiation observations between start and end dates
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= startdate).filter(Measurement.prcp.isnot(None)).all()
    
    session.close()

    # Convert list of tuples into dictionary
    precip = dict(results)
    # return as json
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create session from Python to hawaii db
    session = Session(engine)

    # Query all stations
    results = session.query(Measurement.station.label('station'),Station.name, func.count(Measurement.station).label('count')).group_by(Measurement.station).order_by(desc('count')).join(Station, Station.station==Measurement.station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of stations
    stationslist = []
    for sid, name, obs in results:
        station_dict = {}
        station_dict["Station ID"] = sid
        station_dict["Station Name"] = name
        station_dict["Number of Observations"] = obs
        stationslist.append(station_dict)


    return jsonify(stationslist)


@app.route("/api/v1.0/tobs")
def stationtobs():
    # Create session from Python to hawaii db
    session = Session(engine)

    # Query to find last date of data set
    lastdate = session.query(func.max(Measurement.date))
    enddate = dt.datetime.strptime(lastdate[0][0], '%Y-%m-%d').date()
    # Calculate 1 year from last date
    startdate = enddate.replace(enddate.year - 1)
    # Sub query to get count of temperature observations per station
    tobs_counts = session.query(Measurement.station.label('station'), func.count(Measurement.tobs).label('count')).group_by(Measurement.station).filter(Measurement.tobs.isnot(None)).order_by(desc('count')).subquery()
    # Query to get station with most number of observations
    maxtobs = session.query(func.max(tobs_counts.c.count)).scalar()

    maxtobstation = session.query(tobs_counts.c.station).filter(tobs_counts.c.count == maxtobs).scalar()
    maxtobstation

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= startdate).filter(Measurement.tobs.isnot(None)).filter(Measurement.station == maxtobstation ).all()


    session.close()

    #turns list to dictionary
    tobs = dict(results)


    return jsonify(tobs)



@app.route("/api/v1.0/<start>")
def tobsdate(start):
    
    # Create session from Python to hawaii db
    
    session = Session(engine)

 
    # Query min, max and average temperature observations from start date onwards



        
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    # 
    session.close()

    #list of observations
    obslist = []
    for tmin, tavg, tmax in results:
        obs_dict = {}
        obs_dict["TMIN"] = tmin
        obs_dict["TAVG"] = tavg
        obs_dict["TMAX"] = tmax
        obslist.append(obs_dict)

    #returns list as json
    return jsonify(obslist)




@app.route("/api/v1.0/<start>/<end>")
def tobsdates(start,end):
    
    
    # Create session from Python to hawaii db
    
    session = Session(engine)

    # Query max, min, average temeperature observations between start and end date

        
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

 
    session.close()
    obslist = []
    for tmin, tavg, tmax in results:
        obs_dict = {}
        obs_dict["TMIN"] = tmin
        obs_dict["TAVG"] = tavg
        obs_dict["TMAX"] = tmax
        obslist.append(obs_dict)

    return jsonify(obslist)



if __name__ == '__main__':
    app.run(debug=True)
