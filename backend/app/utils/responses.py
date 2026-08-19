"""
Standardized API response helpers.

Keeping response shape consistent across every endpoint makes the frontend
service layer simple: it always knows whether to look at `data` or `error`.
"""

from flask import jsonify


def success(data=None, message="Success", status_code=200):
    payload = {"success": True, "message": message, "data": data}
    return jsonify(payload), status_code


def error(message="Something went wrong", status_code=400, errors=None):
    payload = {"success": False, "message": message, "errors": errors}
    return jsonify(payload), status_code
