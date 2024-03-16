from backend.models import *
from django.db.models import Q

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
