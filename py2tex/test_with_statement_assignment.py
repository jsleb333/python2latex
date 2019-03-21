class T:
    def __init__(self):
        self.body = []

    def __enter__(self):
        self.global_vars = {k:v for k,v in globals().items()}
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        new_vars = {k:v for k,v in globals().items() if k not in self.global_vars or v is not self.global_vars[k]}
        del self.global_vars
        for val in new_vars.values():
            if isinstance(val, str) or isinstance(val, T):
                if not self.already_in_other_T(val):
                    self.body.append(val)

    def already_in_other_T(self, val):
        for t in self.body:
            if t is val:
                return True
            elif isinstance(t, T):
                if t.already_in_other_T(val):
                    return True
        return False


class Env:
    def __init__(self, name):
        self.name = name
        self.body = []

    def spy(self):
        return Spy(self)

    def append(self, val):
        self.body.append(val)

    def __repr__(self):
        return self.name

    def __contains__(self, val):
        return val in self.body

    def __iter__(self):
        yield from self.body


class Spy:
    def __init__(self, obj_to_append):
        self.obj_to_append = obj_to_append

    def __enter__(self):
        self.global_vars = {k:v for k,v in globals().items()}
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        new_vars = {k:v for k,v in globals().items() if k not in self.global_vars or v is not self.global_vars[k]}
        for val in new_vars.values():
            if isinstance(val, str) or isinstance(val, type(self.obj_to_append)):
                if not self.already_in_obj_to_append(self.obj_to_append, val):
                    self.obj_to_append.append(val)

    @classmethod
    def already_in_obj_to_append(cls, obj_to_append, val):
        for t in obj_to_append:
            if t is val:
                return True
            elif isinstance(t, type(obj_to_append)):
                if cls.already_in_obj_to_append(t, val):
                    return True
        return False




if __name__ == '__main__':
    t = T()

    # x = '1'
    # with t:
    #     y = '3'
    #     z = 8
    #     w = '5'
    #     tt = T()
    #     with tt:
    #         f = '8'
    #         g = '10'
    #         ttt = T()
    #         with ttt:
    #             k = '12'
    #     x = '9'

    # a = '8'

    t = Env('t')

    x = '1'
    with t.spy():
        y = '3'
        z = 8
        w = '5'
        tt = Env('tt1')
        tt = Env('tt2') # This is the downside: if overwritten, never seen by t
        with tt.spy():
            f = '8'
            g = '10'
            ttt = Env('ttt')
            with ttt.spy():
                k = '12'
        x = '9'

    a = '8'

    print(t.body)
    print(tt.body)
    print(ttt.body)
