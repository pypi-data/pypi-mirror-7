# coding=utf-8
from logging import getLogger

from django.core.cache import cache
from django_sae.utils.timestamp import make_timestamp, to_datetime


log = getLogger('django.cache')


class Model(object):
    KEYS = ()
    VALUES = ()

    def __init__(self, expires_in):
        self.expired_at = None
        self.expires_in = expires_in

    @property
    def key(self):
        keys = []
        for attr in self.KEYS:
            value = getattr(self, attr)
            if value is None:
                raise KeyError(u'组装键时出现错误：属性{0}的值不能为None'.format(attr))
            keys.append(str(value))
        keys.insert(0, self.__class__.__name__)
        return '_'.join(keys)

    @property
    def value(self):
        values = {}
        attr_list = list(self.VALUES)
        attr_list.append('expired_at')
        for attr in attr_list:
            value = getattr(self, attr)
            if value is None:
                raise ValueError(u'属性{0}的值不能为None'.format(attr))
            values[attr] = value
        return values

    def _get_expires_in(self):
        if self.expired_at:
            return self.expired_at - make_timestamp()

    def _set_expires_in(self, expires_in):
        if expires_in:
            self.expired_at = int(expires_in) + make_timestamp()

    expires_in = property(_get_expires_in, _set_expires_in)

    def load_values(self, **values):
        for key, value in values.items():
            setattr(self, key, value)

    def load_cache(self):
        values = cache.get(self.key)
        if values is not None:
            self.load_values(**values)

    @property
    def is_expires(self):
        return self.expired_at is None or make_timestamp() >= self.expired_at

    def save(self):
        if not self.is_expires:
            log.debug(u'[{2}][缓存]{0}：{1}'.format(self.key, self.value, to_datetime(self.expired_at)))
            # times秒数如果大于30天，则需传入到期时间的时间戳(且必须为整数)
            cache.set(self.key, self.value, int(self.expired_at))

    def delete(self):
        self.expired_at = None
        cache.delete(self.key)

