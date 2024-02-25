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

# supported keys:
# type
# required
# allow_single_item
# default_key
# default_value
# keys
# items
def normalize_schema(spec, orig_data):
    data = deepcopy(orig_data)

    if data is None:
        if "default_value" in spec:
            data = spec["default_value"]

        if "required" in spec and spec["required"] and data is None:
            raise ValidationError([], None, None)


    if data is not None:
        if "allow_single_item" in spec and spec["allow_single_item"] and type(data) is not list:
            data = [data]

        if "items" in spec:
            lst = list()
            for index, item in enumerate(data):
                try: 
                    lst.append(normalize_schema(spec["items"], item))
                except ValidationError as error: 
                    e = error.addPath("[" + str(index) + "]")
                    raise e.with_traceback(None) from None
            data = lst

        if type(data) is not dict and "default_key" in spec:
            data = { spec["default_key"] : data }

    if "keys" in spec and type(data) is dict:
        for key in spec["keys"]:
            subspec = spec["keys"][key]
            subdata = None
            if key in data:
                subdata = data[key]

            try:
                new_data = normalize_schema(subspec, subdata)
                if new_data is not None:
                    data[key] = new_data
            except ValidationError as error: 
                e = error.addPath("." + key)
                raise e.with_traceback(None) from None

    if "type" in spec and not typecheck(spec["type"], data) and data is not None:
        raise ValidationError([], spec["type"], type(data))

    return data

