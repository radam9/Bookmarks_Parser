import json


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        t = (Node, object)
        if isinstance(obj, t):
            # data = {"name": obj.name, "type": obj.type}
            # if obj.type == "folder":
            #     data["children"] = obj.children
            # return data
            if obj.type == "folder":
                return obj.f()
            elif obj.type == "url":
                return obj.u()
        return json.JSONEncoder.default(self, obj)


class Some:
    def f(self):
        folder = {
            "name": self.name,
            "type": self.type,
            "children": self.children,
        }
        return folder

    def u(self):
        url = {
            "name": self.name,
            "type": self.type,
        }
        return url


class Node(Some):
    def __init__(self, **kwargs):
        self.name = kwargs.pop("name")
        self.type = kwargs.pop("type")
        if self.type == "folder":
            self.children = kwargs.pop("children")

    def __repr__(self):
        return f"{self.name} - {self.type}"


dic = """{
    "name": "root",
    "type": "folder",
    "children": [
        {"name": "link1",
        "type": "url"},
        {"name": "link2",
        "type": "url"},
        {"name": "folder1",
        "type": "folder",
        "children": [{"name": "link3",
        "type": "url"}]
        }
    ]
}"""


def turn_to_object(jdict):
    return Node(**jdict)


test = json.loads(dic, object_hook=turn_to_object)
x = 0

test2 = json.dumps(test, cls=MyEncoder)

x = 0