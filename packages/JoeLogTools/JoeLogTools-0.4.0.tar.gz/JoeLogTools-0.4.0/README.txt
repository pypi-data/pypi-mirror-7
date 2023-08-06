===========
JoeLogTools
===========

This library contains several decorator methods and a class that should be utilized as a metaclass. The metaclass ensures that each customer class has a Logger adpter object that receives a Logger object as its first argument, and class and instance property dictionaries as its second argument. Additionally each  method is decorated with debug level logging events which indicate the start and end of the method.
