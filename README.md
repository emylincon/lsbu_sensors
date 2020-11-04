# Web App for Displaying Sensor data
* Web app is Available on here >>> [link](http://lsbu-sensors.herokuapp.com/)

# Exposed APIs
## Endpoint for realtime-date
* This returns a json data
* `/get-data` 

## Endpoint to obtain data from database
* This returns a json data
* `/sensor-data/<int:length>`

## Endpoint to get csv data
* This returns a csv
* `/sensor-data/csv/<int:length>`

## Endpoint to return statistics of data collected
* This returns a json data
* `/describe` 
