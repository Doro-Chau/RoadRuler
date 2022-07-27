var mymap = L.map('map').setView([25.039407262686808, 121.55009336242676], 12);
var tiles = L.tileLayer('https://tile.jawg.io/2da962d1-5c31-4de7-af98-cb2707b5955d/{z}/{x}/{y}{r}.png?access-token=eqFTq0WXVAanX9dQYEjwrh6PzZn1yn5hvxlkN4blWBWdfLqkGlNtrnsAWD4oZTwf', {
    maxZoom: 19,
}).addTo(mymap);
mymap.attributionControl.addAttribution("<a href=\"https://www.jawg.io\" target=\"_blank\">&copy; Jawg</a> - <a href=\"https://www.openstreetmap.org\" target=\"_blank\">&copy; OpenStreetMap</a>&nbsp;contributors")
let timerId = 0;

// search function
L.Control.geocoder().addTo(mymap);

// road planning
function roadplan(start, end){
    L.Routing.control({
        waypoints: [
            L.latLng(start),
            L.latLng(end)
        ]
    }).addTo(mymap);
}

// alert
function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    getAlert();    
}
function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
}
function getAlert(){
    return fetch('/render_alert')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showAlert(data.slice(1, data.length-1)))
}
function showAlert(object){
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

// construction
function getConstruction(){
    return fetch('/render_construction')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showConstruction(data.slice(1, data.length-1)))
}
var markersConstruction = L.layerGroup();
function showConstruction(object){
    if (mymap.hasLayer(markersConstruction)){
        mymap.removeLayer(markersConstruction);
    }
    else{
        for (let i=0; i< object.length; i+=6){
            let popup = "<dd>施工單位： " + object[i] + "</dd><dd>施工期間： " + object[i+1] + "-" + object[i+2] + "</dd><dd>每日施工時間： " + object[i+3] + "</dd>";
            markersConstruction.addLayer(L.circle([object[i+4], object[i+5]], {radius: 6.5}).bindPopup(popup)).addTo(mymap);
            mymap.addLayer(markersConstruction);
        }
    }
}

// parking space
const days = [
    {value:"sunday",text:"Sunday"},
    {value:"monday",text:"Monday"},
    {value:"tuesday",text:"Tuesday"},
    {value:"wednesday",text:"Wednesday"},
    {value:"thursday",text:"Thursday"},
    {value:"friday",text:"Friday"},
    {value:"saturday",text:"Saturday"},
]
// 1. triggered and get data
function getParking(){
    return fetch('/render_parking')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showParking(data.slice(1, data.length-1)))
}
var markersParking = L.markerClusterGroup();
// 2. mark and renderhistogram
function showParking(object){
    if (mymap.hasLayer(markersParking)){
        mymap.removeLayer(markersParking);
    }
    else{
        markersParking = L.markerClusterGroup();
        for (let i=0; i<object.length; i+=6){
            // var popup = "<dd id='lotid'>" + object[i] + "</dd><dd>" + object[i+1] + "</dd><dd>" + object[i+2] + "</dd><dd>" + object[i+3] + "</dd>'<div id='histogram'></div>'";
            const popup ="<div id='histogram'></div>";
            const parkingInfo = object.slice(i, i + 4)
            const myIcon = L.icon({
                iconUrl: 'static/css/images/parking-pin.svg'
            });
            markersParking.addLayer(L.marker([object[i+4], object[i+5]], { icon: myIcon })
            .bindPopup(popup)
            .on('popupopen', (e)=>{renderHistogram(e, parkingInfo)})
            .on('popupclose', deleteid)
            );
        mymap.addLayer(markersParking);
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
    const leafletPopUpWrapper = document.querySelector(".leaflet-popup-content-wrapper")
    leafletPopUpWrapper.id = "leafletPopUpWrapperReplaceStyle"
    const lotid = parkingInfo[0]
    const now = new Date();
    const today = now.getDay();
    const weekday = days[today]['text']
    const data = await getHistogramData(lotid, weekday)
    const {lot} = data
    if (lot){
        Object.keys(lot).forEach(function(key) {
            histogram(lot[key], lotid, parkingInfo);
        });
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');
function getHistogramData(lotid, weekday){
    const request = new Request(
    "/maplot",
    {headers: {'X-CSRFToken': csrftoken}}
);
    return fetch(request, {
        method:"POST",
	mode: 'same-origin',
        body:JSON.stringify({'lotid': lotid, 'weekday': weekday})
    }).then(function(res) {
	    const data = res.json();
	    return data
    })   
}

function histogram(x, lotid, parkingInfo){
    if (x.length>0){
        var trace = {
            x: x,
            type: 'histogram',
            nbinsx: 24
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
        createSelect();
        createParkingInfoElement(parkingInfo)
        timerId = setInterval(()=>{
            let weekday = document.querySelector('#day-select option:checked').label;
            updateHistogramData(lotid, weekday)
        }, 10000)
    } 
    else {
        document.getElementById("histogram").style.width = "200px";
        document.getElementById("histogram").style.height = "150px";
        createParkingNoInfo(parkingInfo)
    }
}

async function updateHistogramData(lotid, weekday){
    const data = await getHistogramData(lotid, weekday);
    const {lot} = data;
    if (!lot) return
    const trace = [{
        x: lot[Object.keys(lot)[0]],
        type: 'histogram',
        nbinsx: 24
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

function createParkingNoInfo(parkingInfo){
    const parkingName = parkingInfo[1]
    const totalParkingNumber = parkingInfo[2]
    const leftParkingNumber = parkingInfo[3]
    const container = document.createElement("div")
    container.classList.add("parking-no-info")
    container.innerHTML = `
        <div class="parking-no-name">${parkingName}</div>
        <div class="total-no-parking">總停車位數：${totalParkingNumber}</div>
        <div class="left-no-parking">剩餘車位：無提供資料</div>
    `
    const histogram = document.querySelector("#histogram")
    histogram.appendChild(container)
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

// CCTV
function getCctv(){  
    return fetch('/render_cctv')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showCctv(data.slice(1, data.length-1)))
}

var markersCctv = L.markerClusterGroup({
	iconCreateFunction: function(cluster) {
        var html = '<b>' + cluster.getChildCount() + '</b>';
		return L.divIcon({html: html});
	}
});
function showCctv(object){
    if (mymap.hasLayer(markersCctv)){
        mymap.removeLayer(markersCctv);
        return;
    }
    markersCctv = L.markerClusterGroup({
        iconCreateFunction: function(cluster) {
            var html = '<b>' + cluster.getChildCount() + '</b>';
            return L.divIcon({html: html});
        }
    });
    for (var i=0; i<object.length; i+=6){
        var popup = "<dd>" + object[i+5]+"</dd>" + "<dd><a href="+object[i+2]+" target='_blank'>即時畫面</a></dd>"
        const myIcon = L.icon({
            iconUrl: 'static/css/images/videocam-pin.svg'
        });
        markersCctv.addLayer(L.marker([object[i+4], object[i+3]], { icon: myIcon }).bindPopup(popup)).addTo(mymap);
        mymap.addLayer(markersCctv);
    }
}


// traffic
function getLivevd(){
    return fetch('/render_livevd')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showLivevd(data.slice(1, data.length-1)))
}
var markersVd = L.markerClusterGroup();
function showLivevd(object){
    if (mymap.hasLayer(markersVd)){
        mymap.removeLayer(markersVd);
    }
    else{
        for (var i=0; i<object.length; i+=9){
            if (object[i+2] > 60){
                markersVd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]], {color:'green'})).addTo(mymap);
            }
            else if (40 < object[i+2] < 60){
                markersVd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]], {color:'orange'})).addTo(mymap);
            }
            else if (0< object[i+2] < 40){
                markersVd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]], {color:'red'})).addTo(mymap);
            }
            else{
                markersVd.addLayer(L.polyline([[object[i+4], object[i+3]], [object[i+6], object[i+5]], [object[i+8], object[i+7]]])).addTo(mymap);
            }
        }
        mymap.addLayer(markersVd);
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