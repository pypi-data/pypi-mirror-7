import msgpack
from mixins import mixins


class Remote(object):
    """
    Base class for all remote objects(Buffer, Window...).i
    """
    def __init__(self, handle):
        """
        This is the only initializer remote objects need
        """
        self.handle = handle


class Client(object):
    """
    Neovim client. It depends on a stream, an object that implements two
    methods:
        - read(): Returns any amount of data as soon as it's available
        - write(chunk): Writes data

    Both methods should be fully blocking.
    """
    def __init__(self, stream):
        self._request_id = 0
        self._stream = stream
        self._unpacker = msgpack.Unpacker()
        self.vim = None

    def _msgpack_rpc_request(self, method_id, params):
        """
        Sends a msgpack-rpc request to Neovim and returns the response
        """
        # increment request id
        request_id = self._request_id + 1
        self._stream.write(msgpack.packb([0, request_id, method_id, params]))
        # Enter a loop feeding the unpacker with data until we parse
        # the response
        result = None
        while not result:
            try:
                result = self._unpacker.next()
            except StopIteration:
                self._unpacker.feed(self._stream.read())
        # update request id
        self._request_id = request_id
        return result

    def discover_api(self):
        """
        Discovers the remote API using the special method '0'. After this
        the client will have a `vim` attribute containing an object
        that implements an interface similar to the one found in the
        python-vim module(legacy python->vim bridge)
        """
        if self.vim:
            # Only need to do this once
            return
        api = msgpack.unpackb(self._msgpack_rpc_request(0, [])[3])
        # This singleton is the main entry point of the api
        self.vim = type('Vim', (), {})()
        # Build classes for manipulating the remote structures, assigning to a
        # dict using lower case names as keys, so we can easily match methods
        # in the API.
        classes = {'vim': self.vim} # The vim object is a singleton
        for cls in api['classes']:
            klass = type(cls + 'Base', (Remote,), {})
            # Methods of this class will pass an integer representing the
            # remote object as first argument
            klass.requires_handle = True
            classes[cls.lower()] = klass
            setattr(self.vim, cls, klass)
        # now build function wrappers
        for function in api['functions']:
            # Split the name on underscores, the first part is the class name,
            # the remaining is the function name
            class_name, method_name = function['name'].split('_', 1)
            generate_wrapper(self,
                             classes[class_name],
                             method_name,
                             function['id'],
                             function['return_type'],
                             function['parameters'])
        # Now apply all available mixins to the generated classes
        for name, mixin in mixins.items():
            klass = type(name, (getattr(self.vim, name), mixin), {})
            setattr(self.vim, name, klass)

def generate_wrapper(client, klass, name, fid, return_type, parameters):
    """
    Generate an API call wrapper
    """
    # Build a name->pos map for the parameters 
    parameter_names = {}
    parameter_count = 0
    for param in parameters:
        parameter_names[param[1]] = parameter_count
        parameter_count += 1
    # This is the actual function
    @fname(name)
    def rv(*args, **kwargs):
        argv = [None] * parameter_count
        i = 0
        # fill with positional arguments
        for arg in args:
            if hasattr(client.vim, parameters[i][0]):
                # If the type is a remote object class, we use it's remote
                # handle instead
                arg = arg.handle
            # Add to the argument vector 
            argv[i] = arg
            i += 1
        # fill with keyword arguments
        for kw, arg in kwargs.items():
            i = parameter_names[kw]
            if hasattr(client.vim, parameters[i][0]):
                # Same as anove
                arg = arg.handle
            argv[i] = arg
        result = client._msgpack_rpc_request(fid, argv)
        if result[2]:
            # error
            raise Exception(result[2])
        if hasattr(client.vim, return_type):
            # result should be a handle, wrap in it's specialized class
            return getattr(client.vim, return_type)(result[3])
        return result[3]
    setattr(klass, name, rv)


def fname(name):
    """
    Helper for renaming generated functions
    """
    def dec(f):
        f.__name__ = name
        return f
    return dec
