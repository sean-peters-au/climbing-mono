from flask import Flask, g, jsonify

import betaboard.db.session_manager as db_session_manager
import betaboard.utils.config as config_utils
import betaboard.utils.errors as errors_utils
import betaboard.services as services
import flask_cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(config_utils.Config)

    with app.app_context():
        services.init_services(app)
    
    db_session_manager.SessionManager.init_engine(app.config['POSTGRES']['URI'])

    flask_cors.CORS(app, resources={r"/*": {"origins": "*"}})

    from betaboard.routes import blueprints
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/api')

    app.json.mimetype = 'application/json'

    # Registering the error handler for ValidationError
    @app.errorhandler(errors_utils.ValidationError)
    def handle_validation_error(error):
        response = jsonify({'error': error.message})
        response.status_code = error.status_code
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
