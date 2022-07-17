function getAlert(){
    return fetch('/monitorAlert')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showAlert(data.slice(1, data.length-1)))
}
function toInt(object){
    for (let i=0; i<object.length; i++){
        if (!isNaN(object[i])){
            object[i] = parseInt(object[i])
        }
    }
    return object;
}
function showAlert(object){
    const divide = object.length/2;
    const date = object.slice(0, divide).slice(-10)
    const statusstr = object.slice(divide).slice(-10)
    const status = toInt(statusstr);
    let barConfig = {
        type: 'bar',
        backgroundColor: '#454754',
        borderBottom: '8px solid #565867',
        width: '100%',
        title: {
            text: '民生公開示警平台資料接收狀況',
            fontColor: '#ffffff',
        },
        plot: {
            animation: {
            delay: 0,
            effect: 'ANIMATION_EXPAND_BOTTOM',
            method: 'ANIMATION_LINEAR',
            sequence: 'ANIMATION_NO_SEQUENCE',
            speed: '1000',
            },
            barSpace: '10px',
            rules: 
            [
                {
                    rule: '%v > 1',
                    backgroundColor: '#57dde8'
                }
            ],
        },
        plotarea: {
            margin: '45px 30px 40px 65px',
        },
        scaleX: {
            values: date,
            guide: {
                visible: false,
                },
            item: {
            fontColor: '#c0c0c0',
            fontFamily: 'Arial',
            fontSize: '10px',
            },
            lineColor: '#55717c',
            offsetY: '4px',
            tick: {
            lineColor: '#55717c',
            lineWidth: '1px',
            size: '5px',
            visible: false,
            },
        },
        scaleY: {
            values: '0:3:1',
            guide: {
                alpha: 1,
                lineColor: '#5e606c',
                lineStyle: 'solid',
                },
            item: {
            paddingLeft: '2px',
            fontColor: '#c0c0c0',
            fontFamily: 'Arial',
            fontSize: '10px',
            },
            label: 
            {
                text: '正常/異常',
                fontColor: '#ffffff',
                fontFamily: 'Arial',
                fontSize: '11px',
                fontWeight: 'normal',
                offsetX: '-5px',
            },
            lineColor: 'none',
            multiplier: true,
            tick: {
            visible: false,
            },
        },
        series: [
            {
            values: status,
            tooltip: {
                padding: '5px 10px',
                backgroundColor: '#a03f9c',
                borderRadius: '6px',
                fontColor: '#ffffff',
                shadow: false,
            },
            backgroundColor: '#b857b4',
            },
        ],
    }
    barChart(barConfig)
}
function getRealtime(){
    return fetch('/monitorRealtime')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(res3 => res3.slice(1, res3.length-1))
    .then(res4 => toInt(res4))
    .then(data => showRealtime(data));
    // .then(data => showRealtime(data.slice(1, data.length-1)))
}
function showRealtime(object){
    let realtimebarConfig = {
        type: 'bar',
        backgroundColor: '#454754',
        borderBottom: '8px solid #565867',
        width: '50%',
        x: '20%',
        title: {
            text: '即時數量與平均數量比較',
            backgroundColor: 'none',
            fontColor: '#ffffff',
            fontFamily: 'Arial',
        },
        legend: {
            item: {
                // 'background-color': "#454754",
                'font-color': '#ffffff',
            },
            x: "73%",
            y: "13%",
            'background-color': "#454754",
        },
        plot: {
            valueBox: {
            visible: false,
            },
            animation: {
            delay: 0,
            effect: 'ANIMATION_EXPAND_VERTICAL',
            method: 'ANIMATION_LINEAR',
            sequence: 'ANIMATION_BY_PLOT',
            speed: '300',
            },
        },
        plotarea: {
            margin: '60px 10px 40px 65px',
        },
        scaleX: {
            values: [
              '停車場資訊',
              '路況資訊',
            ],
            guide: {
              visible: false,
            },
            item: {
              fontColor: '#c0c0c0',
              fontFamily: 'Arial',
              fontSize: '15px',
            },
            lineColor: '#55717c',
            offsetY: '4px',
            tick: {
              lineColor: '#55717c',
              lineWidth: '1px',
              size: '5px',
              visible: false,
            },
          },
          scaleY: {
            values: '0:2000:500',
            guide: {
              alpha: 1,
              lineColor: '#5e606c',
              lineStyle: 'solid',
            },
            item: {
              paddingLeft: '2px',
              fontColor: '#c0c0c0',
              fontFamily: 'Arial',
              fontSize: '10px',
            },
            label: {
              text: '資料量',
              fontColor: '#ffffff',
              fontFamily: 'Arial',
              fontSize: '15px',
              fontWeight: 'normal',
              offsetX: '-5px',
            },
            lineColor: 'none',
            multiplier: true,
            tick: {
              visible: false,
            },
          },
          series: [
            {
              values: [
                object[2], object[8],
              ],
              text: '歷史數量',
              tooltip: {
                padding: '5px 10px',
                backgroundColor: '#54ced4',
                borderRadius: '6px',
                fontColor: '#454754',
                shadow: false,
              },
              backgroundColor: '#28A4CF',
            },
            {
              values: [
                object[4], object[10],
              ],
              text: '即時數量',
              tooltip: {
                padding: '5px 10px',
                backgroundColor: '#a03f9c',
                borderRadius: '6px',
                fontColor: '#ffffff',
                shadow: false,
              },
              backgroundColor: '#96feff',
            },
          ],
    }
    realtimeChart(realtimebarConfig);
}

function renderLineConfig(xvalue, yvalue, yscale, title){
    let lineConfig = {
        backgroundColor: '#454754',
        graphset: [
          {
            type: 'line',
            backgroundColor: '#454754',
            width: '100%',
            x: '0%',
            title: {
              text: title,
              backgroundColor: 'none',
              fontColor: '#ffffff',
            },
            plotarea: {
              margin: '75px 75px 17px 67px',
            },
            scaleX: {
              values: xvalue,
              flat: false,
              guide: {
                visible: false,
              },
              item: {
                tooltip: {
                  text: '%months',
                },
                fontColor: '#c0c0c0',
                fontFamily: 'Arial',
                fontSize: '10px',
              },
              label: {
                fontColor: '#ffffff',
                fontFamily: 'Arial',
                fontSize: '11px',
                fontWeight: 'normal',
              },
              lineColor: '#55717c',
              offsetY: '4px',
              tick: {
                visible: false,
              },
            },
            scaleY: {
                values: yscale,
                guide: {
                  alpha: 1,
                  lineColor: '#5e606c',
                  lineStyle: 'solid',
                },
                item: {
                  fontColor: '#c0c0c0',
                  fontFamily: 'Arial',
                  fontSize: '10px',
                },
                label: {
                  text: '數量',
                  fontColor: '#ffffff',
                  fontFamily: 'Arial',
                  fontSize: '15px',
                  fontWeight: 'normal',
                },
                lineColor: 'none',
                multiplier: true,
                tick: {
                  visible: false,
                },
              },
              
            series: [
            {
            type: 'line',
            values: yvalue,
            tooltip: {
                padding: '5px 10px',
                backgroundColor: '#54ced4',
                borderRadius: '6px',
                fontColor: '#454754',
                shadow: false,
            },
            animation: {
                delay: 500,
                effect: 'ANIMATION_EXPAND_LEFT',
                method: 'ANIMATION_LINEAR',
                sequence: 'ANIMATION_BY_PLOT',
                speed: '1800',
            },
            lineColor: '#96feff',
            lineWidth: '2px',
            marker: {
                backgroundColor: '#a3bcb8',
                borderColor: '#88f5fa',
                borderWidth: '2px',
                shadow: false,
            },
            scales: 'scale-x,scale-y',
            },
        ],
          },
          ],
    };
    return lineConfig
}
function getDaily(){
    return fetch('/monitorDaily')
    .then(res => res.text())
    .then(res2 => res2.split(/[',\s\[\]]+/))
    .then(res3 => toInt(res3))
    .then(data => showDaily(data.slice(1, data.length-1)))
    
}
function showDaily(object){
    const date = [];
    const cctv = [];
    const lot = [];
    const vd = [];
    for (let i=0; i<object.length; i+=4){
        date.push(object[i]);
        cctv.push(object[i+1]);
        lot.push(object[i+2]);
        vd.push(object[i+3]);
    }
    zingchart.render({
        id: 'parkChart',
        data: renderLineConfig(date, lot, '0:500000:100000', '即時車位資訊日增加量'),
        height: '100%',
        width: '100%',
    });
    zingchart.render({
        id: 'vdChart',
        data: renderLineConfig(date, vd, '0:500000:100000', '路況資訊日增加量'),
        height: '100%',
        width: '100%',
    });
    zingchart.render({
        id: 'cctvChart',
        data: renderLineConfig(date, cctv, '0:500:100', '監控錄像數量'),
        height: '100%',
        width: '100%',
    });
}

function barChart(object){
    zingchart.render({
        id: 'barChart',
        data: object,
        height: '100%',
        width: '100%',
    });
}

function realtimeChart(object){
    zingchart.render({
        id: 'realtimebarChart',
        data: object,
        height: '100%',
        width: '100%',
    });
}

getAlert();
getRealtime();
getDaily();