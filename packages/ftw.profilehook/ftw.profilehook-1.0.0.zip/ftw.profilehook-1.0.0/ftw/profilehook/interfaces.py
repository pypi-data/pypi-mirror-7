from zope.interface import Interface


class IProfileHook(Interface):

    def __call__(site, install_context):
        pass
