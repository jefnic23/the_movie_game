from flask import Flask

app=Flask(__name__)
app.secret_key = "replace later"

from app import routes