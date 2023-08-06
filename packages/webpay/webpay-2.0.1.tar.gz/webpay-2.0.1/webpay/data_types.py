from .error import InvalidRequestError

import re

def normalize(fields, params):
    """Normalize params by dropping unknown fields and None values"""
    new_dict = {}
    for f in fields:
        new_dict[f] = params.get(f, None)
    return new_dict

def stringify_field(value):
    if isinstance(value, list):
       return '[' + ", ".join(map(stringify_field, value)) + ']'
    else:
       return re.sub(r'(\r?\n)', r'\1  ', str(value))

class Entity:
    def to_raw_params(self):
        result = {}
        for k,v in self.__dict__.items():
            result[k] = v.to_raw_params() if hasattr(v, 'to_raw_params') else v
        return result

    def __str__(self):
        result = ['<', self.__class__.__name__, "\n"]
        for field in self.fields:
            result.append('  '); result.append(field); result.append(': ')
            result.append(stringify_field(self.__dict__[field]))
            result.append("\n")
        result.append('>')
        return ''.join(result)


class CardRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['number','exp_month','exp_year','cvc','name']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class ChargeRequestCreate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['amount','currency','customer','shop','card','description','capture','expire_days','uuid']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['card'] = CardRequest(params['card']) if isinstance(params['card'], dict) else params['card']
        self.__dict__ = params


    # attributes setters

    @property
    def card(self):
        return self.__dict__['card']

    @card.setter
    def card(self, value):
        value = CardRequest(value) if isinstance(value, dict) else value
        self.__dict__['card'] = value

class CardResponse(Entity):


    fields = ['object','exp_month','exp_year','fingerprint','last4','type','cvc_check','name','country']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params

class ChargeFeeResponse(Entity):


    fields = ['object','transaction_type','transaction_fee','rate','amount','created']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params

class ChargeResponse(Entity):


    fields = ['id','object','livemode','amount','card','created','currency','paid','captured','refunded','amount_refunded','customer','recursion','shop','description','failure_message','expire_time','fees']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['card'] = CardResponse(params['card']) if isinstance(params['card'], dict) else params['card']
        params['fees'] = list(map(lambda x: ChargeFeeResponse(x) if isinstance(x, dict) else x, params['fees'])) if isinstance(params['fees'], list) else params['fees']
        self.__dict__ = params

class ChargeIdRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, ChargeResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class ChargeRequestWithAmount(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, ChargeResponse):
            return cls({'id': params.id, 'amount': params.amount})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id','amount']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class CreatedRange(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['gt','gte','lt','lte']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class ChargeListRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['count','offset','created','customer','recursion','shop']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['created'] = CreatedRange(params['created']) if isinstance(params['created'], dict) else params['created']
        self.__dict__ = params


    # attributes setters

    @property
    def created(self):
        return self.__dict__['created']

    @created.setter
    def created(self, value):
        value = CreatedRange(value) if isinstance(value, dict) else value
        self.__dict__['created'] = value

class ChargeResponseList(Entity):


    fields = ['object','url','count','data']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['data'] = list(map(lambda x: ChargeResponse(x) if isinstance(x, dict) else x, params['data'])) if isinstance(params['data'], list) else params['data']
        self.__dict__ = params

class CustomerRequestCreate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['card','description','email','uuid']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['card'] = CardRequest(params['card']) if isinstance(params['card'], dict) else params['card']
        self.__dict__ = params


    # attributes setters

    @property
    def card(self):
        return self.__dict__['card']

    @card.setter
    def card(self, value):
        value = CardRequest(value) if isinstance(value, dict) else value
        self.__dict__['card'] = value

class RecursionResponse(Entity):


    fields = ['id','object','livemode','created','amount','currency','period','description','customer','shop','last_executed','next_scheduled','status','deleted']

    def __init__(self, params):
        params = normalize(self.fields, params)
        if params.get('deleted') is None:
          params['deleted'] = False
        self.__dict__ = params

class CustomerResponse(Entity):


    fields = ['id','object','livemode','created','active_card','description','email','recursions','deleted']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['active_card'] = CardResponse(params['active_card']) if isinstance(params['active_card'], dict) else params['active_card']
        params['recursions'] = list(map(lambda x: RecursionResponse(x) if isinstance(x, dict) else x, params['recursions'])) if isinstance(params['recursions'], list) else params['recursions']
        if params.get('deleted') is None:
          params['deleted'] = False
        self.__dict__ = params

class CustomerIdRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, CustomerResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class CustomerRequestUpdate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, CustomerResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id','card','description','email']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['card'] = CardRequest(params['card']) if isinstance(params['card'], dict) else params['card']
        self.__dict__ = params


    # attributes setters

    @property
    def card(self):
        return self.__dict__['card']

    @card.setter
    def card(self, value):
        value = CardRequest(value) if isinstance(value, dict) else value
        self.__dict__['card'] = value

class BasicListRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['count','offset','created']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['created'] = CreatedRange(params['created']) if isinstance(params['created'], dict) else params['created']
        self.__dict__ = params


    # attributes setters

    @property
    def created(self):
        return self.__dict__['created']

    @created.setter
    def created(self, value):
        value = CreatedRange(value) if isinstance(value, dict) else value
        self.__dict__['created'] = value

class CustomerResponseList(Entity):


    fields = ['object','url','count','data']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['data'] = list(map(lambda x: CustomerResponse(x) if isinstance(x, dict) else x, params['data'])) if isinstance(params['data'], list) else params['data']
        self.__dict__ = params

class TokenRequestCreate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, CardRequest):
            return cls({'card': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['card','uuid']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['card'] = CardRequest(params['card']) if isinstance(params['card'], dict) else params['card']
        self.__dict__ = params


    # attributes setters

    @property
    def card(self):
        return self.__dict__['card']

    @card.setter
    def card(self, value):
        value = CardRequest(value) if isinstance(value, dict) else value
        self.__dict__['card'] = value

class TokenResponse(Entity):


    fields = ['id','object','livemode','card','created','used']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['card'] = CardResponse(params['card']) if isinstance(params['card'], dict) else params['card']
        self.__dict__ = params

class TokenIdRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, TokenResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class EventIdRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, EventResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class EventData(Entity):


    fields = ['object','previous_attributes']

    def __init__(self, params):
        params = normalize(self.fields, params)
        if type(params['object']) is not dict or params['object'].get('object') is None:
            params['object'] = params['object']
        else:
            params['object'] = {
              'charge': ChargeResponse,
              'customer': CustomerResponse,
              'shop': ShopResponse,
              'recursion': RecursionResponse,
              'account': AccountResponse,
            }[params['object']['object']](params['object'])
        self.__dict__ = params

class EventResponse(Entity):


    fields = ['id','object','livemode','created','data','pending_webhooks','type','shop']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['data'] = EventData(params['data']) if isinstance(params['data'], dict) else params['data']
        self.__dict__ = params

class EventListRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['count','offset','created','type','shop']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['created'] = CreatedRange(params['created']) if isinstance(params['created'], dict) else params['created']
        self.__dict__ = params


    # attributes setters

    @property
    def created(self):
        return self.__dict__['created']

    @created.setter
    def created(self, value):
        value = CreatedRange(value) if isinstance(value, dict) else value
        self.__dict__['created'] = value

class EventResponseList(Entity):


    fields = ['object','url','count','data']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['data'] = list(map(lambda x: EventResponse(x) if isinstance(x, dict) else x, params['data'])) if isinstance(params['data'], list) else params['data']
        self.__dict__ = params

class ShopRequestCreate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['description','details']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class ShopResponse(Entity):


    fields = ['id','object','livemode','status','description','access_key','created','statement_descriptor','card_types_supported','details']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params

class ShopIdRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, ShopResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class ShopRequestUpdate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, ShopResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id','description','details']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class ShopResponseList(Entity):


    fields = ['object','url','count','data']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['data'] = list(map(lambda x: ShopResponse(x) if isinstance(x, dict) else x, params['data'])) if isinstance(params['data'], list) else params['data']
        self.__dict__ = params

class RecursionRequestCreate(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['amount','currency','customer','period','description','shop','first_scheduled','uuid']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class RecursionIdRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, RecursionResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class RecursionRequestResume(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        elif isinstance(params, RecursionResponse):
            return cls({'id': params.id})
        elif isinstance(params, str) or isinstance(params, unicode):
            return cls({'id': params})
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['id','retry']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class RecursionListRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = ['count','offset','created','customer','shop','suspended']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['created'] = CreatedRange(params['created']) if isinstance(params['created'], dict) else params['created']
        self.__dict__ = params


    # attributes setters

    @property
    def created(self):
        return self.__dict__['created']

    @created.setter
    def created(self, value):
        value = CreatedRange(value) if isinstance(value, dict) else value
        self.__dict__['created'] = value

class RecursionResponseList(Entity):


    fields = ['object','url','count','data']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['data'] = list(map(lambda x: RecursionResponse(x) if isinstance(x, dict) else x, params['data'])) if isinstance(params['data'], list) else params['data']
        self.__dict__ = params

class EmptyRequest(Entity):


    @classmethod
    def create(cls, params):
        """Create an instance of cls from params"""
        if isinstance(params, cls):
            return params
        elif type(params) is dict:
            return cls(params)
        else:
            raise InvalidRequestError('%s does not accept the given value' % cls, params)

    fields = []

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params


    # attributes setters
class AccountResponse(Entity):


    fields = ['id','object','charge_enabled','currencies_supported','details_submitted','email','statement_descriptor','card_types_supported']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params

class DeletedResponse(Entity):


    fields = ['deleted']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params

class ErrorBody(Entity):


    fields = ['message','type','code','param']

    def __init__(self, params):
        params = normalize(self.fields, params)
        self.__dict__ = params

class ErrorData(Entity):


    fields = ['error']

    def __init__(self, params):
        params = normalize(self.fields, params)
        params['error'] = ErrorBody(params['error']) if isinstance(params['error'], dict) else params['error']
        self.__dict__ = params

