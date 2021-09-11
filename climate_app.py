# ---------------------- STEP 2: Climate APP

from flask import Flask, json, jsonify
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///./Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
HI_prcp_Measurement = Base.classes.measurement
HI_Station = Base.classes.station
session = Session(engine)

app = Flask(__name__) # the name of the file & the object (double usage)

# List all routes that are available.
@app.route("/")
def home():
    print("In & Out of Home section.")
    return (
        f"Welcome to the Climate API!<br/>"
        f"</br>"
        f"Available Routes:<br/>"
        f"<a href=http://127.0.0.1:5000/api/v1.0/precipitation>Precipitation</a><br/>"
        f"<a href=http://127.0.0.1:5000/api/v1.0/stations>Stations</a><br/>"
        f"<a href=http://127.0.0.1:5000/api/v1.0/tobs>Temps_Obs</a><br/>"
        f"<a href=http://127.0.0.1:5000/api/v1.0/start_date/>Start_Date</a><br/>"
        f"<a href=http://127.0.0.1:5000/api/v1.0/start_date/end_date/>Start_Date_AND_End_Date</a><br/>"
    )

# Return the JSON representation of your dictionary
@app.route('/api/v1.0/precipitation/')
def precipitation():
    print("In Precipitation section.")
    
    Last_Date = session.query(HI_prcp_Measurement.date).order_by(HI_prcp_Measurement.date.desc()).first().date
    One_Year_before = Last_Date.replace("2017", "2016")

    last_12_prcp = session.query(HI_prcp_Measurement.date, HI_prcp_Measurement.prcp).\
    filter(HI_prcp_Measurement.date >= One_Year_before).\
    filter(HI_prcp_Measurement.date <= Last_Date).\
    order_by(asc(HI_prcp_Measurement.date)).all()
    last_12_prcp = [a for *a, in last_12_prcp]
    last_12_prcp_dict = dict(last_12_prcp)
    
    print(f"Results for Precipitation - {last_12_prcp_dict}")
    print("Out of Precipitation section.")
    return jsonify(last_12_prcp_dict) 

# Return a JSON-list of stations from the dataset.
@app.route('/api/v1.0/stations/')
def stations():
    print("In station section.")
    
    station_list = session.query(HI_Station.station)\
    .order_by(HI_Station.station).all() 
    print()
    print("Station List:")   
    for row in station_list:
        print (row[0])
    print("Out of Station section.")
    return jsonify(station_list)

# Return a JSON-list of Temperature Observations from the dataset.
@app.route('/api/v1.0/tobs/')
def tobs():
    print("In TOBS section.")
    
    Most_Active = session.query(HI_prcp_Measurement.station,func.count(HI_prcp_Measurement.station)).\
    group_by(HI_prcp_Measurement.station).\
    order_by(func.count(HI_prcp_Measurement.station).desc()).first()   
    
    Most_Active_Station = Most_Active[0]
    Most_Active_Station
    
    Last_Date_MAStation = session.query(HI_prcp_Measurement.date).\
        filter(HI_prcp_Measurement.station == Most_Active_Station).\
        order_by(HI_prcp_Measurement.date.desc()).first().date
    One_Year_before_MAStation = Last_Date_MAStation.replace("2017", "2016")

    last_12_tobs_MAStation =session.query(HI_prcp_Measurement.date, HI_prcp_Measurement.tobs).\
    filter(HI_prcp_Measurement.station == Most_Active_Station).\
    filter(HI_prcp_Measurement.date >= One_Year_before_MAStation).\
    filter(HI_prcp_Measurement.date <= Last_Date_MAStation).\
    order_by(asc(HI_prcp_Measurement.date)).all()
    last_12_tobs_MAStation = [a for *a, in last_12_tobs_MAStation]
    last_12_tobs_MAStation_dict = dict(last_12_tobs_MAStation)
    
    print()
    print("Temperature Results for All Stations")
    print(last_12_tobs_MAStation_dict)
    print("Out of TOBS section.")
    return jsonify(last_12_tobs_MAStation_dict)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
@app.route('/api/v1.0/<start_date>/')

def calc_temps_start(start_date):
    print("In start date section.")
    print(start_date)
    
    select = [func.min(HI_prcp_Measurement.tobs), func.avg(HI_prcp_Measurement.tobs), func.max(HI_prcp_Measurement.tobs)]
    result_temp = session.query(*select).\
        filter(HI_prcp_Measurement.date >= start_date).all()
    print()
    print(f"Calculated temp for start date {start_date}")
    print(result_temp)
    print("Out of start date section.")
    return jsonify(result_temp)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
@app.route('/api/v1.0/<start_date>/<end_date>/')
def calc_temps_start_end(start_date, end_date):
    print("In start & end date section.")
    
    select = [func.min(HI_prcp_Measurement.tobs), func.avg(HI_prcp_Measurement.tobs), func.max(HI_prcp_Measurement.tobs)]
    result_temp = session.query(*select).\
        filter(HI_prcp_Measurement.date >= start_date).filter(HI_prcp_Measurement.date <= end_date).all()
    print()
    print(f"Calculated temp data for start date {start_date} & end date {end_date}")
    print(result_temp)
    print("Out of start & end date section.")
    return jsonify(result_temp)

if __name__ == "__main__":
    app.run(debug=True)