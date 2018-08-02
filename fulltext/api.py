"""Provides the blueprint for the fulltext API."""

from flask import request, Blueprint, Response
from flask.json import jsonify
from arxiv import status
from fulltext import controllers

blueprint = Blueprint('fulltext', __name__, url_prefix='/fulltext')


def best_match(available, default):
    """Determine best content type given Accept header and available types."""
    if 'Accept' not in request.headers:
        return default
    return request.accept_mimetypes.best_match(available)


@blueprint.route('/status', methods=['GET'])
def ok() -> tuple:
    """Provide current integration status information for health checks."""
    return jsonify({'iam': 'ok'}), status.HTTP_200_OK


@blueprint.route('', methods=['POST'])
def extract_fulltext() -> tuple:
    """Handle requests for reference extraction."""
    data, code, headers = controllers.extract(request.get_json(force=True))
    return jsonify(data), code, headers


@blueprint.route('/<string:doc_id>', methods=['GET'])
def retrieve(doc_id):
    """Retrieve full-text content for an arXiv paper."""
    available = ['application/json', 'text/plain']
    content_type = best_match(available, 'application/json')
    data, status_code = controllers.retrieve(doc_id)
    # TODO: this should be generalized if we need it in other places.
    if content_type == 'text/plain':
        response_data = Response(data['content'], content_type='text/plain')
    elif content_type == 'application/json':
        response_data = jsonify(data)
    else:
        return jsonify({'explanation': 'unsupported content type'}), \
            status.HTTP_406_NOT_ACCEPTABLE

    return response_data, status_code


@blueprint.route('/status/<string:task_id>', methods=['GET'])
def task_status(task_id: str) -> tuple:
    """Get the status of a reference extraction task."""
    data, code, headers = controllers.status(task_id)
    return jsonify(data), code, headers
