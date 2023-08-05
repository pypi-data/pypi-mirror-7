Version 0.1b

FloraConcierge is worldwide flowers delivery service. We provide api services for
building your own flowers delivery e-commerce and submit users orders into our system.

All information at http://www.floraexpress.ru/

You can simple install floraconcierge api client into your django environment by adding middleware
`floraconcierge.middleware.ApiClientMiddleware` to your `MIDDLEWARE_CLASSES`.

Also you can add `floraconcierge.middleware.ApiObjectNotFound404` to your middlewares for automatic 404 pages when
api result raises ResultObjectNotFoundError.

Available settings
------------------

All settings used in middleware only, if you want manual initiation of api client object, you can do it yourself.

* `FLORACONCIERGE_API_ID` Required. Your application ID.

* `FLORACONCIERGE_API_SECRET` Required. Your application secret.

* `FLORACONCIERGE_API_INIT_ENV` Optional. You can setup custom init function for env setup. Function takes params
`client, request, restored` where client is ApiClient instance, request is django request object and restored is flag
variable indicating client env was restored from request session.

* `FLORACONCIERGE_API_INIT_CLIENT` Optional. Custom api client initiation function. By default middleware initiate
client with function `floraconcierge.middleware.initialize_apiclient`. You can se your own function. Function take
only one param `request`.

