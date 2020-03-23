// API gateway SDK
var apigClient = apigClientFactory.newClient();
// var apigClient = apigClientFactory.newClient({
//   accessKey: 'ACCESS_KEY',
//   secretKey: 'SECRET_KEY',
// });


// interactive model
//
//const messages = document.getElementById('chat-output');
//
//function scrollToBottom() {
//  messages.scrollTop = messages.scrollHeight;
//}

var faceId = new URLSearchParams(window.location.search).get("faceId");
var visitorPhoto;

function loadPhoto(photo) {
    var bucket = photo["bucket"];
    var id = photo["objectKey"];
    var url = "https://" + bucket + ".s3.amazonaws.com/" + id;
    document.getElementById("visitorPhoto").src = url;
    visitorPhoto = [photo];
    console.log(visitorPhoto);
}

$(window).on("load", function() {
    var params = {"faceId": faceId};
    var body = "";
    var additionalParams = "";

    apigClient.doorkeyGet(params, body, additionalParams)
      .then(function(result){
        setTimeout(function() {
            loadPhoto(result["data"]["photo"].slice(-1)[0]);
        }, 250);
      }).catch( function(result){
        console.log("fail");
      });
});

$("#owner-decision-form").on("submit", function(e) {
    var outputArea = $("#panel");
    var name = $("#name").val();
    var phoneNumber = $("#phoneNumber").val();
    e.preventDefault();
    var message = $("input[name='decision']:checked").val();
    if (message == "allow") {
        var params = {};
        var body = {"faceId": faceId, "is_granted": true, "phoneNumber": phoneNumber, "name": name, "photos": visitorPhoto};
        console.log(body);
        var additionalParams = "";
        apigClient.doorkeyPost(params, body, additionalParams)
            .then(function(result){
                setTimeout(function(){
                    if (result == null){
                        outputArea.html("<h1> Fail to access database</h1>");
                    }
                    else {
                        console.log(result);
                        outputArea.html("<h1> Allow access </h1>");
                    }
                }, 250);
            }).catch(function(result){
                outputArea.html("<h1> Fail to access database</h1>");
            });
    }
    else {
        outputArea.html("<h1> Deny access </h1>");
    }
});
