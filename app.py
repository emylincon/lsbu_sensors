from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

data = {'temperature': [], 'pressure': []}


@app.route('/')
def hello_world():
    return render_template('index.html', data=data)


def add_data(temperature, pressure):
    max_length = 200
    if len(data['pressure']) > max_length:
        data['pressure'].pop(0)
        data['temperature'].pop(0)
    data['temperature'].append(temperature)
    data['pressure'].append(pressure)


@app.route('/send')
def send_data():
    try:
        add_data(temperature=float(request.args.get('temperature')), pressure=float(request.args.get('temperature')))
        return jsonify({'info': 'data received'}), 200
    except ValueError:
        return jsonify({'info': 'Value Error! floats only!'})


# if __name__ == '__main__':
#     app.run()
