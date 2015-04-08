from framework.index import get, post, delete, abort
from models.follow import Follow
from framework.session import get_current_user
from modules.entity import get_latest_canonical


@get('/api/follows')
def get_follows_route(request):
    """
    Get a list of the users follows.
    """

    current_user = get_current_user()
    if not current_user.is_authenticated():
        return abort(401)

    follows = Follow.list(user_id=current_user.get_id(), **request['params'])
    return 200, {
        'follows': [follow.deliver(access='private') for follow in follows]
    }


@post('/api/follows')
def follow_route(request):
    """
    Follow a card, unit, or set.
    """

    current_user = get_current_user()
    if not current_user:
        return abort(401)

    follow_data = dict(**request['params'])
    follow_data['user_id'] = current_user.get_id()

    follow = Follow(follow_data)
    errors = follow.validate()
    if errors:
        return 400, {'errors': errors}

    # Ensure the entity exists   TODO should this be a model validation?
    entity = get_latest_canonical(follow['entity']['kind'],
                                  follow['entity']['id'])
    if not entity:
        return abort(404)

    # Ensure we don't already follow   TODO should this be a model validation?
    prev = Follow.list(user_id=current_user.get_id(),
                       entity_id=follow_data['entity']['id'])
    if prev:
        return abort(409)

    follow, errors = follow.save()
    if errors:
        return 400, {'errors': errors}

    return 200, {'follow': follow.deliver(access='private')}


@delete('/api/follows/{follow_id}')
def unfollow_route(request, follow_id):
    """
    Remove a follow. Must be current user's own follow.
    """

    current_user = get_current_user()
    if not current_user:
        return abort(401)

    follow = Follow.get(id=follow_id)
    if not follow:
        return abort(404)

    if follow['user_id'] != current_user.get_id():
        return abort(403)

    follow, errors = follow.delete()
    if errors:
        return 400, {'errors': errors}

    return 200, {}
