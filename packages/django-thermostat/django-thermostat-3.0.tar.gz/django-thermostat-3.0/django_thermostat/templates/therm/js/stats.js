Date.prototype.format = function(format) //author: meizz
{
  var o = {
    "M+" : this.getMonth()+1, //month
    "d+" : this.getDate(),    //day
    "h+" : this.getHours(),   //hour
    "m+" : this.getMinutes(), //minute
    "s+" : this.getSeconds(), //second
    "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
    "S" : this.getMilliseconds() //millisecond
  }

  if(/(y+)/.test(format)) format=format.replace(RegExp.$1,
    (this.getFullYear()+"").substr(4 - RegExp.$1.length));
  for(var k in o)if(new RegExp("("+ k +")").test(format))
    format = format.replace(RegExp.$1,
      RegExp.$1.length==1 ? o[k] :
        ("00"+ o[k]).substr((""+ o[k]).length));
  return format;
}



function make_base_auth(user, password) {
  var tok = user + ':' + password;
  var hash = btoa(tok);
  return "Basic " + hash;
}
function load_stats_old() {

    $(document).ready(function () {
        var line1 = [
            ['2008-09-30 4:00PM', 4],
            ['2008-10-30 4:00PM', 6.5],
            ['2008-11-30 4:00PM', 5.7],
            ['2008-12-30 4:00PM', 9],
            ['2009-01-30 4:00PM', 8.2]
        ];
        var plot1 = $.jqplot('plot_div', [line1], {
            title: 'Default Date Axis',
            axes: {xaxis: {renderer: $.jqplot.DateAxisRenderer}},
            series: [
                {lineWidth: 4, markerOptions: {style: 'square'}}
            ]
        });
    });
}
function load_stats(){


    var lines = []
    var series = []
    $.ajax({
        url: "{%url 'dumy_stats'%}",
        dataType: "json",
        success: function(data){
            $.each(data, function(k, v){
                series.push({label: k})
                lines.push([])

                $.each(v, function(k, vv){

                    var d = new Date(0);
                    d.setUTCSeconds(k);

                    var i = lines.length -1
                    if (lines[i] == "undefined") lines[i ] = []
                    lines[i].push([d, vv ])
                    delete d, i;
                })

            })
            console.log(lines)
            //console.log(series)
            $.jqplot("plot_div", lines, {
                  title:'Temperature evolution for last day',
                  // Series options are specified as an array of objects, one object
                  // for each series.
                  seriesDefaults:{
                      shadowAlpha: 0.2,
                      lineWidth:2,
                      markerOptions: { show: false }
                  },
                  series: series,
                        legend: {
                          show: true,
                          location: 'nw',
                          placement: 'inside',
                        fontSize: '11px'
                    } ,

                axes: {
                    // options for each axis are specified in seperate option objects.
                    xaxis: {
                      label: "Date",
                      // Turn off "padding".  This will allow data point to lie on the
                      // edges of the grid.  Default padding is 1.2 and will keep all
                      // points inside the bounds of the grid.
                      renderer:$.jqplot.DateAxisRenderer,
                        showTicks: true,
                    },
                    yaxis: {
                      label: "Temperature(celsius)"
                    }
                  }
                })

        },
        beforeSend: function (xhr){xhr.setRequestHeader('Authorization', make_base_auth("raton", "soportep"));},
    })
    delete lines, series;


}