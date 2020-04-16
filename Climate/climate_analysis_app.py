# 1. import Flask and other dependancies

from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt

#create engine
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


# 3. Define static routes
@app.route("/")
def Welcome():
    # list all the available api routes
    return (
        f"Hawaii Climate Analysis!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"  
    )


# Defining the functional routes
#1. Getting that dates and precipitation values of last year

@app.route("/api/v1.0/precipitation")
def precipitation():

# Create our session (link) from Python to the DB
    session = Session(engine)

    date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    rain_totals = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date > date_year_ago).\
        order_by(Measurement.date).all()

# Convert the query results to a dictionary using date as the key and prcp as the value.
    
    prcp_data = []
    for date, precipitation in rain_totals:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict['precipitation'] =precipitation
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)   


    session.close()


# getting list of all station names

@app.route(f"/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_names = session.query(Station.name).all()


    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_names))

    return jsonify(all_stations)

    session.close()

# Query the dates and temperature observations of the most active station for the last year of data.




# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route(f"/api/v1.0/tobs")
def temperature():

    session = Session(engine)

    date_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    active_stations = session.query(Measurement.station,func.count(Measurement.station))\
               .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    temp_obs = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == active_stations[0][0]).\
        filter(Measurement.date > date_year_ago).\
        order_by(Measurement.date).all()

    session.close()

    return jsonify(temp_obs)


# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/<start>")
def temperatures_start(start):

    session = Session(engine)
   
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
         filter(Measurement.date >= start).all()

    session.close()
    
    # Convert list of tuples into normal list
    temperatures_start = list(np.ravel(results))
    print(results)
    return jsonify(temperatures_start)

@app.route("/api/v1.0/<start>/<end>")
def temperatures_start_end(start,end):

    session = Session(engine)
   
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
         filter(Measurement.date >= start).\
         filter(Measurement.date <=end).all()

    session.close()
    
    # Convert list of tuples into normal list
    temperatures_start_end = list(np.ravel(results))
    print(results)
    return jsonify(temperatures_start_end)


if __name__ == "__main__":
    app.run(debug=True)

