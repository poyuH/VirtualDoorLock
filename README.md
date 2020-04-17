# VirtualDoorLock

# Introduction
**Note: this repository is maintained by: [@poyuH](https://github.com/poyuH), [@Raghav](https://github.com/ragvri), [@Jefflin413](https://github.com/Jefflin413).**

We built a Virtual door lock that let you see the visitors and grand access to them remotely.

## Working 

Here is how it works:

Once an unidentified visitor approach your webcam, a meessage will be sent to your phone
![alt text](https://raw.githubusercontent.com/poyuH/VirtualDoorLock/master/misc/message.png)

After clicking the url, the face of the visitor will be shown and you can decide whether to grand him access or not.
![alt text2](https://raw.githubusercontent.com/poyuH/VirtualDoorLock/master/misc/owner_website.png)

Once you grand access to the visitor, the vistor can get One Time Passcode(OTP) to access your recources.
![alt text3](https://raw.githubusercontent.com/poyuH/VirtualDoorLock/master/misc/otp.png)
![alt text4](https://raw.githubusercontent.com/poyuH/VirtualDoorLock/master/misc/otp1.png)

## Architecture
![alt text5](https://raw.githubusercontent.com/poyuH/VirtualDoorLock/master/misc/architecture.png)

1. **Visitor Vault**

    1. Create a S3 bucket to store the photos of the visitors.
    
    1. Create a DynamoDB table “passcodes” that stores temporary access codes to your virtual door and a reference to the visitor it was assigned to. Use the TTL feature1 of DynamoDB to expire the records after 5 minutes.
    
    1. Create a DynamoDB table “visitors” that stores details about the visitors that your Smart Door system is interacting with.
    
    1. Index each visitor by the FaceId detected by Amazon Rekognition2 (more in the next section), alongside the name of the visitor and their phone number. When storing a new face, if the FaceId returned by Rekognition already exists in the database, append the new photo to the existing photos array. Use the following schema for the JSON object:
        
        {
        “faceId”: “{UUID}”,
        “name”: “Jane Doe”,
        “phoneNumber”: “+12345678901”, 
        “photos”: [
        {
        “objectKey”: “my-photo.jpg”, “bucket”: “my-photo-bucket”, “createdTimestamp”:
        “2018-11-05T12:40:02” 
        }]
        
1. **Analyze**
    
    1. Create a Kinesis Video Stream3, that will be used to capture and stream video for analysis.
        
        1. Download the KVS Producer SDK GStreamer plugin4
      
        1. Get an IP camera5 or simulate one on your device to create an RTSP video stream.
      
        1. Run one of the GStreamer commands6 outlined in the GStreamer documentation to stream your RSTP source to Kinesis Video Streams.
    1. Subscribe Rekognition Video7 to the Kinesis Video Stream .
    1. Output the Rekognition Video analysis to a Kinesis Data Stream and trigger a Lambda function for every event that Rekognition Video outputs.
    1. For every known face detected by Rekognition, send the visitor an SMS message to the phone number on file. The text message should include a PIN or a One-Time Passcode (OTP) that they can use to open the virtual door.
        1. Store the OTP in the “passcodes” table, with a 5 minute expiration timestamp.
    1. For every unknown face detected by Rekogniton, send an SMS to the “owner” (i.e. yourself or a team member) a photo9 of the visitor. The text message should also include a link to approve access for the visitor.
        1. If clicked, the link should take you to a simple web page that collects the name and phone number of the visitor via a web form.
            1. Submitting this form should create a new record in the “visitors” table, indexed by the FaceId identified by Rekognition. Note that you will have to build your own API to send information from the form to the backend. Its design and implementation is left up to you.
            1. Generate a OTP as in step (d) above and store it in the “passcodes” table, with a 5 minute expiration timestamp.Send the visitor an SMS message to the phone number on file. The text message should include the OTP.
1. Authorize
    1. Create a second web page, the “virtual door”, that prompts the user to input the OTP.
        1. If the OTP is valid, greet the user by name and present a success message.
        1. If the OTP is invalid, present a “permission denied” message.
