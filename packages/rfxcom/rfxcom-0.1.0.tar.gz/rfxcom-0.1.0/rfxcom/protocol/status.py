from rfxcom.protocol.base import BasePacketHandler


def int_to_binary_list(int_):
    return list('{0:08b}'.format(int_))

MSG3_PROTOCOLS = [
    'EDisplay ofundecoded',
    'RFU6',
    'Byron SX',
    'RSL',
    'Lighting4',
    'FineOffset/Viking',
    'Rubicson',
    'AE Blyss',
]

MSG4_PROTOCOLS = [
    'BlindsT1/T2/T3/T4',
    'BlindsT0',
    'ProGuard',
    'FS20',
    'La Crosse',
    'Hideki/UPM',
    'AD LightwaveRF',
    'Mertik',
]

MSG5_PROTOCOLS = [
    'Visonic',
    'ATI',
    'Oregon Scientific',
    'Meiantech',
    'HomeEasy EU',
    'AC',
    'ARC',
    'X10',
]

PROTOCOLS = MSG3_PROTOCOLS + MSG4_PROTOCOLS + MSG5_PROTOCOLS


class Status(BasePacketHandler):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.PACKET_TYPES = {
            0x01: "Interface message"
        }

        self.SUB_TYPES = {
            0x00: "Response on a mode command",
            0xFF: "Wrong command recieved from the application.",
        }

    def log_enabled_protocols(self, flags, protocols):

        enabled, disabled = [], []

        for procol, flag in sorted(zip(protocols, flags)):

            if flag == '1':
                enabled.append(procol)
                status = 'Enabled'
            else:
                disabled.append(procol)
                status = 'Disabled'

            message = "{0:21}: {1}".format(procol, status)
            self.log.info(message)

        return enabled, disabled

    def parse(self, data):
        """Parse a 18 byte packet in the Status format.
        """

        self.validate_packet(data)

        packet_length = data[0]
        packet_type = data[1]
        sub_type = data[2]
        sequence_number = data[3]
        command_type = data[4]
        transceiver_type = data[5]
        firmware_version = data[6]

        flags = int_to_binary_list(data[7])
        flags.extend(int_to_binary_list(data[8]))
        flags.extend(int_to_binary_list(data[9]))

        enabled, disabled = self.log_enabled_protocols(flags, PROTOCOLS)

        return {
            'packet_length': packet_length,
            'packet_type': packet_type,
            'sequence_number': sequence_number,
            'sub_type': sub_type,
            'sub_type_name': self.SUB_TYPES.get(sub_type),
            'command_type': command_type,
            'transceiver_type': transceiver_type,
            'firmware_version': firmware_version,
            'enabled_protocols': enabled,
            'disabled_protocols': disabled,
        }
