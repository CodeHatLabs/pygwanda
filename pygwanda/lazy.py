class LazyMorpher(object):
    """
        Use:
            m = LazyMorpher(factory)
            m = LazyMorpher(lambda: SomeClass(args))
        Where:
            `factory` is a function that creates and returns an object
            instance; the instance returned by the factory must be of a
            class that inheirts from Python's native `object` class.
        What:
            `m` remains a LazyMorpher instance until you get or set
            an attribute or item on it, or until you invoke it as a
            function (__call__ it), at which time it invokes the
            factory and fully morphs itself into the instance returned
            by the factory.
    """

    def __init__(self, factory):
        self.__dict__['__factory'] = factory

    def __call__(self, *args, **kwargs):
        return self.__morph()(*args, **kwargs)

    def __getattr__(self, key):
        return super().__getattr__(key) \
            if key == '_LazyMorpher__morph' \
            else getattr(self.__morph(), key)

    def __getitem__(self, key):
        return self.__morph()[key]

    def __morph(self):
        self.__dict__['__morphing'] = True
        obj = self.__dict__['__factory']()
        self.__class__ = obj.__class__
        self.__dict__ = obj.__dict__
        return self

    def __setattr__(self, key, value):
        if '__morphing' in self.__dict__:
            super().__setattr__(key, value)
        else:
            setattr(self.__morph(), key, value)

    def __setitem__(self, key, value):
        self.__morph()[key] = value


