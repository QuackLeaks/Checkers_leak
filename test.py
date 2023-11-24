import requests as req
import re
import threading
from flask import Flask, request, jsonify
app = Flask(__name__)


def worker(proxies, post_url, results_list):
    result = tg_views(proxies, post_url)
    results_list.append(result)


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"


__config__ = {
    # replace your proxy here
    "proxy": "isp2.hydraproxy.com:9989:jais52340nowg221172:XNT43j1YsvZK7wUc",
    # secret api key
    "apikey": "hyperxd2023"
}


def getProxy(proxy: str):
    line = proxy.split(":")
    line = line if len(line) >= 4 else None
    if line:
        host, port, user, pas = line
        return {
            "http": f"http://{user}:{pas}@{host}:{port}",
            "https": f"http://{user}:{pas}@{host}:{port}"
        }
    return None


def tg_views(proxies: dict, post_link: str):
    link = re.findall(r'https://t.me/(\S+)/(\d+)', post_link)
    post_link = "/".join(["https://t.me"] + list(link[0])) if link else None
    retries = 0
    while 1:
        try:
            session = req.session()
            headers = {
                'referer': post_link,
                'user-agent': user_agent
            }
            session.proxies = proxies
            r = session.get(
                f'{post_link}?embed=1&mode=tme', headers=headers)
            status, text = r.status_code, r.text
            if status != 200:
                return {"message": "Request failed", "status": status}
            token = re.findall(r'data-view="([^"]+)"', r.text)
            if not token:
                return {"message": "Request failed no token found", "status": status}

            headers = {
                'referer': f'{post_link}?embed=1&mode=tme',
                'user-agent': user_agent, 'x-requested-with': 'XMLHttpRequest'
            }
            r2 = session.post('https://t.me/v/?views=' +token[0], headers=headers)
            print(" | ".join([str(r2.status_code), token[0]]))
            return {"message": "Request succeeded" if r2.status_code == 200 else "failed", "status": r2.status_code, "token": token[0]}
        except Exception as er:
            print("400 | Proxy Error")
            retries += 1


app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


@app.route("/")
def root():
    return jsonify({"message": "listening", })


@app.route("/tg_views", methods=["GET"])
def process_views():
  try:
    _px = request.args.get("proxy", None)
    proxies = getProxy(__config__.get('proxy'))
    if _px:
       proxies =  getProxy(_px)
    

    limit = request.args.get("limit", 100, type=int)
    post_url = request.args.get("link", None)
    if not post_url:
        return jsonify({"message": "post_url is required", "success": False}), 400

    results = []
    threads = []

    for _ in range(limit):
        thread = threading.Thread(
            target=worker, args=(proxies, post_url, results))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    threadReq = [result for result in results if "proxy error" not in result['message']]
    print(threadReq)
    print(len(threadReq))
    if not threadReq:
        return jsonify({"success": False, "message": "proxy error occured..."}), 400
    count = len(threadReq)
    return jsonify({"requested": count, "success":  count > 0, "post_url": post_url, "message": "succeed" if count > 0 else "failed"}), 200
  except Exception as er:
   return {"message": str(er), "success":False}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
