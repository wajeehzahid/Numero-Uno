# import uuid
# from flask import request, jsonify
# from app import pusher, app
#
#
# @app.route('/post', methods=['POST'])
# def addPost():
#     data = {
#         'id': "post-{}".format(uuid.uuid4().hex),
#         'name': request.form.get('name'),
#         'content': request.form.get('content'),
#         'status': 'active',
#         'event_name': 'created'
#     }
#     pusher.trigger("blog", "post-added", data)
#     return jsonify(data)
#
#
# # update or delete post
# @app.route('/post/<id>', methods=['PUT', 'DELETE'])
# def updatePost(id):
#     data = {'id': id}
#     if request.method == 'DELETE':
#         data['event_name'] = 'deleted'
#         pusher.trigger("blog", "post-deleted", data)
#     else:
#         data['event_name'] = 'deactivated'
#         pusher.trigger("blog", "post-deactivated", data)
#     return jsonify(data)
