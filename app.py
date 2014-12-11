from flask import Flask, redirect, request

application = Flask(__name__)

@application.route("/oauth/authorize", methods=['GET'])
def authorization():
    resp_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')

    if redirect_uri is None:
        return "Bad redirect_uri", 401
    if client_id is None or resp_type is None:
        return redirect(redirect_uri + "?error=invalid_request",401)
    if resp_type != "code":
        return redirect(redirect_uri + "?error=unsupproted_responce_type",401)
    return

@application.route("/oauth/token", methods=['POST'])
def handletoken():
    resp_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')

    if redirect_uri is None:
        return "Bad redirect_uri", 401
    if client_id is None or resp_type is None:
        return redirect(redirect_uri + "?error=invalid_request",401)
    if resp_type != "code":
        return redirect(redirect_uri + "?error=unsupproted_responce_type",401)

if __name__ == "__main__":
    application.run()