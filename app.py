from flask import Flask, jsonify, request, render_template, send_from_directory, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
from flask_marshmallow import Marshmallow
import os
import time
from datetime import datetime as dt
import csv
import pytz
import pandas as pd

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)

display_data = {'actual': {'sensor': {'heat_index': 24.94215049377219, 'temperature': 21.0, 'humidity': 51.0,
                                      'datetime': '29-09-2020 10:22:37', 'id': 3018},
                           'lstm': {'heat_index': 26.94215049377219, 'temperature': 18.350318908691406,
                                    'humidity': 38.90366744995117, 'datetime': '29-09-2020 10:22:37', 'id': 3018},
                           'arima': {'heat_index': 25.763476888337447, 'temperature': 25.0,
                                     'humidity': 43.40027524883986, 'datetime': '29-09-2020 10:22:37', 'id': 3018}},
                'data_stat': {'temperature': {'count': {'data': 3018.0, 'arrow': 'up', '%': 0.57},
                                              'mean': {'data': 25.12, 'arrow': 'down', '%': 0.09},
                                              'std': {'data': 0.50, 'arrow': 'up', '%': 27.04},
                                              'min': {'data': 20.26, 'arrow': 'equal', '%': 0.0},
                                              'max': {'data': 26.0, 'arrow': 'equal', '%': 0.0}},
                              'humidity': {'count': {'data': 3018.0, 'arrow': 'up', '%': 0.57},
                                           'mean': {'data': 39.13, 'arrow': 'up', '%': 0.18},
                                           'std': {'data': 1.48, 'arrow': 'up', '%': 31.31},
                                           'min': {'data': 36.0, 'arrow': 'equal', '%': 0.0},
                                           'max': {'data': 53.0, 'arrow': 'up', '%': 26.19}},
                              'heat_index': {'count': {'data': 3018.0, 'arrow': 'up', '%': 0.57},
                                             'mean': {'data': 25.74, 'arrow': 'down', '%': 0.02},
                                             'std': {'data': 0.24, 'arrow': 'up', '%': 3.42},
                                             'min': {'data': 20.55, 'arrow': 'equal', '%': 0.0},
                                             'max': {'data': 26.27, 'arrow': 'equal', '%': 0.0}}},
                'pred_stat': {'lstm': {
                    'hum': {'rmse': 1.34, 'date': '24-09-2020 19:09:36', 'accuracy': 59.82, 'arrow': 'down',
                            'loss': 40.18},
                    'temp': {'rmse': 0.01, 'date': '24-09-2020 19:09:36', 'accuracy': 99.1, 'arrow': 'down',
                             'loss': 0.9},
                    'heat': {'rmse': 0.03, 'date': '24-09-2020 19:09:36', 'accuracy': 71.53, 'arrow': 'down',
                             'loss': 28.47}},
                              'arima': {'hum': {'rmse': 1.11, 'date': '24-09-2020 19:09:36', 'arrow': 'up'},
                                        'temp': {'rmse': 0.0, 'date': '24-09-2020 19:09:36', 'arrow': 'down'},
                                        'heat': {'rmse': 0.02, 'date': '24-09-2020 19:09:36', 'arrow': 'up'}}}}


# database models
class Sensors(db.Model):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    datetime = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    heat_index = Column(Float)


class LSTMData(db.Model):
    __tablename__ = 'lstmData'
    id = Column(Integer, primary_key=True)
    datetime = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    heat_index = Column(Float)


class ARIMAData(db.Model):
    __tablename__ = 'ARIMAData'
    id = Column(Integer, primary_key=True)
    datetime = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    heat_index = Column(Float)


class SensorSchema(ma.Schema):
    class Meta:
        fields = ('id', 'datetime', 'temperature', 'humidity', 'heat_index')


class LSTMSchema(ma.Schema):
    class Meta:
        fields = ('id', 'datetime', 'temperature', 'humidity', 'heat_index')


class ARIMASchema(ma.Schema):
    class Meta:
        fields = ('id', 'datetime', 'temperature', 'humidity', 'heat_index')


sensor_schema = SensorSchema()
sensors_schema = SensorSchema(many=True)

lstm_schema = LSTMSchema()
lstm_schemas = LSTMSchema(many=True)

arima_schema = ARIMASchema()
arima_schemas = ARIMASchema(many=True)


def get_db_data(table):
    tables = {'sensor': [Sensors, sensors_schema], 'lstm': [LSTMData, lstm_schemas],
              'arima': [ARIMAData, arima_schemas]}
    return tables[table][1].dump(tables[table][0].query.all())


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
    data = [20.26, 40.11, 20.55]
    funcs = [Sensors, LSTMData, ARIMAData]
    for table in funcs:
        entry = table(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now()),
                      temperature=data[0],
                      humidity=data[1],
                      heat_index=data[2])
        time.sleep(1)
        db.session.add(entry)

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
        out.writerow(['id', 'datetime', 'temperature', 'humidity', 'heat_index', 'lstm_temp', 'lstm_hum', 'lstm_heat',
                      'arima_temp', 'arima_hum', 'arima_heat'])
        s_data = db.session.query(Sensors).all()
        l_data = db.session.query(LSTMData).all()
        a_data = db.session.query(ARIMAData).all()

        for i in range(len(s_data)):
            row = [s_data[i].id, s_data[i].datetime, s_data[i].temperature, s_data[i].humidity, s_data[i].heat_index,
                   l_data[i].temperature, l_data[i].humidity, l_data[i].heat_index,
                   a_data[i].temperature, a_data[i].humidity, a_data[i].heat_index]
            out.writerow(row)
        out.writerow(['id', 'datetime', 'temperature', 'humidity'])

        # for item in db.session.query(Sensors).all():
        #     row = [item.id, item.datetime, item.temperature, item.humidity]
        #     out.writerow(row)


# @app.cli.command('db_test')
def delete_rows():
    tables = [Sensors, LSTMData, ARIMAData]
    for table in tables:
        obj = db.session.query(table).order_by(table.id.desc()).first()
        all_data = Sensors.query.limit(obj.id - 1).all()
        for row in all_data:
            db.session.delete(row)
    db.session.commit()
    print('rows deleted!')


@app.route('/')
def hello_world():
    files = os.listdir('static/csv_data')
    return render_template('index.html', data=files)


def add_data(sent_data):
    ''':key
    sent_data = {'sensor': {'heat_index': 24.94215049377219, 'temperature': 21.0, 'humidity': 51.0, 'datetime': '29-09-2020 10:22:37', 'id': 3018},
			'lstm': {'heat_index': 25.70731544494629, 'temperature': 18.350318908691406, 'humidity': 38.90366744995117, 'datetime': '29-09-2020 10:22:37', 'id': 3018},
			'arima': {'heat_index': 25.763476888337447, 'temperature': 25.0, 'humidity': 43.40027524883986, 'datetime': '29-09-2020 10:22:37', 'id': 3018}}
    '''
    london = pytz.timezone('Europe/London')
    time_now = dt.now().astimezone(london)
    raw_save_time = '23:59:45'
    save_time = [int(i) for i in raw_save_time.split(':')]
    if (time_now.hour == save_time[0]) and (time_now.minute == save_time[1]) and (time_now.second >= save_time[2]):
        if f'{"{:%d %b %Y}".format(dt.now().astimezone(london))}.csv' not in os.listdir('static/csv_data'):
            print('\n\nsaving data\n\n ')
            save_data()
            delete_rows()

    my_date = "{:%d-%m-%Y %H:%M:%S}".format(dt.now().astimezone(london))
    sen_data = sent_data['sensor']
    arima_data = sent_data['arima']
    lstm_data = sent_data['lstm']
    # new_data = Sensors(datetime="{:%d-%m-%Y %H:%M:%S}".format(dt.now().astimezone(london)),
    #                    temperature=temperature,
    #                    humidity=humidity)
    data1 = Sensors(datetime=my_date,
                    temperature=sen_data['temperature'],
                    humidity=sen_data['humidity'],
                    heat_index=sen_data['heat_index'])

    data2 = LSTMData(datetime=my_date,
                     temperature=lstm_data['temperature'],
                     humidity=lstm_data['humidity'],
                     heat_index=lstm_data['heat_index'])

    data3 = ARIMAData(datetime=my_date,
                      temperature=arima_data['temperature'],
                      humidity=arima_data['humidity'],
                      heat_index=arima_data['heat_index'])

    # data2 = LSTMData(datetime=my_date,
    #                  temperature=lstm_temp,
    #                  humidity=lstm_hum,
    #                  heat_index=lstm_heat)
    #
    # data3 = ARIMAData(datetime=my_date,
    #                  temperature=arima_temp,
    #                  humidity=arima_hum,
    #                  heat_index=arima_heat)
    db.session.add(data1)
    db.session.add(data2)
    db.session.add(data3)
    db.session.commit()


@app.route('/send', methods=["POST"])
def send_data():
    try:
        sent_data = request.get_json()
        display_data.update(sent_data)
        add_data(sent_data['actual'])

        return jsonify({'info': 'data received'}), 200
    except ValueError:
        return jsonify({'info': 'accepts only json data'}), 400


@app.route("/download", methods=["POST", "GET"])
def get_csv():
    try:
        return send_from_directory('static/csv_data', filename=request.form["myfile"], as_attachment=True)
    except FileNotFoundError:
        abort(404)


# @app.route("/get-data")
# def get_data():
#     obj = db.session.query(Sensors).order_by(Sensors.id.desc()).first()
#     return jsonify({'datetime': obj.datetime, 'temperature': obj.temperature, 'humidity': obj.humidity}), 200

@app.route("/get-data")
def get_data():
    london = pytz.timezone('Europe/London')
    result = {**display_data, 'datetime': "{:%d-%m-%Y %H:%M:%S}".format(dt.now().astimezone(london))}
    return jsonify(result), 200


def stat():
    result = sensors_schema.dump(Sensors.query.all())
    df = pd.DataFrame(result)
    return df.describe()


@app.route("/describe")
def get_stat():
    dfb = stat()
    return dfb.to_json()


@app.route("/sensor-data/<int:length>")
def sensor_data(length=50):
    result = {}
    for table in ['sensor', 'lstm', 'arima']:
        result[table] = get_db_data(table)[-length:]

    # result = sensors_schema.dump(Sensors.query.all())[:length]
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
        out.writerow(['id', 'datetime', 'temperature', 'humidity', 'heat_index', 'lstm_temp', 'lstm_hum', 'lstm_heat',
                      'arima_temp', 'arima_hum', 'arima_heat'])
        s_data = db.session.query(Sensors).all()[-length:]
        l_data = db.session.query(LSTMData).all()[-length:]
        a_data = db.session.query(ARIMAData).all()[-length:]
        for i in range(len(s_data)):
            row = [s_data[i].id, s_data[i].datetime, s_data[i].temperature, s_data[i].humidity, s_data[i].heat_index,
                   l_data[i].temperature, l_data[i].humidity, l_data[i].heat_index,
                   a_data[i].temperature, a_data[i].humidity, a_data[i].heat_index]
            out.writerow(row)

    return send_from_directory(folder, filename=file_name, as_attachment=True)
