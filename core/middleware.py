from django.utils.deprecation import MiddlewareMixin

from apps.users.models.device import Device


class DeviceLanguageMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token = request.headers.get('Token')
        device = None

        if token:
            try:
                device = Device.objects.filter(device_token=token).first()
            except Exception:
                device = None

        if device:
            lang = device.language.lower()
        else:
            lang = 'uz'

        request.device = device
        request.lang = lang
        print(request.device)