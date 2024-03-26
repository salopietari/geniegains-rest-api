from backend.models import *
from backend.checks import check_user_permission
from django.db.models import Q
from datetime import datetime

def get_model_data(user: CustomUser, model: models.Model, additional_model: models.Model=None, additional_filter: dict=None) -> list:
    '''
    Retrieve all objects of type model belonging to the user and filtered by additional_model&/filter (optional),
    and return a list of dictionaries where each key represents an object of model, 
    with the values of the key being the values of the object
    '''
    try:
        # used for get all additions regarding goal / tracking
        if additional_model is not None and additional_filter is not None:
            objects = model.objects.filter(user=user, **additional_filter)
        # used for get all objects of user as well as public objects (admin created)
        elif additional_model is None and additional_filter is not None:
            objects = model.objects.filter(Q(user=user) | Q(**additional_filter)).distinct()
        # default case, get all objects of user
        else:
            objects = model.objects.filter(user=user)

        data_list = []
        for obj in objects:
            obj_data = {}
            for field in obj._meta.fields:
                if isinstance(field, models.ForeignKey):
                    continue
                obj_data[field.name] = getattr(obj, field.name)
            data_list.append(obj_data)
        return data_list
    
    except Exception as e:
        raise Exception(e)

def delete_object(user: CustomUser, model: models.Model, object_id: int) -> None:
    '''
    Delete the object of type model with id object_id if the user has permission to do so
    '''
    try:
        obj = model.objects.get(id=object_id)
        check_user_permission(user, model, object_id)
        obj.delete()
    
    except Exception as e:
        raise Exception(e)
    
def convert_unix_time_to_normal(seconds: int) -> str:
    '''
    Convert a unix timestamp (seconds that have elapsed since the Unix epoch, 
    which is defined as 00:00:00 UTC on January 1, 1970, not counting leap seconds) 
    to a normal date string
    '''
    try:
        normal_date = seconds/1000
        normal_date = datetime.fromtimestamp(normal_date)
        return normal_date
    
    except Exception as e:
        raise Exception(e)
    
def reset_query_quota(user: CustomUser) -> None:
    '''
    Reset user's query quota to the defined default in models.py 
    if the last query was not made today
    '''
    try:
        if user.last_query.date() < timezone.now().date():
            user.query_quota = user._meta.get_field('query_quota').default
            user.save()

    except Exception as e:
        raise Exception(e)
    
def decrement_query_quota(user: CustomUser) -> None:
    '''
    Decrement user's query quota by 1
    and update the last query to the current time
    '''
    try:
        user.query_quota -= 1
        user.last_query = timezone.now()
        user.save()

    except Exception as e:
        raise Exception(e)