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
L.Control.geocoder().addTo(mymap);

function getPosition(value){
    console.log(value);
}

// self made navigation bar
// var form = document.getElementById('form');
// var destination = document.getElementById('destination');
// form.addEventListener('submit', (e) => {
//     console.log("submit")
//     e.preventDefault();
//     try{
//         var value = destination.value.split(',');
//         value = value.map(Number);
//         L.marker(value).addTo(mymap);
//     }
//     catch{
//         $.ajax({
//             url: '/map',
//             type: 'POST',
//             contentType: 'application/json',
//             data: $("#destination"),
//             success: function(){
//                 console.log('success')
//             },
//             error: function(){
//                 console.log('error')
//             }
//         });
//     }
    
//     navigator.geolocation.watchPosition(position => {
//         console.log(position);
//         var start = [position.coords.latitude, position.coords.longitude];
//         console.log(start[0], start[1], value[0], value[1]);
//         roadplan(start, value);
//     });
// })

// road planning
function roadplan(start, end){
    L.Routing.control({
        waypoints: [
            L.latLng(start),
            L.latLng(end)
        ]
    }).addTo(mymap);
}

// 示警
function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    getAlert();    
}
function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
}
function getAlert(){
    return fetch('/renderAlert')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showAlert(data.slice(1, data.length-1)))
}
function showAlert(object){
    console.log(object);
    const innerDiv = document.createElement('div');
    const mySidebar = document.getElementById('mySidebar')
    innerDiv.className = 'innerdiv';
    mySidebar.innerHTML='';
    var close= document.createElement('span')
    close.className = 'closebtn'
    close.addEventListener("click", closeNav)
    close.innerHTML='&times;';
    innerDiv.appendChild(close);
    var alerttitle = document.createElement('span');
    // alerttitle.className = 'alert-title-container'
    alerttitle.className = 'alert-title'
    alerttitle.innerHTML='綜合警戒';
    innerDiv.appendChild(alerttitle);
    const alertinfo = document.createElement("section")
    alertinfo.id = "alert-info"
    console.log(alertinfo)
    for (let i=0; i<object.length; i+=3){
        var text = document.createElement('div');
        text.innerHTML = `
        <p class="alert-type">${object[i+1]}警戒</p>
        <p class="alert-location">${object[i]}</p>
        <p class="alert-description">${object[i+2]}</p>
        <hr></hr>
        `
        alertinfo.appendChild(text);
    }

    mySidebar.appendChild(innerDiv);
    mySidebar.appendChild(alertinfo)
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
                    var popup = "<dd>" + object[i+1] + "</dd><dd> 路段編號" + object[i+2] + "</dd>";
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
    {value:"sunday",text:"Sunday"},
    {value:"monday",text:"Monday"},
    {value:"tuesday",text:"Tuesday"},
    {value:"wednesday",text:"Wednesday"},
    {value:"thursday",text:"Thursday"},
    {value:"friday",text:"Friday"},
    {value:"saturday",text:"Saturday"},
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
        for (let i=0; i<object.length; i+=6){
            // var popup = "<dd id='lotid'>" + object[i] + "</dd><dd>" + object[i+1] + "</dd><dd>" + object[i+2] + "</dd><dd>" + object[i+3] + "</dd>'<div id='histogram'></div>'";
            const popup ="<div id='histogram'></div>";
            const parkingInfo = object.slice(i, i + 4)
            const myIcon = L.icon({
                iconUrl: 'static/css/images/parking-pin.svg'
            });
            markers_parking.addLayer(L.marker([object[i+4], object[i+5]], { icon: myIcon })
            .bindPopup(popup)
            .on('popupopen', (e)=>{renderHistogram(e, parkingInfo)})
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
async function renderHistogram(e, parkingInfo){
    console.log(parkingInfo)
    const leafletPopUpWrapper = document.querySelector(".leaflet-popup-content-wrapper")
    leafletPopUpWrapper.id = "leafletPopUpWrapperReplaceStyle"
    const lotid = parkingInfo[0]
    const now = new Date();
    const today = now.getDay();
    console.log(today, days)
    const weekday = days[today]['text']
    console.log(weekday)
    const data = await getHistogramData(lotid, weekday)
    const {lot} = data
    if (lot){
        Object.keys(lot).forEach(function(key) {
            console.log(lot[key][0])
            histogram(lot[key][0], lotid, parkingInfo);
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

function histogram(data, lotid, parkginInfo){
    var trace = {
        x: data,
        type: 'histogram',
    };
    var data = [trace];
    var layout = {
        width: 350,
        height: 250,
        yaxis: {title: '數量'},
        xaxis: {title: '時間'},
        margin: {l:42, b:30}
    };
    Plotly.newPlot('histogram', data, layout);
    createSelect()
    createParkingInfoElement(parkginInfo)
    timerId = setInterval(()=>{
        let weekday = document.querySelector('#day-select option:checked').label;
        updateHistogramData(lotid, weekday)
    }, 100000)
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
        width: 350,
        height: 250,
        yaxis: {title: '數量'},
        xaxis: {title: '時間'},
        margin: {l:42, b:30}
    };
    Plotly.newPlot('histogram', trace, layout)
}

function createParkingInfoElement(parkingInfo){
    const parkingName = parkingInfo[1]
    const totalParkingNumber = parkingInfo[2]
    const leftParkingNumber = parkingInfo[3]
    const container = document.createElement("div")
    container.classList.add("parking-info")
    container.innerHTML = `
        <div class="parking-name">${parkingName}</div>
        <div class="total-parking">總停車位數：${totalParkingNumber}</div>
        <div class="left-parking">剩餘車位：${leftParkingNumber}</div>
        <div class="time-zone-parkgin">各時段剩餘車位數</div>
    `
    const histogram = document.querySelector("#histogram")
    histogram.appendChild(container)
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
        if (today === index) {
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
        var popup = "<dd>" + object[i+5]+"</dd>" + "<dd><a href="+object[i+2]+" target='_blank'>即時畫面</a></dd>"
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

document.querySelectorAll('.map-layer').forEach(item => {
    item.addEventListener('click', function() {
        if (item.getAttribute('data-clicked') === "true") {
            item.setAttribute('data-clicked', "false");
            item.classList = 'map-layer map-layer-inactive';
            if(item.getAttribute('id') === 'livevd') {
                document.getElementById('map-legend-container').style = 'display: none';
            }
        } else if (item.getAttribute('data-clicked') === "false") {
            item.setAttribute('data-clicked', "true");
            item.classList = 'map-layer map-layer-active';
            if(item.getAttribute('id') === 'livevd') {
                document.getElementById('map-legend-container').style = 'display: flex';
            }
        }
    });
})