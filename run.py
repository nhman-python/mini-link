from index import app
from module import db

db.init_app(app)
with app.app_context():
    db.create_all()
    app.run()