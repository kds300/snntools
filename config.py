class Config:
    def __init__(self, parameters:dict={}, **kwargs):
        _params = {}
        for param_src in [parameters, kwargs]:
            for key, val in param_src.items():
                if type(val) == dict:
                    _params[key] = Config(val)
                else:
                    _params[key] = val
        # super().__init__(**_params)
        self.__dict__.update(_params)

    def as_dict(self):
        out = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Config):
                out[k] = v.as_dict()
            else:
                out[k] = v
        return out

    def __repr__(self):
        return f"{type(self).__name__}({self.as_dict()})"

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = Config(value)
        self.__dict__[key] = value

    def __setattr__(self, name, value):
        self.__setitem__(name, value)
