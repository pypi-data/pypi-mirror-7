import urlparse, urllib, urllib2, hashlib, base64, json as _json
from datetime import datetime
from . import dao, gateway, errors

class attrdict(dict):
	def __init__(self, *args, **kwargs):
		if len(args) > 1:
			raise TypeError("__init__ expected at most 1 arguments, got %d" % len(args))
		if args: self.update(args[0])
		if kwargs: self.update(**kwargs)

	def update(self, *args, **kwargs):
		if args:
			if len(args) > 1:
				raise TypeError("update expected at most 1 arguments, got %d" % len(args))
			other = dict(args[0])
			for key in other:
				self[key] = other[key]
		for key in kwargs:
			self[key] = kwargs[key]

	def __getattr__(self, name):
		try:
			return super(attrdict, self).__getattr__(name)
		except AttributeError:
			if self.has_key(name):
				return self[name]
			else:
				return None

def to_dotted_array(v, path):
	dictout = {}
	for i in range(0, len(v)):
		key = "%s.%s" % (path, i)

		if isinstance(v[i], dict):
			dictout.update(to_dotted(v[i], key))
		elif isinstance(v[i], (list, tuple)) and not isinstance(v[i], str):
			dictout.update(to_dotted_array(v[i], key))
		else:
			if v[i] is not None:
				dictout[key] = v[i]
	return dictout


def to_dotted(dictin, path=None):
	dictout = {}
	for k, v in dictin.iteritems():
		key = "%s.%s" % (path, k) if path else k
	
		if isinstance(v, dict):
			dictout.update(to_dotted(v, key))
		elif isinstance(v, (list, tuple)) and not isinstance(v, str):
			dictout.update(to_dotted_array(v, key))
		else:
			if v is not None:
				if isinstance(v, bool):
					dictout[key] = 'true' if v else 'false'
				else:
					dictout[key] = v
	return dictout
		
class Message(object):
	def __init__(self, **kwargs):
		self._kwargs = kwargs

	def _timestamp(self):
		return datetime.utcnow().strftime('%Y%m%d%H%M%S')

	def _encoded_list(self, in_list):
		out_list = []
		for v in in_list:
			if isinstance(v, dict):
				out_list.append(self._encoded_dict(v))
			elif isinstance(v, list):
				out_list.append(self._encoded_list(v))
			elif isinstance(v, unicode):
				out_list.append(str(v.encode('utf8')))
			else:
				out_list.append(v)
		return out_list

	def _encoded_dict(self, in_dict):
		out_dict = {}
		for k, v in in_dict.iteritems():
			if isinstance(v, dict):
				out_dict[k] = self._encoded_dict(v)
			elif isinstance(v, list):
				out_dict[k] = self._encoded_list(v)
			elif isinstance(v, unicode):
				out_dict[k] = str(v.encode('utf8'))
			else:
				out_dict[k] = v
		return out_dict

	def _to_dict(self, api_key=None, api_secret=None):
		dictin = {}
		for k, v in self._kwargs.iteritems():
			if isinstance(v, dao.DAO):
				dictin[k] = v._to_dict()
			else:
				if isinstance(v, dict):
					dictin[k] = self._encoded_dict(v)
				elif isinstance(v, list):
					dictin[k] = self._encoded_list(v)
				elif isinstance(v,unicode):
					dictin[k] = str(v.encode('utf8'))
				else :
					dictin[k] = v

		if api_key:
			dictin['api_key'] = api_key 

		if api_secret:
			dictin['ts'] = self._timestamp() 
			if dictin.has_key('sig'):
				del dictin['sig']
			qs = urllib.urlencode(sorted(to_dotted(dictin).iteritems())).replace('%2A', '*').replace('+', '%20')
			dictin['sig'] = base64.urlsafe_b64encode(hashlib.sha1("%s%s" % (api_secret, qs)).digest())

		return dictin

	
	def __getattr__(self, name):
		try:
			return super(Message, self).__getattr__(name)
		except AttributeError:
			if self._kwargs.has_key(name):
				return self._kwargs[name]
			else:
				return None

class Request(Message):
	def __init__(self, gateway, **kwargs):
		self._gateway = gateway
		super(Request, self).__init__(**kwargs)
	
	def send(self):
		qs = urllib.urlencode(sorted(to_dotted(self._to_dict()).iteritems()))
		if self.method == 'GET':
			request = urllib2.Request('%s?%s' % (self.endpoint, qs))
		else:
			request = urllib2.Request(self.endpoint, data=qs)
			request.add_header('Content-Type', 'application/x-www-form-urlencoded')
		request.get_method = lambda: self.method

		try:
			response = self._gateway.url_opener.open(request)
		except urllib2.HTTPError, e:
			print e
			response = e.read()			
		else:
			response = response.read()
		return Response(self._gateway, json=response)

	@property
	def form_data(self):
		form_data = to_dotted(self._to_dict(api_key=self._gateway.api_key, api_secret=self._gateway.api_secret))
		return urllib.urlencode(sorted(form_data.iteritems()))
	
	@property
	def endpoint(self):
		return '%s%s' % (self._gateway.environment.base_url, '%s')
	
	@property
	def method(self):
		return 'GET'
	

class Response(Message):
	def __init__(self, gateway, qs=None, json=None):
		self._gateway = gateway

		kwargs = {}
		sig = None

		if qs:
			for k, v in (dict((k, v[0]) for k, v in urlparse.parse_qs(qs).iteritems()) if isinstance(qs, basestring) else dict((k, v) for k, v in qs.iteritems())).iteritems():
				d = kwargs
				k = k.split('.')
				for i in range(0, len(k) - 1):
					d[k[i]] = d[k[i]] if d.has_key(k[i]) else attrdict() 
					d = d[k[i]]
				d[k[-1]] = v
		elif json:
			kwargs = _json.loads(json, object_hook=attrdict)

		super(Response, self).__init__(**kwargs)

		if self.error:
			raise errors.ApiException.create(self.error.type, self.error.get('message'), self.error.get('code'), self.error.get('body'))

		if self.sig is None or self.ts is None:
			raise errors.InvalidSignatureException()

		check = self._to_dict(api_secret=self._gateway.api_secret)
		if self.sig != check['sig']:
			raise errors.InvalidSignatureException()

	def _timestamp(self):
		return self._kwargs['ts']

	@property
	def form_data(self):
		form_data = to_dotted(self._to_dict(api_key=self._gateway.api_key, api_secret=self._gateway.api_secret))
		return urllib.urlencode(sorted(form_data.iteritems()))
gateway.Gateway.response = lambda gateway, qs=None, json=None: Response(gateway, qs=qs, json=json) 


class CardCreateRequest(Request):
	@property
	def endpoint(self):
		return super(CardCreateRequest, self).endpoint % '/card'
	
	@property
	def method(self):
		return 'POST'
gateway.Gateway.create_card = lambda gateway, **kwargs: CardCreateRequest(gateway, **kwargs)

class CardDeleteRequest(Request):
	def __init__(self, gateway, card=None, **kwargs):
		super(CardDeleteRequest, self).__init__(gateway, **kwargs)
		self.card = card

	@property
	def endpoint(self):
		return super(CardDeleteRequest, self).endpoint % ('/card/%s' % self.card.token,)

	@property
	def method(self):
		return 'DELETE'
gateway.Gateway.delete_card = lambda gateway, **kwargs: CardDeleteRequest(gateway, **kwargs)

class CardListRequest(Request):
	@property
	def endpoint(self):
		return super(CardListRequest, self).endpoint % '/card'
gateway.Gateway.list_cards = lambda gateway, **kwargs: CardListRequest(gateway, **kwargs)

class TransactionCreateRequest(Request):
	@property
	def endpoint(self):
		return super(TransactionCreateRequest, self).endpoint % '/transaction'

	@property
	def method(self):
		return 'POST'
gateway.Gateway.create_transaction = lambda gateway, **kwargs: TransactionCreateRequest(gateway, **kwargs)

class TransactionCommitRequest(Request):
	def __init__(self, gateway, transaction=None, **kwargs):
		super(TransactionCommitRequest, self).__init__(gateway, **kwargs)
		self.transaction = transaction

	@property
	def endpoint(self):
		return super(TransactionCommitRequest, self).endpoint % ('/transaction/%s' % self.transaction.id,)

	@property
	def method(self):
		return 'POST'
gateway.Gateway.commit_transaction = lambda gateway, **kwargs: TransactionCommitRequest(gateway, **kwargs)

class UserCreateRequest(Request):
	@property
	def endpoint(self):
		return super(UserCreateRequest, self).endpoint % '/user'

	@property
	def method(self):
		return 'POST'
gateway.Gateway.create_user = lambda gateway, **kwargs: UserCreateRequest(gateway, **kwargs)

class UserAuthenticateRequest(Request):
	@property
	def endpoint(self):
		return super(UserAuthenticateRequest, self).endpoint % '/user/authenticate'

	@property
	def method(self):
		return 'POST'
gateway.Gateway.authenticate_user = lambda gateway, **kwargs: UserAuthenticateRequest(gateway, **kwargs)

class UserUpdateRequest(Request):
	def __init__(self, gateway, user=None, **kwargs):
		self.id = user.id
		del user.id
		super(UserUpdateRequest, self).__init__(gateway, user=user, **kwargs)
		
	@property
	def endpoint(self):
		return super(UserUpdateRequest, self).endpoint % ('/user/%s' % self.id)

	@property
	def method(self):
		return 'POST'
gateway.Gateway.update_user = lambda gateway, **kwargs: UserUpdateRequest(gateway, **kwargs)

class UserDeleteRequest(Request):
	def __init__(self, gateway, user=None, **kwargs):
		self.id = user.id
		del user.id
		super(UserDeleteRequest, self).__init__(gateway, user=user, **kwargs)
		
	@property
	def endpoint(self):
		return super(UserDeleteRequest, self).endpoint % ('/user/%s' % self.id)

	@property
	def method(self):
		return 'DELETE'
gateway.Gateway.delete_user = lambda gateway, **kwargs: UserDeleteRequest(gateway, **kwargs)

class UserGetRequest(Request):
	def __init__(self, gateway, user=None, **kwargs):
		self.id = user.id
		del user.id
		super(UserGetRequest, self).__init__(gateway, user=user, **kwargs)

	@property
	def endpoint(self):
		return super(UserGetRequest, self).endpoint % ('/user/%s' % self.id)
gateway.Gateway.get_user = lambda gateway, **kwargs: UserGetRequest(gateway, **kwargs)

class ScheduleCreateRequest(Request):
	def __init__(self, gateway, **kwargs):
		super(ScheduleCreateRequest, self).__init__(gateway, **kwargs)

	@property
	def endpoint(self):
		return super(ScheduleCreateRequest, self).endpoint % '/schedule'

	@property
	def method(self):
		return 'POST'
gateway.Gateway.create_schedule = lambda gateway, **kwargs: ScheduleCreateRequest(gateway, **kwargs)

class ScheduleListRequest(Request):
	def __init__(self, gateway, **kwargs):
		super(ScheduleListRequest, self).__init__(gateway, **kwargs)

	@property
	def endpoint(self):
		return super(ScheduleListRequest, self).endpoint % '/schedule'
gateway.Gateway.list_schedules = lambda gateway, **kwargs: ScheduleListRequest(gateway, **kwargs)

class ScheduleGetRequest(Request):
	def __init__(self, gateway, schedule=None, **kwargs):
		self.id = schedule.id
		del schedule.id
		super(ScheduleGetRequest, self).__init__(gateway, schedule=schedule, **kwargs)

	@property
	def endpoint(self):
		return super(ScheduleGetRequest, self).endpoint % ('/schedule/%s' % self.id)
gateway.Gateway.get_schedule = lambda gateway, **kwargs: ScheduleGetRequest(gateway, **kwargs)

class ScheduleUpdateRequest(Request):
	def __init__(self, gateway, schedule=None, **kwargs):
		self.id = schedule.id
		del schedule.id
		super(ScheduleUpdateRequest, self).__init__(gateway, schedule=schedule, **kwargs)

	@property
	def endpoint(self):
		return super(ScheduleUpdateRequest, self).endpoint % ('/schedule/%s' % self.id)

	@property
	def method(self):
		return 'POST'
gateway.Gateway.update_schedule = lambda gateway, **kwargs: ScheduleUpdateRequest(gateway, **kwargs)

class ScheduleDeleteRequest(Request):
	def __init__(self, gateway, schedule=None, **kwargs):
		self.id = schedule.id
		del schedule.id
		super(ScheduleDeleteRequest, self).__init__(gateway, schedule=schedule, **kwargs)

	@property
	def endpoint(self):
		return super(ScheduleDeleteRequest, self).endpoint % ('/schedule/%s' % self.id)

	@property
	def method(self):
		return 'DELETE'
gateway.Gateway.delete_schedule = lambda gateway, **kwargs: ScheduleDeleteRequest(gateway, **kwargs)
