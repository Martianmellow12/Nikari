# Nikari Core DB Extension Functions
#
# Written by Martianmellow12

import os

db_extension_path = os.path.dirname(__file__)
__all__ = [i[:-3] for i in os.listdir(db_extension_path) if (i[-3:] == ".py") and (i != "__init__.py")]


##############
# Exceptions #
##############

class UndefinedMethodError(Exception): pass


########################
# Extension Management #
########################

class __Extensions__:
    def __init__(self):
        self.list = list()

EXTENSIONS = __Extensions__()

def db_extension(name):
    def impl(cls):
        extension_obj = cls()
        EXTENSIONS.list.append(extension_obj)
        setattr(EXTENSIONS, name, extension_obj)
        return cls
    return impl


########################
# Extension Base Class #
########################

class DbExtensionBase:

    def __init__(self):
        # These will be set by the DB manager
        self.__db_path__ = None

    async def create_tables(self, db_obj):
        raise UndefinedMethodError("The create_tables method should be defined by children of DbExtensionBase")