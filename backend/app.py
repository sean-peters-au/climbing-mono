from flask import Flask, g, jsonify
import mongoengine
import utils.config
import utils.errors
import services
import flask_cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(utils.config.Config)

    with app.app_context():
        services.init_services(app)
    
    mongoengine.connect(
        app.config['MONGODB_SETTINGS']['db'],
        host = app.config['MONGODB_SETTINGS']['host'],
    )

    flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

    from routes.wall import wall_blueprint
    app.register_blueprint(wall_blueprint, url_prefix='/api')

    # Registering the error handler for ValidationError
    @app.errorhandler(utils.errors.ValidationError)
    def handle_validation_error(error):
        response = jsonify({'error': error.message})
        response.status_code = error.status_code
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
