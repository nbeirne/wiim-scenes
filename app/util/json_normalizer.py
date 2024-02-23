
from copy import deepcopy
import sys

class ValidationError(Exception):
    def __init__(self, path, expected_type, got_type):
        if got_type is None and expected_type is not None:
            super().__init__("missing key {2} of type {1}".format(got_type, expected_type, "".join(path)))
        else:
            super().__init__("unexpected type: {0}. Expected {1} at path {2}".format(got_type, expected_type, "".join(path)))
        self.path = path
        self.expected_type = expected_type
        self.got_type = got_type

    def addPath(self, path):
        self.path = [path] + self.path
        return ValidationError(self.path, self.expected_type, self.got_type)

def typecheck(type_str, value):
    return getattr(sys.modules['builtins'], type_str) == type(value)

def normalize_data(spec, orig_data):
    data = deepcopy(orig_data)

    if data is None:
        if "default_value" in spec:
            data = spec["default_value"]

        if "required" in spec and spec["required"] and data is None:
            raise ValidationError([], spec["type"], None)


    if spec["type"] == "list":
        if "allow_single_item" in spec and spec["allow_single_item"] and type(data) is not list:
            data = [data]

        if "items" in spec and data is not None:
            lst = list()
            for index, item in enumerate(data):
                try: 
                    lst.append(normalize_data(spec["items"], item))
                except ValidationError as error: 
                    e = error.addPath("[" + str(index) + "]")
                    raise e.with_traceback(None) from None
            data = lst

    if spec["type"] == "dict":
        if data is not None and type(data) is not dict and "default_key" in spec:
            data = { spec["default_key"] : data }

        if "keys" in spec and type(data) is dict:
            for key in spec["keys"]:
                subspec = spec["keys"][key]
                subdata = None
                if key in data:
                    subdata = data[key]

                try:
                    new_data = normalize_data(subspec, subdata)
                    if new_data is not None:
                        data[key] = new_data
                except ValidationError as error: 
                    e = error.addPath("." + key)
                    raise e.with_traceback(None) from None

    if not typecheck(spec["type"], data) and data is not None:
        raise ValidationError([], spec["type"], type(data))

    return data

if __name__ == "__main__":
    import json

    def test(spec, data, expected):
        result = normalize_data(spec, data)
        if result != expected:
            print("FAIL: {0} != {1}\ndata: {3}\nspec: {2}".format(json.dumps(expected), json.dumps(result), json.dumps(spec, indent=2), data))

    # basic type tests
    #test({ "type": "int" }, 0, 0)

    ## None with a default_key and default_value produces the default dictionay
    test({"type": "dict", "default_key": "d", "keys": {} }, "test", { "d": "test" } )
    test({"type": "dict", "keys": { "d": { "type": "str", "default_value": "dv", "required": True }} }, {}, { "d": "dv" } )
    test({"type": "dict", "default_key": "d", "keys": { "d": { "type": "str", "required": True }} }, "dv", { "d": "dv" } )
    test({"type": "dict", "default_key": "d", "default_value": {}, "keys": { "d": { "type": "str", "default_value": "dv", "required": True }} }, None, { "d": "dv" } )


    test({"type": "list", "allow_single_item": True }, 1, [1])
    test({"type": "list", "default_value": [] }, None, [])

    test({"type": "list", "allow_single_item": True, "default_value": [] }, None, [])

    test({"type":"dict", "default_key": "a", "keys": { "a": { "type": "dict", "keys": { "b": { "type": "dict", "required": True } } } } }, {}, {})

    test({
        "type": "dict",
        "keys": {
            "input": {
                "type": "dict",
                "default_key": "type",
                "keys": {
                    "type": {
                        "type": "str",
                        "required": True,
                    },
                },
            },
        }
    }, {}, {})


    # below is a complex test.
    basic_spec = {
        "type": "dict",
        "keys": {
            "no_match": {
                "type": "list",
            },
            "default_val": {
                "type": "bool",
                "default_value": True,
                "required": True,
            },
            "insert_lst": {
                "type": "list",
                "allow_single_item": True,
            },
            "insert_dict": {
                "type": "dict",
                "default_key": "key",
            },
            "insert_dict_default": {
                "type": "dict",
                "default_key": "key",
            },
            "dict_default": {
                "type": "dict",
                "default_key": "key",
            },
        }
    }
    spec = {
        "type": "dict",
        "default_key": "some",
        "keys": {
            **basic_spec["keys"],
            "dict_nested": basic_spec,
            "array": {
                "type": "list",
                "items": basic_spec
            }
        }
    }
    basic_data = {
        "nochange": 1,
        "none": None,
        "insert_lst": "ins",
        "insert_dict": "val", # key: key
        "insert_dict_default": "val", # key: key
        "dict_default": {
            "key": "value",
            "default": False,
        },
    }

    data = {
        **basic_data,
        "dict_nested": {
            **basic_data,
        },
        "array": [
            basic_data,
            basic_data,
        ],
    }

    expected = {"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "dict_nested": {"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "default_val": True}, "array": [{"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "default_val": True}, {"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "default_val": True}], "default_val": True}

    test(spec, data, expected)

