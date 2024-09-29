import flask
import utils.config
import utils.errors
import flask_cors

def create_app():
    app = flask.Flask(__name__)
    app.config.from_object(utils.config.Config)
    
    flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

    from routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/api')

    # Registering the error handler for ValidationError
    @app.errorhandler(utils.errors.ValidationError)
    def handle_validation_error(error):
        response = flask.jsonify({'error': error.message})
        response.status_code = error.status_code
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
