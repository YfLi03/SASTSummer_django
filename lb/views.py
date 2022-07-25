from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)

from lb.models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from lb import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method


def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })


# 装饰器，限制GET方法
@method(["GET"])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, username: str):
    res = utils.get_history(username)
    print(res)
    if res:
        return JsonResponse({
            "code": 0,
            "data": [model_to_dict(r) for r in res],
        })
    else:
        return JsonResponse({
            "code": -1,
        })


@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    content = json.loads(req.body)
    if "avatar" not in content:
        content["avatar"] = "null"
    if not ("user" in content and "avatar" in content and "content" in content):
        return JsonResponse({
            "code": 1,
            "msg": "参数不全啊"
        })

    if len(content["user"]) > 255:
        return JsonResponse({
            "code": -1,
            "msg": "用户名太长了"
        })

    if len(content["avatar"]) > 1024000:
        return JsonResponse({
            "code": -2,
            "msg": "图像太大了"
        })
    try:
        score, sub = utils.judge(content["content"])
        user = User.objects.filter(username=content["user"])
        print(len(user))
        if len(user) == 0:
            User.objects.create(username=content["user"])
        user = User.objects.get(username=content["user"])
        subs = str(sub[0]) + " " + str(sub[1]) + " " + str(sub[2])
        Submission.objects.create(user=user, avatar=content["avatar"], score=score, subs=subs)
        return JsonResponse({
            "code": 0,
            "msg": "提交成功",
            "data": {
                "leaderboard": utils.get_leaderboard(),
            }
        })
    except Exception as e:
        print(e)
        return JsonResponse({
            "code": -3,
            "msg": "提交内容非法呜呜"
        })


@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers \
            or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })

    body = json.loads(req.body)
    if len(User.objects.filter(username=body["user"])) == 0:
        return JsonResponse({
            "code": -1,
        })
    user = User.objects.get(username=body["user"])
    user.votes = user.votes + 1
    user.save()

    return JsonResponse({
        "code": 0,
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    })
