========
Usage
========

To use ThriftAsyncIOServer in a project::

    from thriftasyncioserver import Server
    from thrift.protocol import TBinaryProtocol
    from my_service import MyService

    class MyHandler(object):
        def function1(self):
    
    server = Server('localhost',
                    2005, 
                    TBinaryProtocol.TBinaryProtocolFactory()
                    MyService.Processor(MyHandler()))
                    
    server.serve()