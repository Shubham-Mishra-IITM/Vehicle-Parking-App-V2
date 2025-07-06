from backend import create_app, celery

flask_app = create_app()

celery.conf.update(flask_app.config)

if __name__ == '__main__':
    celery.start()