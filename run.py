from app import create_app

app, celery = create_app()

if __name__ == '__main__':
    with app.app_context():
        from app.models import db
        db.create_all()
    app.run()
