# -*- coding: utf-8 -*-

from forwardable import Forwardable, def_delegators

from .model_cache_class import *

valid_storage_types = ("memory", "sqlite", "redis")

class ModelCache():
    @classmethod
    def connect(cls, original_model, **kwargs):
        # assert original_model's behavior
        process_notifier(original_model)

        # setup args
        default_kwargs = {
                    'cache_dir'      : None,
                    'storage_type'   : 'sqlite',
                    'percentage'     : 0.9999,
                    'filter_lambda'  : lambda item1: False,
                    'read_id_lambda' : lambda item1: str(item1['_id']),
                    'included_class' : object,
                }
        for k1, v1 in kwargs.iteritems():
            if k1 in default_kwargs:
                default_kwargs[k1] = v1

        # validate storage
        assert default_kwargs['storage_type'] in valid_storage_types
        if (default_kwargs['cache_dir'] is None) and (default_kwargs['storage_type'] != "memory"):
            raise Exception(u"`cache_dir` should not be None when storage_type is not memory.")

        cache_dir = default_kwargs['cache_dir']
        del default_kwargs['cache_dir']

        # decorate class
        def _model_cache_decorator(decorated_class):
            # 1. included_class should not overwrite ModelCacheClass's important methods,
            #    include `__init__`, `init__before`, `init__after`.
            # 2. ensure decorated_class's methods will overwrite ModelCache's.
            class _model_cache(decorated_class, ModelCacheClass, default_kwargs['included_class']):
                class OriginalClass(): pass # so we can setattr here.
                original = OriginalClass()
                for k1, v1 in default_kwargs.iteritems():
                    setattr(original, k1, v1)
                    del k1; del v1
                original.model   = original_model

                # Thx http://stackoverflow.com/questions/4932438/how-to-create-a-custom-string-representation-for-a-class-object/4932473#4932473
                class MetaClass(type):
                    __metaclass__ = Forwardable
                    _ = def_delegators('datadict', ('__getitem__', '__setitem__', '__delitem__', \
                                                    '__iter__', '__len__', '__contains__', \
                                                    'has_key', 'get', 'pop', 'popitem', \
                                                    'keys', 'values', \
                                                    'items', 'iteritems', 'iterkeys', 'itervalues', ))

                    def __repr__(self):
                        while len(self.first_five_items) < 5:
                            for item_id1, item1 in self.iteritems():
                                self.first_five_items.append(item1)
                                if len(self.first_five_items) == 5: break

                        dots = ", ......" if len(self) > 5 else ""
                        return (u"<%s has %i items:[%s%s]>" % \
                                        (self.__name__, len(self), \
                                        ", ".join([str(item1.item_id) for item1 in self.first_five_items]), \
                                        dots, )).encode("UTF-8")


                __metaclass__ = MetaClass

            _model_cache.__name__   = decorated_class.__name__
            _model_cache.__module__ = decorated_class.__module__ # so can pickle :)

            _model_cache.first_five_items = []

            _model_cache.cache_dir  = cache_dir
            _model_cache.connect()

            return _model_cache
        return _model_cache_decorator
