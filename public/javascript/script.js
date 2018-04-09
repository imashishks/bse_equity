$("#loader").fadeIn("slow");
var searchInput = $("#search-input");
function makeRequest() {
    $("#table-body").html(" ");
    $("#table").fadeOut("slow");
    $("#loader").fadeIn("slow");
    var req = $.ajax({
        url: "/stock?keyword=" + searchInput.val().toUpperCase(),
        method: "GET"
    });
    req.done(function (data) {
        data = "[" + data.replace(/.$/, "") + "]"
        data = JSON.parse(data);
        var tr = "";
        if (!data.length) {
            tr = `<tr><td></td><td></td><td>No data found for <b>${searchInput.val()} </b></td><td></td><td></td></tr>`

        } else {
            data.forEach(function (t) {
                tr += `<tr><td>${t.CODE}</td><td>${t.NAME}</td><td>${t.OPEN}</td><td>${t.HIGH}</td><td>${t.LOW}</td><td>${t.CLOSE}</td></tr>`
            })
        }
        $("#loader").fadeOut("slow");
        $("#table").fadeIn("slow");
        $("#table-body").html(tr);
    })

    req.fail(function () {

    })
}
var debounceTimeout = null;
makeRequest();
searchInput.on('change keyup', function (event) {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(makeRequest, 300);
});
