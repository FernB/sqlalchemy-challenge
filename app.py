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
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/<start></br>"
        f"/api/v1.0/<start><end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all passenger names"""
    # Query all passengers
    lastdate = session.query(func.max(Measurement.date))
    enddate = dt.datetime.strptime(lastdate[0][0], '%Y-%m-%d').date()
    startdate = enddate.replace(enddate.year - 1)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= startdate).filter(Measurement.prcp.isnot(None)).all()
    
    session.close()

    # Convert list of tuples into normal list
    precip = dict(results)

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    results = session.query(Measurement.station.label('station'),Station.name, func.count(Measurement.station).label('count')).group_by(Measurement.station).order_by(desc('count')).join(Station, Station.station==Measurement.station).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
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
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    lastdate = session.query(func.max(Measurement.date))
    enddate = dt.datetime.strptime(lastdate[0][0], '%Y-%m-%d').date()
    startdate = enddate.replace(enddate.year - 1)
    tobs_counts = session.query(Measurement.station.label('station'), func.count(Measurement.tobs).label('count')).group_by(Measurement.station).filter(Measurement.tobs.isnot(None)).order_by(desc('count')).subquery()

    maxtobs = session.query(func.max(tobs_counts.c.count)).scalar()

    maxtobstation = session.query(tobs_counts.c.station).filter(tobs_counts.c.count == maxtobs).scalar()
    maxtobstation

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= startdate).filter(Measurement.tobs.isnot(None)).filter(Measurement.station == maxtobstation ).all()


    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    tobs = dict(results)


    return jsonify(tobs)


@app.route("/api/v1.0/<start>/<end>")
def tobsdate(start,end=dt.date.today()):
    
    
    # Create our session (link) from Python to the DB
    
    session = Session(engine)

    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers



        
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # maxtobs = session.query(func.max(tobs_counts.c.count)).scalar()

    # maxtobstation = session.query(tobs_counts.c.station).filter(tobs_counts.c.count == maxtobs).scalar()
    # maxtobstation

    # results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= startdate).filter(Measurement.tobs.isnot(None)).filter(Measurement.station == maxtobstation ).all()
    session.close()
    obslist = []
    for tmin, tavg, tmax in results:
        obs_dict = {}
        obs_dict["TMIN"] = tmin
        obs_dict["TAVG"] = tavg
        obs_dict["TMAX"] = tmax
        obslist.append(obs_dict)


    return jsonify(obslist)


      

    # # Create a dictionary from the row data and append to a list of all_passengers
    # tobs = dict(results)



    # return jsonify(tobs)







if __name__ == '__main__':
    app.run(debug=True)
