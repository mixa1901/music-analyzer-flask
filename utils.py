from flask import jsonify


def return_json(api_func):
    def decorate_api_func(*args, **kwargs):
        response_data = api_func(*args, **kwargs)
        if isinstance(response_data, list):
            return jsonify(
                {
                    "info": response_data
                }
            )
        elif isinstance(response_data, dict):
            return jsonify(
                {
                    "info": [response_data]
                }
            )
        else:
            return jsonify({
                "error": {
                    "message": "Bad data type returns from Flask API function"
                }
            }), 500
    return decorate_api_func
