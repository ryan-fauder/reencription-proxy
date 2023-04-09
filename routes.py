from flask import Blueprint
from flask_restful import Api
from resources.Hello import Hello
from resources.TokenResource import TokenResource

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Route
api.add_resource(Hello, '/hello')
api.add_resource(TokenResource, '/resource', '/resource/<token>')