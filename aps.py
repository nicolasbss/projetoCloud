from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal
import os
import pymongo

client = pymongo.MongoClient(
    "mongodb://52.87.213.151:27017")  # defaults to port 27017

db = client['Projeto-Cloud']
taskCollection = db['tasks']
# taskCollection.drop()

app = Flask(__name__)
api = Api(app)


task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}


class TaskListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided', location='json')
        self.reqparse.add_argument(
            'description', type=str, default="", location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        tasks = list(taskCollection.find())
        return {'tasks': [marshal(task, task_fields) for task in tasks]}

    def post(self):
        args = self.reqparse.parse_args()
        tasks = list(taskCollection.find())
        task = {
            'id': tasks[-1]['id'] + 1 if len(tasks) > 0 else 1,
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        taskCollection.insert_one(
            task
        )
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        tasks = list(taskCollection.find())
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            return {'result': '404'}
        return {'task': marshal(task[0], task_fields)}

    def put(self, id):
        tasks = list(taskCollection.find())
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            return {'result': '404'}
        args = self.reqparse.parse_args()
        print(args)
        for k, v in args.items():
            if v is not None:
                taskCollection.update_one({"id": id}, {"$set": {k: v}})
        return {'task': marshal(task, task_fields)}

    def delete(self, id):
        tasks = list(taskCollection.find())
        task = [task for task in tasks if task['id'] == id]
        if len(task) == 0:
            return {'result': '404'}
        taskCollection.delete_one({'id': id})
        return {'result': True}


api.add_resource(TaskListAPI, '/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/tasks/<int:id>', endpoint='task')

if __name__ == '__main__':
    app.run(host=os.getenv('LISTEN', '0.0.0.0'), port=int(
        os.getenv('PORT', '8080')), debug=True)
