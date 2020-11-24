let get_temp = async () => {
    let result = await fetch("/temp")
    let temp = await result.json()
    return temp
}
var layout = {
    xaxis: {
        visible: false
    },
    yaxis: {
        range: [0, -90],
        dtick: 10
    }
};

(async () => {
    let result = await get_temp()
    let temp = await result['temp']
    Plotly.plot('chart',[{
        y:[temp],
        type:'line'
    }], layout);
})()


var cnt = 0;
setInterval(async function(){
    
    try {
        let result = await get_temp()
        let temp = await result['temp']
        console.log(temp)
        Plotly.extendTraces('chart',{ y:[[temp]]}, [0]);
        $("#temp").text(temp.toFixed(2))
    } catch {
        $("#temp").text('ERROR')
    }
    
    
},1000);



