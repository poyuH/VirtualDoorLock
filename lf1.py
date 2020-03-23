import base64
import json
import boto3
import datetime
import random
import string


def generateCode(length=7):
    return ''.join(random.choices(string.digits, k=length))


def send_sns_message(message, phone_number="+12292997716"):
    if not phone_number.startswith('+'):
        phone_number = '+1'+phone_number
    sns.publish(Message=message, PhoneNumber=phone_number)


print('Loading function')

rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')
visitors = dynamodb.Table('visitors')
passcodes = dynamodb.Table('passcodes')
photo = dynamodb.Table('photo')
sns = boto3.client('sns')
visitors_photos = boto3.client('s3')


def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    print(f"The number of records is {len(event['Records'])}")
    for record in event['Records']:
        # Kinesis data is base64 encoded so decode here
        image = base64.b64decode(record['kinesis']['data'])
        face_exists = rekognition.detect_faces(Image={'Bytes': image})
        if face_exists['FaceDetails']:
            response = rekognition.search_faces_by_image(CollectionId='face_search',
                                                         Image={'Bytes': image}, MaxFaces=1, FaceMatchThreshold=95)
            if response['FaceMatches']:
                print('matched')
                face = response['FaceMatches'][0]
                face_id = str(face['Face']['FaceId'])
                # check if face_id in the visitors dynamo db (faceId)
                known = visitors.get_item(
                    Key={'faceId': face_id}).get('Item', None)

                if known:
                    visitors_photos.put_object(ACL='public-read',
                                               Body=image, Bucket='visitorphotos', Key=f"{face_id}/{len(known['photos'])}.jpg", ContentType='image/jpeg')

                    photos = [{'bucket': 'visitorphotos', 'createdTimeStamp': str(
                        (datetime.datetime.now())), 'objectKey': f"{face_id}/{len(known['photos'])}.jpg"}]
                    known['photos'].extend(photos)
                    visitors.update_item(
                        Key={'faceId': face_id},
                        UpdateExpression='SET photos = :val1',
                        ExpressionAttributeValues={
                            ':val1': known['photos']
                        }
                    )

                    OTP = generateCode()
                    passcodes.put_item(Item={'OTP': OTP, 'faceId': face_id,
                                             'ttl': 300+int(datetime.datetime.now().strftime("%s"))})
                    send_sns_message('your OTP is '+str(OTP),
                                     known['phoneNumber'])

                else:
                    photos = [{'bucket': 'visitorphotos', 'createdTimeStamp': str(
                        (datetime.datetime.now())), 'objectKey': f"{face_id}/0.jpg"}]

                    visitors_photos.put_object(ACL='public-read',
                                               Body=image, Bucket='visitorphotos', Key=f"{face_id}/0.jpg", ContentType='image/jpeg')
                    photo.put_item(
                        Item={'faceId': str(face_id), 'photo': photos})
                    url = f'http://owner.com.s3-website.us-east-1.amazonaws.com?faceId={face_id}'
                    message = f'An unidentified person is trying to get in: {url}'
                    send_sns_message(message)
                    # print(message)

    return 'Successfully processed {} records.'.format(len(event['Records']))