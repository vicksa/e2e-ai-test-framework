"""Tiny Flask app used as a real target for the generated Playwright tests.

Not a real authentication system — just enough UI (labeled fields, a named
button, and a result message) to demonstrate the generated test scripts
actually driving a browser end-to-end.
"""
from __future__ import annotations

from flask import Flask, request

app = Flask(__name__)

_VALID_USERS = {"victoria": "secret123"}

_PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Demo Login</title></head>
<body>
  <h1>Sign in</h1>
  <form method="post" action="/login">
    <label for="username">Username</label>
    <input id="username" name="username" type="text">
    <label for="password">Password</label>
    <input id="password" name="password" type="password">
    <button type="submit">Login</button>
  </form>
  {message}
</body>
</html>"""


@app.get("/login")
def login_form() -> str:
    return _PAGE.format(message="")


@app.post("/login")
def login_submit() -> str:
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if _VALID_USERS.get(username) == password:
        message = f"<p>Welcome, {username}</p>"
    else:
        message = "<p>Invalid credentials</p>"
    return _PAGE.format(message=message)


if __name__ == "__main__":
    app.run(port=5000)
