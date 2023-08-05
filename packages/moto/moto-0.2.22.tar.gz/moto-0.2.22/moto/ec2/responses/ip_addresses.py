from moto.core.responses import BaseResponse


class IPAddresses(BaseResponse):
    def assign_private_ip_addresses(self):
        raise NotImplementedError('IPAddresses.assign_private_ip_addresses is not yet implemented')

    def unassign_private_ip_addresses(self):
        raise NotImplementedError('IPAddresses.unassign_private_ip_addresses is not yet implemented')
