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
    },
    plotarea: {
        margin: '45px 30px 40px 65px',
    },
    scaleX: {
        values: [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
        ],
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
        values: '0:50000:10000',
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
        text: 'Sales by Employee',
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
        values: [
            31000, 39500, 24300, 36000, 38000, 45500, 28500, 38000, 21000,
            17000, 24000, 17500,
        ],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#54ced4',
            borderRadius: '6px',
            fontColor: '#454754',
            shadow: false,
        },
        backgroundColor: '#57dde8',
        },
        {
        values: [
            11500, 36750, 7000, 44500, 11500, 28450, 42900, 26750, 13050, 32600,
            12500, 14300,
        ],
        tooltip: {
            padding: '5px 10px',
            backgroundColor: '#796bdd',
            borderRadius: '6px',
            fontColor: '#ffffff',
            shadow: false,
        },
        backgroundColor: '#978af6',
        },
        {
        values: [
            21500, 29550, 14500, 16500, 28450, 35600, 21550, 18750, 11600, 7500,
            14750, 16000,
        ],
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

zingchart.render({
    id: 'barChart',
    data: barConfig,
    height: '100%',
    width: '100%',
});