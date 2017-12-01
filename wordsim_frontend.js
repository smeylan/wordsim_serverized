var payload = {"word":"dog","nsim":50,"adult_surprisal_filter":30,"child_surprisal_filter":30, "nretrieve":5};


$( document ).ready(function() {
    console.log( "ready!" );

    $.ajax({
        type: 'post',
        url: 'http://0.0.0.0:8000/api/getNclosestNodes',
        data: JSON.stringify(payload),
        contentType: "application/json; charset=utf-8",
        traditional: true,
        success: function (data) {
            console.log(data)                    
        },
        error: function (xhr, ajaxOptions, thrownError) {
            console.log(xhr.responseText);        
        }
     });
    console.log("after ajax call")
});



