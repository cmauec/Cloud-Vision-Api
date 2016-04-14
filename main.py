# -*- coding: utf-8 -*-
#
# Copyright 2016 Carlos Vaca
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.appengine.api import urlfetch
from google.appengine.api import images
from google.appengine.api import app_identity
import json
import base64
import urllib
import jinja2
import os
import cgi
import cloudstorage as gcs
from PIL import Image
import StringIO
import random
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient import errors


key_google_translate = 'AIzaSyC2zOdsCTQcdhkW0PUZZGYE_jhPBLr2IqI' #clave de api para utilizar el API de Google Translate
api = 'https://vision.googleapis.com/$discovery/rest?version=v1'
scopes = ['https://www.googleapis.com/auth/cloud-platform']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'secret.json', scopes)
http = credentials.authorize(httplib2.Http())
vision_service = build("vision", "v1", http=http,discoveryServiceUrl=api)

urlfetch.set_default_fetch_deadline(60)


jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.abspath('.')))

emotions_score = {
    'UNKNOWN':'Desconocido',
    'VERY_UNLIKELY':'Muy improbable',
    'UNLIKELY':'Improbable',
    'POSSIBLE':'Posible',
    'LIKELY': 'Probable',
    'VERY_LIKELY':'Muy probable'
}
emotions = {
    'joyLikelihood':u'Alegría',
    'sorrowLikelihood':'Dolor',
    'angerLikelihood':'Ira',
    'surpriseLikelihood':'Sorpresa',
    'underExposedLikelihood':'Subexpuesta',
    'blurredLikelihood':'Borrosa',
    'headwearLikelihood':'Accesorios'
}


class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('view/index.html')
        template_vars = {}
        self.response.write(template.render(template_vars))

class VisionElementsHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('view/vision/elements.html')
        template_vars = {}
        self.response.write(template.render(template_vars))

    def post(self):
        upload_files = self.request.POST['imgpage']
        if len(str(upload_files)) > 0:
            try:
                image = images.Image(image_data=upload_files.value)
            except: 
                self.response.write('No es una imagen valida')
                return
            try: 
                if image.format == images.JPEG:
                    extension_file = '.jpg'
                    typeMIME = 'image/jpeg'
                    format = 'JPEG'
                elif image.format == images.PNG:
                    extension_file = '.png'
                    typeMIME = 'image/png'
                    format = 'PNG'
                elif image.format == images.GIF:
                    extension_file = '.gif'
                    typeMIME = 'image/gif'
                    format = 'GIF'
                else:
                    self.response.write(u'La imagen no tiene un formato válido')
                    return
            except: 
                self.response.write('No es una imagen valida')
                return
            image_content = base64.b64encode(upload_files.value)
            service_request = vision_service.images().annotate(
            body={
                    'requests': [{
                      'image': {
                        'content': image_content
                       },
                      'features': [{
                        'type': 'LABEL_DETECTION',
                        'maxResults': 15,
                       }]
                     }]
            }
            )
            response = service_request.execute()
            if('responses' in response and 'labelAnnotations' in response['responses'][0]):
                labels = response['responses'][0]['labelAnnotations']
            else:
                labels = None
            labels_array = []
            if not labels:
                self.response.write('No se pudo procesar la imagen')
                return
            for label in labels:
                form_fields = {
                    'key': key_google_translate,
                    'q': urllib.quote(label['description']),
                    'source': 'en',
                    'target': 'es'
                }
                form_data = urllib.urlencode(form_fields)
                result = urlfetch.fetch(
                    url='https://www.googleapis.com/language/translate/v2?key={0}&q={1}&source={2}&target={3}'.format(form_fields['key'],form_fields['q'],form_fields['source'],form_fields['target']),
                    method=urlfetch.GET)
                translated = json.loads(result.content)
                # self.response.write(translated['data']['translations'][0]['translatedText'])
                # return
                labels_array.append({'description':translated['data']['translations'][0]['translatedText'],'score':label['score']})
            template = jinja_environment.get_template('view/vision/elements.html')
            template_vars = {
                'labels':labels_array,
                'image':'data:{0};base64,{1}'.format(typeMIME,image_content)
            }
            self.response.write(template.render(template_vars))
        else:
            self.response.write('Escoge una imagen')

class VisionFacesHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('view/vision/faces.html')
        template_vars = {}
        self.response.write(template.render(template_vars))

    def post(self):
        upload_files = self.request.POST['imgpage']
        if len(str(upload_files)) > 0:
            try:
                image = images.Image(image_data=upload_files.value)
            except: 
                self.response.write('No es una imagen valida')
                return
            try: 
                if image.format == images.JPEG:
                    extension_file = '.jpg'
                    typeMIME = 'image/jpeg'
                    format = 'JPEG'
                elif image.format == images.PNG:
                    extension_file = '.png'
                    typeMIME = 'image/png'
                    format = 'PNG'
                elif image.format == images.GIF:
                    extension_file = '.gif'
                    typeMIME = 'image/gif'
                    format = 'GIF'
                else:
                    self.response.write(u'La imagen no tiene un formato válido')
                    return
            except: 
                self.response.write('No es una imagen valida')
                return
            image_content = base64.b64encode(upload_files.value)
            service_request = vision_service.images().annotate(
            body={
                    'requests': [{
                      'image': {
                        'content': image_content
                       },
                      'features': [{
                        'type': 'FACE_DETECTION',
                        'maxResults': 15,
                       }]
                     }]
            }
            )
            response = service_request.execute()
            if('responses' in response and 'faceAnnotations' in response['responses'][0]):
                faces = response['responses'][0]['faceAnnotations']
                im = Image.open(StringIO.StringIO(upload_files.value))
                output = StringIO.StringIO()
                faces_array = []
                for face in faces:
                    color = "#%06x" % random.randint(0, 0xFFFFFF)
                    box = [(v['x'], v['y']) for v in face['fdBoundingPoly']['vertices']]
                    faces_array.append({
                        emotions['joyLikelihood']:emotions_score[face['joyLikelihood']],
                        emotions['sorrowLikelihood']:emotions_score[face['sorrowLikelihood']],
                        emotions['angerLikelihood']:emotions_score[face['angerLikelihood']],
                        emotions['surpriseLikelihood']:emotions_score[face['surpriseLikelihood']],
                        emotions['underExposedLikelihood']:emotions_score[face['underExposedLikelihood']],
                        emotions['blurredLikelihood']:emotions_score[face['blurredLikelihood']],
                        emotions['headwearLikelihood']:emotions_score[face['headwearLikelihood']],    
                        'color':color,
                        'coordenadas':box,
                        'width':image.width,
                        'height':image.height,
                        'ratio':float("{0:.2f}".format(float(image.height)/float(image.width)))
                        })
                im.save(output, format)
                image_faces = base64.b64encode(output.getvalue())
                image_faces_exist = True
            else:
                faces = None
                image_faces = None
                image_faces_exist = False
                faces_array = None
            template = jinja_environment.get_template('view/vision/faces.html')
            template_vars = {
                'faces':faces_array,
                'image_faces_exist':image_faces_exist,
                'image':'data:{0};base64,{1}'.format(typeMIME,image_faces)
            }
            self.response.write(template.render(template_vars))
        else:
            self.response.write('Escoge una imagen')

class VisionOCRHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('view/vision/ocr.html')
        template_vars = {}
        self.response.write(template.render(template_vars))

    def post(self):
        upload_files = self.request.POST['imgpage']
        if len(str(upload_files)) > 0:
            try:
                image = images.Image(image_data=upload_files.value)
            except: 
                self.response.write('No es una imagen valida')
                return
            try: 
                if image.format == images.JPEG:
                    extension_file = '.jpg'
                    typeMIME = 'image/jpeg'
                    format = 'JPEG'
                elif image.format == images.PNG:
                    extension_file = '.png'
                    typeMIME = 'image/png'
                    format = 'PNG'
                elif image.format == images.GIF:
                    extension_file = '.gif'
                    typeMIME = 'image/gif'
                    format = 'GIF'
                else:
                    self.response.write(u'La imagen no tiene un formato válido')
                    return
            except: 
                self.response.write('No es una imagen valida')
                return
            image_content = base64.b64encode(upload_files.value)
            service_request = vision_service.images().annotate(
            body={
                    'requests': [{
                      'image': {
                        'content': image_content
                       },
                      'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 15,
                       }]
                     }]
            }
            )
            response = service_request.execute()
            if('responses' in response and 'textAnnotations' in response['responses'][0]):
                texts = response['responses'][0]['textAnnotations']
            else:
                texts = None
            template = jinja_environment.get_template('view/vision/ocr.html')
            template_vars = {
                'texts':texts,
                'image':'data:{0};base64,{1}'.format(typeMIME,image_content)
            }
            self.response.write(template.render(template_vars))
        else:
            self.response.write('Escoge una imagen')

app = webapp2.WSGIApplication([
    ('/vision/elements',VisionElementsHandler),
    ('/vision/faces',VisionFacesHandler),
    ('/vision/ocr',VisionOCRHandler),
    ('/', MainHandler),
], debug=True)
