"""Controller implementation for an OpenXC USB device."""
from __future__ import absolute_import

import json
import logging
import usb.core

from .base import Controller, ControllerError

LOG = logging.getLogger(__name__)


class UsbControllerMixin(Controller):
    """An implementation of a Controller type that connects to an OpenXC USB
    device.

    This class acts as a mixin, and expects ``self.device`` to be an instance
    of ``usb.Device``.

    TODO bah, this is kind of weird. refactor the relationship between
    sources/controllers.
    """
    VERSION_CONTROL_COMMAND = 0x80
    DEVICE_ID_CONTROL_COMMAND = 0x82
    COMPLEX_CONTROL_COMMAND = 0x83

    def write_bytes(self, data):
        if self.out_endpoint is None:
            LOG.warn("Can't write \"%s\" to USB, OUT endpoint is %x", data,
                    self.out_endpoint)
            return 0
        else:
            # See upstream issue in pyusb on why we have to manually encode
            # here: https://github.com/walac/pyusb/issues/8
            return self.out_endpoint.write(data.encode("utf8"))

    def version(self):
        """Request the firmware version identifier from the VI via USB control
        request.
        """
        # TODO is 0xC0 correct for IN control transfers? if I clear the in
        # endpoint on the VI it dies, but if I clear the OUT, it works.
        raw_version = self.device.ctrl_transfer(0xC0,
                self.VERSION_CONTROL_COMMAND, 0, 0, 100)
        return ''.join([chr(x) for x in raw_version])

    def device_id(self):
        """Request the unique device ID of the attached VI with a USB control
        request.
        """
        raw_device_id = self.device.ctrl_transfer(0xC0,
                self.DEVICE_ID_CONTROL_COMMAND, 0, 0, 20)
        return ''.join([chr(x) for x in raw_device_id])

    def diagnostic_request(self, message_id, mode, bus=None, pid=None,
            frequency=None, payload=None, wait_for_first_response=False):
        """Send a new diagnostic request to the VI with a USB control request.
        """
        request = self._build_diagnostic_request(message_id, mode, bus, pid,
                frequency, payload)
        self.device.ctrl_transfer(0x40, self.COMPLEX_CONTROL_COMMAND, 0, 0,
                json.dumps(request))
        result = None
        if wait_for_first_response:
            result = self._wait_for_response(request)
        return result

    @property
    def out_endpoint(self):
        """Open a reference to the USB device's only OUT endpoint. This method
        assumes that the USB device configuration has already been set.
        """
        if getattr(self, '_out_endpoint', None) is None:
            config = self.device.get_active_configuration()
            interface_number = config[(0, 0)].bInterfaceNumber
            interface = usb.util.find_descriptor(config,
                    bInterfaceNumber=interface_number)

            self._out_endpoint = usb.util.find_descriptor(interface,
                    custom_match = \
                            lambda e: \
                            usb.util.endpoint_direction(e.bEndpointAddress) == \
                            usb.util.ENDPOINT_OUT)

            if not self._out_endpoint:
                raise ControllerError(
                        "Couldn't find OUT endpoint on the USB device")
        return self._out_endpoint
