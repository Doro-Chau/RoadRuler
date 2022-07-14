function getAlert(){
    return fetch('/monitorAlert')
    .then(res => res.text())
    .then(res2 => res2.split(/[,'\s\[\]]+/))
    .then(data => showAlert(data.slice(1, data.length-1)))
}
function showAlert(object){
    const divide = object.length/2;
    // console.log(divide, object);
    const date = object.slice(0, divide).slice(-10)
    const status = object.slice(divide).slice(-10)
    for (let i=0; i<status.length; i++){
        status[i] = parseInt(status[i])
    }
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
getAlert();

let pieConfig = {
    type: 'pie',
    backgroundColor: '#454754',
    width: '34%',
    x: '66%',
    title: {
        backgroundColor: 'none',
        fontColor: '#ffffff',
        fontFamily: 'Arial',
        fontWeight: 'normal',
        height: '40px',
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
        margin: '60px 10px 0px 0px',
    },
    series: [
        {
        text: 'Product 1',
        values: [15],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#54ced4',
            borderRadius: '6px',
            fontColor: '#454754',
            shadow: false,
        },
        backgroundColor: '#57dce5',
        borderColor: '#454754',
        borderWidth: '1px',
        shadow: false,
        },
        {
        text: 'Product 2',
        values: [18],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#796bdd',
            borderRadius: '6px',
            fontColor: '#ffffff',
            shadow: false,
        },
        backgroundColor: '#9688f7',
        borderColor: '#454754',
        borderWidth: '1px',
        shadow: false,
        },
        {
        text: 'Product 3',
        values: [20],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#a03f9c',
            borderRadius: '6px',
            fontColor: '#ffffff',
            shadow: false,
        },
        backgroundColor: '#b659b4',
        borderColor: '#454754',
        borderWidth: '1px',
        shadow: false,
        },
        {
        text: 'Product 4',
        values: [16],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#1b9ede',
            borderRadius: '6px',
            fontColor: '#ffffff',
            shadow: false,
        },
        backgroundColor: '#3bbcfc',
        borderColor: '#454754',
        borderWidth: '1px',
        shadow: false,
        },
        {
        text: 'Product 5',
        values: [21],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#2f6672',
            borderRadius: '6px',
            fontColor: '#ffffff',
            shadow: false,
        },
        backgroundColor: '#6597a2',
        borderColor: '#454754',
        borderWidth: '1px',
        shadow: false,
        },
    ],
}


let mixConfig = {
    backgroundColor: '#454754',
    graphset: [
      {
        type: 'mixed',
        backgroundColor: '#454754',
        width: '70%',
        title: {
          text: '日資料',
          paddingLeft: '20px',
          backgroundColor: 'none',
          fontColor: '#ffffff',
          fontFamily: 'Arial',
          fontSize: '18px',
          fontWeight: 'normal',
          height: '40px',
          textAlign: 'left',
          y: '10px',
        },
        plotarea: {
          margin: '75px 75px 5px 67px',
        },
        scaleX: {
          values: ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
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
          values: '0:100000:20000',
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
            text: 'Net Profit',
            fontColor: '#ffffff',
            fontFamily: 'Arial',
            fontSize: '11px',
            fontWeight: 'normal',
          },
          lineColor: 'none',
          multiplier: true,
          tick: {
            visible: false,
          },
        },
        scaleY2: {
          values: '0:500:100',
          guide: {
            visible: false,
          },
          item: {
            fontColor: '#c0c0c0',
            fontFamily: 'Arial',
            fontSize: '10px',
          },
          label: {
            text: 'Units Sold',
            fontColor: '#ffffff',
            fontFamily: 'Arial',
            fontSize: '11px',
            fontWeight: 'normal',
            offsetX: '5px',
          },
          lineColor: 'none',
          multiplier: true,
          tick: {
            visible: false,
          },
        },
        series: [
          {
            type: 'bar',
            values: [
              48000, 31000, 62000, 40500, 44550, 29500, 46000, 70050, 39500,
              45800, 29000, 15000,
            ],
            tooltip: {
              padding: '5px 10px',
              backgroundColor: '#2f6672',
              borderRadius: '6px',
              shadow: false,
            },
            animation: {
              delay: 0,
              effect: 'ANIMATION_EXPAND_BOTTOM',
              method: 'ANIMATION_LINEAR',
              sequence: 'ANIMATION_NO_SEQUENCE',
              speed: '1000',
            },
            backgroundColor: '#6597a2',
            hoverState: {
              visible: false,
            },
          },
        {
        type: 'line',
        values: [110, 58, 104, 357, 294, 367, 285, 340, 397, 425, 254, 187],
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
        scales: 'scale-x,scale-y-2',
        },
    ],
      },
      ],
};

zingchart.render({
    id: 'mixChart',
    data: mixConfig,
    height: '100%',
    width: '100%',
});

zingchart.render({
    id: 'pieChart',
    data: pieConfig,
    height: '100%',
    width: '100%',
});

function barChart(object){
    zingchart.render({
        id: 'barChart',
        data: object,
        height: '100%',
        width: '100%',
    });
}