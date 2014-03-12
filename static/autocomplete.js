var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

$("#search").keyup(function() {
    delay(function(){
        $.post(
            "/search",
            {query:$("#search").val()},
            function(data, textStatus, req) {
                html = "";
                window.data = data;
                $.each(data, function(idx, q) {
                    html += "<tr><td width=55>"+q.id+"</td><td>"+q.body+"</td></tr>";
                });

                $("#resultstable").html(html)
            },
            "json"
        );
    }, 1000)
});