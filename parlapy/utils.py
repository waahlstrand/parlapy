def filter_method(obj, param):

    def method(query):

        obj.params.update({obj.param_map[param]: query})

        return obj

    return method