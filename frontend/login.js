// API gateway SDK
var apigClient = apigClientFactory.newClient();
// var apigClient = apigClientFactory.newClient({
//   accessKey: 'ACCESS_KEY',
//   secretKey: 'SECRET_KEY',
// });

document.getElementById('user-input').style.height="100px";
document.getElementById('user-input').style.fontSize="48pt";

var outputArea = $("#chat-output");

$("#user-input-form").on("submit", function(e) {
  
  e.preventDefault();
  
  var OTP = $("#user-input").val();
  
  // outputArea.append(`
  //   <div class='user-message'>
  //     <div class='message'>
  //       ${message}
  //     </div>
  //     <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcSyp6RH-mqsYvUvEzr4pvBZ6IkiCp7fSg4puh5P7uCbuNZS_79J" alt="Avatar2">
  //   </div>
  // `);

  var params = {"otp": OTP};
  var body = {
  "queryStringParameters": {
    "otp": OTP
  },
  "httpMethod": "GET", 
  
};
  var additionalParams = {};

  apigClient.doorlockGet(params, body, additionalParams)
    .then(function(result){
      setTimeout(function() {
        if (result['data']['name'] != null){
        outputArea.empty();
        outputArea.append(`
          <div class='bot-message'>
            <div class='message'>
              Welcome back ${result['data']['name']} !
            </div>
          </div>
        `);} else {
        outputArea.empty();
	      outputArea.append(`
          <div class='bot-message'>
            <div class='message'>
              Invalid OTP!
            </div>
          </div>
        `);
	      }
	 
      }, 250);

        
    }).catch( function(result){
      console.log("fail");
    });

  $("#user-input").val("");
  
});