
var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [0],
        datasets: [{
            label: 'Celsius',
            data: [1],
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    callback: function(value, index, values) {
                        return value+'°';
                    }
                }
            }]
        },
        title: {
            fontSize: 20,
            text: "Temperature",
            display: true,
            fontStyle: 'bold'
        },
    }
});

var ct1 = document.getElementById('myChart1').getContext('2d');
var myChart1 = new Chart(ct1, {
    type: 'line',
    data: {
        labels: [0],
        datasets: [{
            label: 'Percentage',
            data: [1],
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    callback: function(value, index, values) {
                        return value+'%';
                    }
                }
            }]
        },
        title: {
            fontSize: 20,
            text: "Humidity",
            display: true,
            fontStyle: 'bold'
        },
    }
});

const max_length = 50;
const start = new Date("Sep 10, 2020 12:00:00").getTime();

function today(){
    let date = new Date();
    document.getElementById("today").innerHTML = `${date.getDate()}-${date.getMonth()+1}-${date.getFullYear()}`;
}

today()

function next_x(chat, item){
    chat.data.labels.push(item);
    if (chat.data.labels.length > max_length){
        chat.data.labels.shift();
    }

}

function next_y(chat, item){
    chat.data.datasets[0].data.push(item);
    if (chat.data.datasets[0].data.length > max_length){
        chat.data.datasets[0].data.shift();
    }

}

function timeCount(){
    var now = new Date().getTime();
    var myCount =  now - start;
    var days = Math.floor(myCount / (1000 * 60 * 60 * 24));
    var hours = Math.floor((myCount  % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((myCount  % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((myCount  % (1000 * 60)) / 1000);

    document.getElementById("time").innerHTML = days + "d " + hours + "h "
  + minutes + "m " + seconds + "s ";
}


async function myData(){
    const response = await fetch('/get-data');
    const data = await response.json();
    let myTime = data['datetime'].split(" ")[1];
    next_x(myChart, myTime);        // temperature
    next_x(myChart1, myTime);       // humidity
    next_y(myChart, data['temperature']);    // temperature
    next_y(myChart1, data['humidity']);      // temperature
    // console.log(data['datetime']);
    // console.log(data['temperature']);
    // console.log(data['humidity']);

}

function update(){
    myData();
    myChart.update();
    myChart1.update();
    timeCount();
}

setInterval(update, 1000);


