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

function loadPhoto(photo) {
    var bucket = photo["bucket"];
    var id = photo["objectKey"];
    var url = "https://" + bucket + ".s3.amazonaws.com/" + id;
    console.log(url);

    document.getElementById("visitorPhoto").src = url;
}

$(window).on("load", function() {
    var params = new URLSearchParams(window.location.search);
    var params = {"faceId": params.get("faceId")};
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
