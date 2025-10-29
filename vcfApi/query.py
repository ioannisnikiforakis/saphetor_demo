"""
This module contains HTTP Request related helper functions. 
Mainly to be used by the views.
"""
import collections
import urllib

QUERY_STRING = 'QUERY_STRING'
QSTRING_DEL = '&'
FILTER_DEL = '='

def filter_query(metadict,filterset):
    """
    This function translates the filtering parameters from a request.META querystring 
    to something that we can pass directly to the Django ORM filter function for convenience
    
    Args: 
        metadict(dict): The request's META dict that contains the querystring
        filterset(dict): A valid filterset dict with the fields declared as 
                        filterable for the view
    
    Returns:
        my_filters(dict): A dict of key:values ready to be passed to the filter function
    """
    if not metadict or len(metadict) == 0:
        return {}
    my_filters = {}
    my_filterset = filterset
    # If filterset is dict we need to support  {'name':['exact','isnull'], etc
    # which translates to name=value and name__isnull=true filters
    if isinstance(filterset, collections.abc.Mapping):
        my_filterset = []
        for key,mfilter in filterset.items():
            if "exact" in mfilter:
                my_filterset.append(key)
            if "isnull" in mfilter:
                my_filterset.append(key+"__isnull")

    querystring = metadict.get(QUERY_STRING)
    querystring = urllib.parse.unquote(querystring)
    if querystring and len(querystring) > 2:
        parts = [i.strip()  for i in querystring.split(QSTRING_DEL)]
        for part in parts:
            pfilter = part.split(FILTER_DEL)
            if len(pfilter) >1 and pfilter[0] in my_filterset and len(pfilter[1]) > 0:
                value = pfilter[1]
                if value.upper() == "TRUE":
                    value = True
                elif value.upper() == "FALSE":
                    value = False
                my_filters[pfilter[0]] = value

    return my_filters
