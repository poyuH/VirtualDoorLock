# search_faces_by_image()
import boto3
import cv2
import os
from acesskeys import aws_access_key_id, aws_secret_access_key

session = boto3.Session(aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

kvs_client = session.client('kinesisvideo')
kvs_data_pt = kvs_client.get_data_endpoint(
    StreamName='KVS_visitor',
    APIName='GET_MEDIA'
)

kds_client = session.client('kinesis')

rekognition = session.client('rekognition')


def create_collection(resource, id):
    response = resource.create_collection(CollectionId=id)
    # print(response)


def delete_collection(resource, id):
    resource.delete_collection(CollectionId=id)


delete_collection(rekognition, 'face_search')
create_collection(rekognition, 'face_search')
end_pt = kvs_data_pt['DataEndpoint']
# print(end_pt)
kvs_video_client = session.client(
    'kinesis-video-media', endpoint_url=end_pt, region_name='us-east-1')  # provide your region

rekognition = session.client('rekognition')
previous_id = None

while True:
    kvs_stream = kvs_video_client.get_media(
        StreamName='KVS_visitor',
        # to keep getting latest available chunk on the stream
        StartSelector={'StartSelectorType': 'NOW'}
    )
    with open('stream.mp4', 'wb') as f:
        streamBody = kvs_stream['Payload'].read(1024*16384//16)
        f.write(streamBody)
        # use openCV to get a frame

    print('written')
    cap = cv2.VideoCapture('stream.mp4')
    ret, frame = cap.read()
    # use some logic to ensure the frame being read has the person, something like bounding box or median'th frame of the video etc
    count = 0
    while ret:
        if count % 50 == 0:
            _, encoded_image = cv2.imencode('.jpg', frame)
            image = encoded_image.tobytes()
            face_exists = rekognition.detect_faces(Image={'Bytes': image})
            if face_exists['FaceDetails']:
                response = rekognition.search_faces_by_image(CollectionId='face_search',
                                                             Image={'Bytes': image}, MaxFaces=1, FaceMatchThreshold=95)
                if response['FaceMatches']:
                    print('matched')
                    face = response['FaceMatches'][0]
                    face_id = face['Face']['FaceId']
                    if not previous_id or face_id != previous_id:
                        print('Putting')
                        previous_id = face_id
                        print(f'faceid: {face_id}')
                        # put in kds
                        kds_client.put_record(
                            StreamName='analyze', Data=image, PartitionKey='f')

                else:
                    print('notmatched')
                    response = rekognition.index_faces(
                        CollectionId='face_search',
                        Image={'Bytes': image}, DetectionAttributes=['DEFAULT'], MaxFaces=1)
                    if response['FaceRecords']:
                        face_id = response['FaceRecords'][0]['Face']['FaceId']
                        print(face_id)
                        previous_id = face_id
                        # put in kds
                        print('Putting')
                        print(f'faceid: {face_id}')
                        kds_client.put_record(
                            StreamName='analyze', Data=image, PartitionKey='f')

        ret, frame = cap.read()
        count += 1
    cap.release()
    print('released')
    os.remove('stream.mp4')
