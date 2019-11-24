from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal
import os
import requests
import json


app = Flask(__name__)
api = Api(app)


task_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}

privateCloudIp = "http://3.135.123.239:8080"


class TaskListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided', location='json')
        self.reqparse.add_argument(
            'description', type=str, default="", location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        response = requests.get(privateCloudIp + "/tasks")

        return {"Response": response.json()}

    def post(self):

        args = self.reqparse.parse_args()

        task = {
            'title': args['title'],
            'description': args['description'],
            'done': False
        }

        headers = {'content-type': 'application/json'}

        response = requests.post(
            privateCloudIp + "/tasks", data=json.dumps(task), headers=headers)

        return {"Response": response.json()}, 201


class TaskAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument(
            'description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        response = requests.get(privateCloudIp + "/tasks/{0}".format(id))
        task = response.json()
        return {'Reponse': task}

    def put(self, id):
        args = self.reqparse.parse_args()
        response = requests.put(privateCloudIp + "/tasks/{0}".format(id), args)
        response = response.json()
        return {'Response': response}

    def delete(self, id):

        response = requests.delete(privateCloudIp + "/tasks/{0}".format(id))
        response = response.json()
        return {'Response': response}


api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint='task')

if __name__ == '__main__':
    app.run(host=os.getenv('LISTEN', '0.0.0.0'), port=int(
        os.getenv('PORT', '8080')), debug=True)
