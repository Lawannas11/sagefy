"""
Routes for the discussion platform.
Includes topics, posts, proposals, and votes.
"""
# TODO-3 what checks should be moved to models?
from framework.routes import get, post, put, abort
from framework.session import get_current_user
from modules.discuss import instance_post_facade, \
    get_post_facade, get_posts_facade
from modules.util import pick, omit, object_diff
from modules.entity import get_kind, get_latest_accepted, get_version, \
    instance_new_entity
from models.topic import Topic
from models.user import User
from modules.content import get as c
from modules.notices import send_notices


@post('/s/topics')
def create_topic_route(request):
    """
    Create a new topic.
    The first post (or proposal) must be provided.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)

    # ## STEP 1) Create post and topic (and entity) instances
    topic_data = request['params'].get('topic')
    post_data = request['params'].get('post')
    if not topic_data:
        return 400, {
            'errors': [{
                'name': 'topic',
                'message': 'Missing topic data.'
            }],
            'ref': 'zknSd46f2hRNjSjVHCg6YLwN'
        }
    if not post_data:
        return 400, {
            'errors': [{
                'name': 'post',
                'message': 'Missing post data.'
            }],
            'ref': 'Qki4oWX4nTdNAjYI8z5iNawr'
        }
    topic_data = omit(topic_data, ('id', 'created', 'modified'))
    topic_data['user_id'] = current_user['id']
    topic = Topic(topic_data)
    post_data = omit(post_data, ('id', 'created', 'modified',))
    post_data['user_id'] = current_user['id']
    post_data['topic_id'] = topic['id']
    post_ = instance_post_facade(post_data)
    post_kind = post_['kind']
    if post_kind == 'proposal':
        entity = instance_new_entity(request['params'])
        entity_kind = get_kind(request['params'])[0]
        post['entity_version'] = {
            'id': entity['id'],
            'kind': entity_kind,
        }

    # ## STEP 2) Validate post and topic (and entity) instances
    errors = topic.validate() + post_.validate()
    if post_kind == 'proposal':
        errors = errors + entity.validate()
    if len(errors):
        return 400, {
            'errors': errors,
            'ref': 'TAY5pX3ghWBkSIVGTHzpQySa'
        }

    # ## STEP 3) Save post and topic (and entity)
    topic.save()
    post_.save()
    if post_kind == 'proposal':
        entity.save()

    # ## STEP 4) Send out any needed notifications
    send_notices(
        entity_id=topic['entity']['id'],
        entity_kind=topic['entity']['kind'],
        notice_kind='create_topic',
        notice_data={
            'user_name': current_user['name'],
            'topic_name': topic['name'],
            'entity_kind': topic['entity']['kind'],
            'entity_name': topic['entity']['id'],
        }
    )

    # ## STEP 5) Return response
    return 200, {'topic': topic.deliver(), 'post': post_.deliver()}


@put('/s/topics/{topic_id}')
def update_topic_route(request, topic_id):
    """
    Update the topic.
    - Only the name can be changed.
    - Only by original author.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)

    # ## STEP 1) Find existing topic instance ## #
    topic = Topic.get(id=topic_id)
    if not topic:
        return abort(404)
    if topic['user_id'] != current_user['id']:
        return abort(403)

    # ## STEP 2) Limit the scope of changes ## #
    topic_data = request['params']['topic']
    topic_data = pick(topic_data, ('name',))

    # ## STEP 3) Validate and save topic instance ## #
    topic, errors = topic.update(topic_data)
    if errors:
        return 400, {
            'errors': errors,
            'ref': 'k7ItNedf0I0vXfiIUcDtvHgQ',
        }

    # ## STEP 4) Return response ## #
    return 200, {'topic': topic.deliver()}


@get('/s/topics/{topic_id}/posts')
def get_posts_route(request, topic_id):
    """
    Get a reverse chronological listing of posts for given topic.
    Includes topic meta data and posts (or proposals or votes).
    Paginates.
    """

    # Is the topic valid?
    topic = Topic.get(id=topic_id)
    if not topic:
        return 404, {
            'errors': [{
                'name': 'topic_id',
                'message': c('no_topic'),
            }],
            'ref': 'pgnNbqSP1VUWkOYq8MVGPrSS',
        }

    # Pull the entity
    entity_kind = topic['entity']['kind']
    entity = get_latest_accepted(entity_kind,
                                 topic['entity']['id'])

    # Pull all kinds of posts
    posts = get_posts_facade(
        limit=request['params'].get('limit') or 10,
        skip=request['params'].get('skip') or 0,
        topic_id=topic_id
    )

    # For proposals, pull up the proposal entity version
    # ...then pull up the previous version
    # ...make a diff between the previous and the proposal entity version
    diffs = {}
    for post_ in posts:
        if post_['type'] == 'proposal':
            kind = post_['entity_version']['kind']
            entity_version = get_version(kind,
                                         post_['entity_version']['id'])
            previous_version = get_version(kind,
                                           entity_version['previous_id'])
            diff = object_diff(previous_version.deliver(),
                               entity_version.deliver())
            diffs[post_['id']] = diff

    # TODO-2 SPLITUP create new endpoint for this instead
    users = {}
    for post_ in posts:
        user_id = post_['user_id']
        if user_id not in users:
            user = User.get(id=user_id)
            if user:
                users[user_id] = {
                    'name': user['name'],
                    'avatar': user.get_avatar(48)
                }

    # TODO-2 SPLITUP create new endpoints for these instead
    output = {
        'topic': topic.deliver(),
        'posts': [p.deliver() for p in posts],
        'diffs': diffs,
        'users': users,
    }
    if entity:
        output[entity_kind] = entity.deliver()
    return 200, output


@post('/s/topics/{topic_id}/posts')
def create_post_route(request, topic_id):
    """
    Create a new post on a given topic.
    Proposal: must include entity (card, unit, or set) information.
    Vote: must refer to a valid proposal.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)

    topic = Topic.get(id=topic_id)
    if not topic:
        return 404, {
            'errors': [{
                'name': 'topic_id',
                'message': c('no_topic'),
            }],
            'ref': 'PCSFCxsJtnlP0x9WzbPoKcwM',
        }

    # ## STEP 1) Create post (and entity) instances
    post_data = request['params'].get('post')
    if not post_data:
        return 400, {
            'errors': [{
                'name': 'post',
                'message': 'Missing post data.',
            }],
            'ref': 'ykQpZwJKq54MTCxgkx0p6baW'
        }
    post_data = omit(post_data, ('id', 'created', 'modified',))
    post_data['user_id'] = current_user['id']
    post_data['topic_id'] = topic_id
    post_ = instance_post_facade(post_data)
    post_kind = post_['kind']
    if post_kind == 'proposal':
        entity = instance_new_entity(request['params'])
        entity_kind = get_kind(request['params'])[0]
        post['entity_version'] = {
            'id': entity['id'],
            'kind': entity_kind,
        }

    # ## STEP 2) Validate post (and entity) instances
    errors = post_.validate()
    if post_kind == 'proposal':
        errors = errors + entity.validate()
    if len(errors):
        return 400, {
            'errors': errors,
            'ref': 'tux33ztgFj9ittSpS7WKIkq7'
        }

    # ## STEP 3) Save post (and entity)
    post_.save()
    if post_kind == 'proposal':
        entity.save()

    # TODO-0 ## STEP 4) Make updates based on proposal / vote status

    # TODO-1 ## STEP 5) Send out any needed notifications

    # ## STEP 6) Return response
    return 200, {'post': post_.deliver()}


@put('/s/topics/{topic_id}/posts/{post_id}')
def update_post_route(request, topic_id, post_id):
    """
    Update an existing post. Must be one's own post.

    For post:
    - Only the body field may be changed.

    For proposals:
    - Only the name, body, and status fields can be changed.
    - The status can only be changed to declined, and only when
      the current status is pending or blocked.

    For votes:
    - The only fields that can be updated are body and response.
    """

    current_user = get_current_user(request)
    if not current_user:
        return abort(401)

    # ## STEP 1) Find existing post instance ## #
    post_ = get_post_facade(post_id)
    if not post_:
        return abort(404)
    if post_['user_id'] != current_user['id']:
        return abort(403)
    kind = post_['kind']

    # ## STEP 2) Limit the scope of changes ## #
    post_data = request['params']['post']
    if kind is 'post':
        post_data = pick(post_data, ('body',))
    elif kind is 'proposal':
        post_data = pick(post_data, ('name', 'body', 'status',))
        if (post_data.get('status') != 'declined' or
                post_data.get('status') not in ('pending', 'blocked',)):
            del post_data['status']
    elif kind is 'vote':
        post_data = pick(post_data, ('body', 'response',))

    # ## STEP 3) Validate and save post instance ## #
    post_, errors = post_.update(post_data)
    if errors:
        return 400, {
            'errors': errors,
            'ref': 'E4LFwRv2WEJZks7use7TCpww'
        }

    # TODO-0 ## STEP 4) Make updates based on proposal / vote status ## #

    # TODO-1 ## STEP 5) Send out any needed notifications ## #

    # ## STEP 6) Return response ## #
    return 200, {'post': post_.deliver()}
