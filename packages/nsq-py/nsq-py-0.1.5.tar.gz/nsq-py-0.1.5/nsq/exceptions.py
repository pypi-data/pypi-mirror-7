'''Exception classes'''


class NSQException(Exception):
    '''Base class for all exceptions in this library'''


class TimeoutException(NSQException):
    '''Exception for failing a timeout'''


class InvalidException(NSQException):
    '''Exception for E_INVALID'''
    name = 'E_INVALID'


class BadBodyException(NSQException):
    '''Exception for E_BAD_BODY'''
    name = 'E_BAD_BODY'


class BadTopicException(NSQException):
    '''Exception for E_BAD_TOPIC'''
    name = 'E_BAD_TOPIC'


class BadChannelException(NSQException):
    '''Exception for E_BAD_CHANNEL'''
    name = 'E_BAD_CHANNEL'


class BadMessageException(NSQException):
    '''Exception for E_BAD_MESSAGE'''
    name = 'E_BAD_MESSAGE'


class PubFailedException(NSQException):
    '''Exception for E_PUB_FAILED'''
    name = 'E_PUB_FAILED'


class MpubFailedException(NSQException):
    '''Exception for E_MPUB_FAILED'''
    name = 'E_MPUB_FAILED'


class FinFailedException(NSQException):
    '''Exception for E_FIN_FAILED'''
    name = 'E_FIN_FAILED'


class ReqFailedException(NSQException):
    '''Exception for E_REQ_FAILED'''
    name = 'E_REQ_FAILED'


class TouchFailedException(NSQException):
    '''Exception for E_TOUCH_FAILED'''
    name = 'E_TOUCH_FAILED'
