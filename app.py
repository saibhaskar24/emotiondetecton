from flask import Flask , request , render_template
import base64
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
import io
import uuid
import azure.cosmos.cosmos_client as cosmos_client

app = Flask(__name__)

cosmos_url = 'https://faceviitdatabase.documents.azure.com:443/'
cosmos_primary_key = ''
cosmos_collection_link = 'dbs/attendies/colls/faces'
client = cosmos_client.CosmosClient(url_connection=cosmos_url,auth = {'masterKey': cosmos_primary_key})
@app.route('/')
def home():
  docs = list(client.ReadItems(cosmos_collection_link))
  return render_template('home.html', result = docs)

face_api_endpoint = 'https://myfaceviit.cognitiveservices.azure.com/'
face_api_key = ''
credentials = CognitiveServicesCredentials(face_api_key)
face_client = FaceClient(face_api_endpoint, credentials=credentials)

def best_emotion(emotion):
  emotions = {}
  emotions['anger'] = emotion.anger
  emotions['contempt'] = emotion.contempt
  emotions['disgust'] = emotion.disgust
  emotions['fear'] = emotion.fear
  emotions['happiness'] = emotion.happiness
  emotions['neutral'] = emotion.neutral
  emotions['sadness'] = emotion.sadness
  emotions['surprise'] = emotion.surprise
  return max(zip(emotions.values(), emotions.keys()))[1]
@app.route('/image', methods=['POST'])
def upload_image():
  json = request.get_json()
  b = base64.b64decode(json['image'])
  image = io.BytesIO(b)
  faces = face_client.face.detect_with_stream(image,return_face_attributes=['age', 'smile', 'emotion'])
  for face in faces:
      doc = {
              'id' : str(uuid.uuid4()),
              'age': face.face_attributes.age,
              'smile': 'Yes' if face.face_attributes.smile > 0.5 else 'No',
              'emotion': best_emotion(face.face_attributes.emotion)
            }
      client.CreateItem(cosmos_collection_link, doc)
  return 'OK'