var mymap = L.map('map').setView([25.039407262686808, 121.55009336242676], 12);
var tiles = L.tileLayer('https://tile.jawg.io/2da962d1-5c31-4de7-af98-cb2707b5955d/{z}/{x}/{y}{r}.png?access-token=eqFTq0WXVAanX9dQYEjwrh6PzZn1yn5hvxlkN4blWBWdfLqkGlNtrnsAWD4oZTwf', {
    maxZoom: 19,
}).addTo(mymap);
mymap.attributionControl.addAttribution("<a href=\"https://www.jawg.io\" target=\"_blank\">&copy; Jawg</a> - <a href=\"https://www.openstreetmap.org\" target=\"_blank\">&copy; OpenStreetMap</a>&nbsp;contributors")
let timerId = 0;

// locate current position
// var lc = L.control.locate({
//     position: 'topright',
//     strings: {
//         title: "Show me where I am, yo!"
//     },
//     setView: 'always',
//     locateOptions:{
//         enableHighAccuracy: true
//     }
// }).addTo(mymap);
// lc.start();

// search function (navigator to be add)
// L.Control.geocoder().addTo(mymap);

function getPosition(value){
    console.log(value);
}

// self made navigation bar
var form = document.getElementById('form');
var destination = document.getElementById('destination');
form.addEventListener('submit', (e) => {
    console.log("submit")
    e.preventDefault();
    try{
        var value = destination.value.split(',');
        value = value.map(Number);
        L.marker(value).addTo(mymap);
    }
    catch{
        $.ajax({
            url: '/map',
            type: 'POST',
            contentType: 'application/json',
            data: $("#destination"),
            success: function(){
                console.log('success')
            },
            error: function(){
                console.log('error')
            }
        });
    }
    
    navigator.geolocation.watchPosition(position => {
        console.log(position);
        var start = [position.coords.latitude, position.coords.longitude];
        console.log(start[0], start[1], value[0], value[1]);
        roadplan(start, value);
    });
})

// road planning
function roadplan(start, end){
    L.Routing.control({
        waypoints: [
            L.latLng(start),
            L.latLng(end)
        ]
    }).addTo(mymap);
}

// 施工
function getConstruction(){
    return fetch('/renderConstruction')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showConstruction(data.slice(1, data.length-1)))
}
var markers_construction = L.markerClusterGroup();
function showConstruction(object){
    if (mymap.hasLayer(markers_construction)){
        mymap.removeLayer(markers_construction);
    }
    else{
        let temp_road = 999;
        for (let i=0; i<object.length; i+=5){
            if (object[i+2] != temp_road){
                if (i!=0){
                    var popup = "<dd>" + object[i] + "</dd><dd>" + object[i+1] + "</dd><dd>" + object[i+2] + "</dd>";
                    markers_construction.addLayer(L.polyline(line).bindPopup(popup)).addTo(mymap);
                }
                temp_road = object[i+2];
                var line = [[object[i+3], object[i+4]]];
            }
            else{
                line.push([object[i+3], object[i+4]]);
            }
            mymap.addLayer(markers_construction);
        }
    }
}

// 停車場
const days = [
    {value:"monday",text:"Monday"},
    {value:"tuesday",text:"Tuesday"},
    {value:"wednesday",text:"Wednesday"},
    {value:"thursday",text:"Thursday"},
    {value:"friday",text:"Friday"},
    {value:"saturday",text:"Saturday"},
    {value:"sunday",text:"Sunday"},
]
// 1. 被觸發，拿資料
function getParking(){
    return fetch('/renderParking')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showParking(data.slice(1, data.length-1)))
}
var markers_parking = L.markerClusterGroup();

// 2. 點標出來、導向 renderhistogram
function showParking(object){
    if (mymap.hasLayer(markers_parking)){
        mymap.removeLayer(markers_parking);
    }
    else{
        for (var i=0; i<object.length; i+=6){
            var popup = "<dd id='lotid'>" + object[i] + "</dd><dd>" + object[i+1] + "</dd><dd>" + object[i+2] + "</dd><dd>" + object[i+3] + "</dd>'<div id='histogram'></div>'";
            // var popup = '<div id="foo"></div>';
            markers_parking.addLayer(L.marker([object[i+4], object[i+5]])
            .bindPopup(popup)
            .on('popupopen', renderHistogram)
            .on('popupclose', deleteid)
            );
        mymap.addLayer(markers_parking);
        }
    }
}
function deleteid(){
    if (timerId) {
        clearInterval(timerId)
    }
}
// 3. send lotid and weekday to gethistogramdata and plot first graph
async function renderHistogram(e){
    let marker = e.popup._source._popup._content;
    var doc = new DOMParser().parseFromString(marker, "text/html");
    lotid = doc.getElementById('lotid').textContent;
    const now = new Date();
    const today = now.getDay();
    const weekday = days[today-1]['text']
    console.log(lotid);
    const data = await getHistogramData(lotid, weekday)
    const {lot} = data
    if (lot){
        Object.keys(lot).forEach(function(key) {
            console.log(lot[key][0])
            histogram(lot[key][0], lotid);
        });
    }
}

async function getHistogramData(lotid, weekday){
    console.log(lotid);
    const res = await fetch("/maplot", {
        method:"POST",
        headers:{'Content-type':'application/json'},
        body:JSON.stringify({'lotid': lotid, 'weekday': weekday})
    })
    const data = await res.json()
    return data
}

function histogram(data, lotid){
    var trace = {
        x: data,
        type: 'histogram',
    };
    var data = [trace];
    var layout = {
        width: 500,
        title: 'Remaining Parking Space',
        yaxis: {title: 'number of parking space'},
        xaxis: {title: 'time'}
    };
    Plotly.newPlot('histogram', data, layout);
    createSelect()
    timerId = setInterval(()=>{
        let weekday = document.querySelector('#day-select option:checked').label;
        updateHistogramData(lotid, weekday)
    }, 10000)
}

async function updateHistogramData(lotid, weekday){
    const data = await getHistogramData(lotid, weekday);
    const {lot} = data;
    if (!lot) return
    const trace = [{
        x: lot[Object.keys(lot)[0]][0],
        type: 'histogram'
        }]
    var layout = {
        width: 500,
        title: 'Remaining Parking Space',
        yaxis: {title: 'number of parking space'},
        xaxis: {title: 'time'}
    };
    Plotly.newPlot('histogram', trace, layout)
}

function createSelect(){
    const histogram = document.querySelector(".user-select-none.svg-container")
    const container = document.createElement("div")
    container.classList.add("day-select-container")
    const select = document.createElement("select")
    select.id = "day-select"
    const weekOptgroup = document.createElement("optgroup")
    weekOptgroup.setAttribute("label", "平假日")
    weekOptgroup.innerHTML = `
        <option value="weekend">假日</option>
        <option value="weekday">平日</option>
    `
    const dayOptgroup = document.createElement("optgroup")

    dayOptgroup.setAttribute("label", "單日")
    const now = new Date();
    const today = now.getDay()
    days.forEach((day, index)=>{
        const dayOption = document.createElement("option")
        dayOption.setAttribute("value", day.value)
        dayOption.textContent = day.text
        if (today -1 === index) {
            dayOption.setAttribute("selected", true)
        }
        dayOptgroup.appendChild(dayOption)
    })
    select.appendChild(weekOptgroup)
    select.appendChild(dayOptgroup)
    container.appendChild(select)
    histogram.append(container)
    var dayselect = document.getElementById('day-select');
    dayselect.addEventListener('input', (e) => {
        e.preventDefault();
        let weekday = e.target.value;
        updateHistogramData(lotid, weekday);
    })
}

// 監控畫面
function getCctv(){  
    return fetch('/renderCctv')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showCctv(data.slice(1, data.length-1)))
}

// var markers_cctv = L.markerClusterGroup();
var markers_cctv = L.markerClusterGroup({
	iconCreateFunction: function(cluster) {
        var markers = cluster.getAllChildMarkers();
        // '<div class="circle">' + markers.length + '</div><div>'
        var html = '<b>' + cluster.getChildCount() + '</b>';
        // console.log(markers);
		return L.divIcon({html: html});
	}
});
function showCctv(object){
    if (mymap.hasLayer(markers_cctv)){
        mymap.removeLayer(markers_cctv);
        return;
    }
    
    for (var i=0; i<object.length; i+=6){
        var popup = "<dd>" + object[i+5]+"</dd>" + "<dd><a href="+object[i+2]+">即時畫面</a></dd>"
        markers_cctv.addLayer(L.marker([object[i+4], object[i+3]]).bindPopup(popup)).addTo(mymap);
        mymap.addLayer(markers_cctv);
    }
}



// 壅塞狀況
function getLivevd(){
    return fetch('/renderLivevd')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showLivevd(data.slice(1, data.length-1)))
}
var markers_vd = L.markerClusterGroup();
function showLivevd(object){
    if (mymap.hasLayer(markers_vd)){
        mymap.removeLayer(markers_vd);
    }
    else{
        for (var i=0; i<object.length; i+=9){
            if (object[i+2] > 60){
                markers_vd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]], {color:'green'})).addTo(mymap);
            }
            else if (40 < object[i+2] < 60){
                markers_vd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]], {color:'orange'})).addTo(mymap);
            }
            else if (0< object[i+2] < 40){
                markers_vd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]], {color:'red'})).addTo(mymap);
            }
            else{
                markers_vd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]])).addTo(mymap);
            }
        }
        mymap.addLayer(markers_vd);
    }
}



var circle = L.circle([51.508, -0.11], {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5,
    radius: 500
}).addTo(mymap);

var polygon = L.polygon([
    [51.509, -0.08],
    [51.503, -0.06],
    [51.51, -0.047]
]).addTo(mymap);