from rest_framework.throttling import UserRateThrottle

class AddressThrottle(UserRateThrottle):
    rate = '50/min'
