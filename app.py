from flask import Flask, jsonify, request, render_template, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
import os
import time
from datetime import datetime as dt
import csv
import pytz

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)


# database models
class Sensors(db.Model):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    datetime = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)


class SensorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'datetime', 'temperature', 'humidity')


sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('database dropped!')


@app.cli.command('db_seed')
def db_seed():
    first = Sensors(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now()),
                    temperature=20.26,
                    humidity=14.11)
    time.sleep(1)
    second = Sensors(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now()),
                     temperature=21.42,
                     humidity=15.11)
    time.sleep(1)
    third = Sensors(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now()),
                    temperature=22.33,
                    humidity=13.41)

    db.session.add(first)
    db.session.add(second)
    db.session.add(third)
    db.session.commit()
    print('database seeded!')


# @app.cli.command('db_save')
def save_data():
    london = pytz.timezone('Europe/London')
    folder = "static/csv_data"
    files = os.listdir(folder)
    if len(files) > 7:
        files.sort()
        os.remove(f"{folder}/{files[0]}")
    path_name = f'{folder}/{"{:%d %b %Y}".format(dt.now().astimezone(london))}.csv'
    with open(path_name, 'w', newline='\n') as f:
        out = csv.writer(f)
        out.writerow(['id', 'datetime', 'temperature', 'humidity'])

        for item in db.session.query(Sensors).all():
            row = [item.id, item.datetime, item.temperature, item.humidity]
            out.writerow(row)


# @app.cli.command('db_test')
def delete_rows():
    obj = db.session.query(Sensors).order_by(Sensors.id.desc()).first()
    all = Sensors.query.limit(obj.id - 1).all()
    for row in all:
        db.session.delete(row)
    db.session.commit()
    print('rows deleted!')


@app.route('/')
def hello_world():
    files = os.listdir('static/csv_data')
    return render_template('index.html', data=files)


def add_data(temperature, humidity):
    london = pytz.timezone('Europe/London')
    time_now = dt.now().astimezone(london)
    raw_save_time = '23:59:45'
    save_time = [int(i) for i in raw_save_time.split(':')]
    if (time_now.hour == save_time[0]) and (time_now.minute == save_time[1]) and (time_now.second >= save_time[2]):
        if f'{"{:%d %b %Y}".format(dt.now().astimezone(london))}.csv' not in os.listdir('static/csv_data'):
            print('\n\nsaving data\n\n ')
            save_data()
            delete_rows()

    new_data = Sensors(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now().astimezone(london)),
                       temperature=temperature,
                       humidity=humidity)

    db.session.add(new_data)
    db.session.commit()


@app.route('/send')
def send_data():
    try:
        add_data(temperature=float(request.args.get('temperature')), humidity=float(request.args.get('pressure')))
        return jsonify({'info': 'data received'}), 200
    except ValueError:
        return jsonify({'info': 'Value Error! floats only!'}), 400


@app.route("/download", methods=["POST", "GET"])
def get_csv():
    try:
        return send_from_directory('static/csv_data', filename=request.form["myfile"], as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route("/get-data")
def get_data():
    obj = db.session.query(Sensors).order_by(Sensors.id.desc()).first()
    return jsonify({'datetime': obj.datetime, 'temperature': obj.temperature, 'humidity': obj.humidity}), 200


# if __name__ == '__main__':
#     app.run()


@app.route("/sensor-data/<int:length>")
def sensor_data(length=50):
    result = sensors_schema.dump(Sensors.query.all())[:length]
    return jsonify(result), 200


def lru_cache():
    folder = "static/temp"
    files = os.listdir(folder)
    max_len = 20
    if len(files) > max_len:
        files.sort()
        os.remove(f"{folder}/{files[0]}")


@app.route("/sensor-data/csv/<int:length>")
def sensor_data_csv(length=50):
    folder = "static/temp"
    file_name = f'{int(time.time())}.csv'
    lru_cache()
    with open(f'{folder}/{file_name}', 'w', newline='\n') as f:
        out = csv.writer(f)
        out.writerow(['id', 'datetime', 'temperature', 'humidity'])

        for item in db.session.query(Sensors).all()[-length:]:
            row = [item.id, item.datetime, item.temperature, item.humidity]
            out.writerow(row)

    return send_from_directory(folder, filename=file_name, as_attachment=True)
