from app import create_app
from app.views.view import views_bp
app, celery = create_app()
app.register_blueprint(views_bp)
if __name__ == '__main__':
    with app.app_context():
        from app.models import db
        db.create_all()
    app.run()
