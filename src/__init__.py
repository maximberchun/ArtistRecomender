from . import config

__all__ = getattr(config, "__all__", [])
for name in __all__:
	globals()[name] = getattr(config, name)