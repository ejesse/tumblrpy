import logging
import datetime
import time
log = logging.getLogger('tumblr')

def dict_to_object_value(field_name,obj,dict_object,type='string',object_field_name=None,dict_field_name=None,importance=logging.WARN):
    if object_field_name is None:
        object_field_name = field_name
    if dict_field_name is None:
        dict_field_name = field_name
    if importance==logging.DEBUG:
        log.debug('attempting to set ' + field_name)
    if dict_object.has_key(dict_field_name):
        value = dict_object[dict_field_name]
        try:
            if type == 'datetime':
                value = datetime.datetime.fromtimestamp(value)
            elif type == 'int':
                value = int(value)
                
            setattr(obj, object_field_name, value)
        except:
            message = 'failed to set field %s with value %s' % (object_field_name,value)
            logging.WARN(message)
        
        setattr(obj, object_field_name, value)
    else:
        log.warn('field ' + dict_field_name + ' not found')
        
def remove_nones(dict):
    new_dict = {}
    for key in dict.keys():
        if dict[key] is not None:
            if dict[key] is not '':
                log.debug('Preserving key %s with value %s' % (key,dict[key]))
                value = dict[key]
                if isinstance(value,datetime.datetime):
                    value = int(time.mktime(dict[key].timetuple()))
                new_dict[key] = value
            else:
                log.debug("Removing key %s with value ''" % (key))
        else:
            log.debug("Removing key %s with value None" % (key))
    return new_dict

def to_unicode_or_bust(
    obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj