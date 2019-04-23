from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from numpy import ravel

#Setting things up
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Saving references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#getting latest and earliest dates in the dataset.
latest = session.query(func.max(Measurement.date).label("late")).all()
early = dt.datetime.strptime(latest[0].late,"%Y-%m-%d") - dt.timedelta(days=365)
early_date = dt.datetime.strftime(early,"%Y-%m-%d")
late_date = latest[0].late
#Getting station counts
station_counts = session.query(func.count(Measurement.tobs),Measurement.station).\
group_by(Measurement.station).\
order_by(func.count(Measurement.station).desc()).all()

#Data for the precip path.
sel = [Measurement.date, Measurement.prcp]
qry = session.query(*sel).filter(Measurement.date >= early_date).\
group_by(Measurement.date).\
order_by(Measurement.date.desc()).all()
rain = {pair[0]:pair[1] for pair in qry}

#Data for the stations path.
qry2 = session.query(Measurement.station).distinct().all()
stations = list(ravel(qry2))

#Data for the temperature path.
qry3 = session.query(Measurement.date,Measurement.tobs).\
filter(Measurement.date >= early_date).all()
temps = [list(pear) for pear in qry3]

app = Flask(__name__)

@app.route("/")
def home():
    return(
        f"The collective will now list the paths available for feeble human meanderings.<br/>"
        f"All paths start with /api. Know this and learn it well!<br/>"
        f"Further continuations of the path are available as follows:<br/>"
        f"/precipitation<br/>   /stations<br/>   /temperature<br/>   /<'start_date'>/<'end_date'><br/>"
        f"<br/><br/>"
        f"The precipitation path will list off the average amount of precipitation on all days data was taken.<br/>"
        f"Because there are multiple readings on each date, and the date has to be the key as per instructions, we present you the average of all the prcp readings taken on any given day!<br/><br/>"
        f"The stations path will return the stations that are located in Hawaii.<br/><br/>"
        f"The temperature path will list off the temperatures taken by station {station_counts[0][1]} from within 365 days before {latest[0].late}.<br/><br/>"
        f"Substituting values for both start and end_date in the YYYY-MM-DD format will give you the min, avg, and max temp within that date range.<br/>"
        f"The early date is {early_date} and the last date is {latest[0].late}. Don't exceed them."
    )

@app.route("/precipitation")
def rainman():
    return jsonify(rain)

@app.route("/stations")
def plots():
    return jsonify(stations)

@app.route("/temperature")
def sunshine():
    return jsonify(temps)

@app.route("/<start>")
@app.route("/<start>/<end>")
def groupies(start, end = late_date):
    #Recreating stuff in this thread so it can be used here in said thread
    #Setting things up
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")
    # reflect an existing database into a new model
    Base = automap_base()
    # reflect the tables
    Base.prepare(engine, reflect=True)
    # Saving references to the used table
    Measurement = Base.classes.measurement
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #This is the code that does the work. Getting the data and so forth.
    ins = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    qry4 = session.query(*ins).filter(Measurement.station == station_counts[0][1]).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    wanted = [list(groups) for groups in qry4]
    return jsonify(wanted[0])

if __name__ == "__main__":
    app.run(debug=True)