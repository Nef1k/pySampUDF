import logging

from .gta import GtaInstance, Pointer


class SampAPI:
    def __init__(self, gta_instance: GtaInstance):
        self.gta = gta_instance
        self.samp_pointer = None

    def get_samp_username(self) -> str:
        return self.gta.read_string(self.gta.samp_address + self.OFFSET_SAMP_USERNAME)

    def get_server_ip(self) -> str:
        return self.gta.read_string(self.gta.samp_address + self.OFFSET_SAMP_IP)

    def get_server_port(self) -> int:
        port_str = self.gta.read_string(self.gta.samp_address + self.OFFSET_SAMP_PORT)
        return int(port_str)

    def get_server_name(self) -> str:
        addr = self.gta.read_int32(self.gta.samp_address + self.OFFSET_SAMP_INFO)
        server_name = self.gta.read_string(addr + self.OFFSET_SAMP_SERVER_NAME, 100)
        return server_name

    def get_lplayer_coordinates(self):
        x = self.gta.read_float(self.ADDR_POS_X)
        y = self.gta.read_float(self.ADDR_POS_Y)
        z = self.gta.read_float(self.ADDR_POS_Z)
        return x, y, z

    def get_lplayer_money(self) -> int:
        return self.gta.read_int32(self.ADDR_CPED_MONEY)

    def get_lplayer_health(self) -> int:
        ped_ptr = self.gta.read_dword(self.ADDR_CPED_PTR)
        health = self.gta.read_float(ped_ptr + self.OFFSET_CPED_HP)
        return round(health)

    def get_lplayer_armor(self) -> float:
        ped_ptr = self.gta.read_dword(self.ADDR_CPED_PTR)
        armor = self.gta.read_float(ped_ptr + self.OFFSET_CPED_ARMOR)
        return armor

    def add_message(self, message: str):
        if not message:
            return

        func_addr = self.gta.samp_address + self.FUNC_SAMP_ADD_MESSAGE
        chat_info = self.gta.read_dword(self.gta.samp_address + self.ADDR_SAMP_CHATMSG_PTR)

        self.gta.call_with_params(func_addr, [
            Pointer(chat_info), str(message)
        ])

    def send_message(self, message: str):
        if not message:
            return

        func = self.FUNC_SAMP_SEND_MESSAGE
        if message[0] == '/':
            func = self.FUNC_SAMP_SEND_COMMAND
            message = message[1:]
            self.add_message(f'Команда: {message}')
        func += self.gta.samp_address

        self.gta.call_with_params(func, [
            message
        ], cleanup_stack=False)

        logging.debug(f'Sent message: {message}')

    def show_game_text(self, text: str, t: int, text_style: int):
        self.gta.call_with_params(self.gta.samp_address + self.FUNC_SAMP_SHOW_GAME_TEXT, [
            str(text), int(t), int(text_style),
        ], cleanup_stack=False)

    ADDR_POS_X = 0xB6_F2E4
    ADDR_POS_Y = 0xB6_F2E8
    ADDR_POS_Z = 0xB6_F2EC

    ADDR_CPED_PTR = 0xB6F5F0
    ADDR_CPED_MONEY = 0xB7CE54
    OFFSET_CPED_HP = 0x540
    OFFSET_CPED_ARMOR = 0x548
    OFFSET_CPED_SKIN_ID = 0x22

    OFFSET_SAMP_INFO = 0x2ACA24
    OFFSET_SAMP_SERVER_NAME = 0x131
    OFFSET_SAMP_USERNAME = 0x2AC187
    OFFSET_SAMP_PORT = 0x2AC086
    OFFSET_SAMP_IP = 0x2ABF85

    ADDR_SAMP_CHATMSG_PTR = 0x2ACA10

    FUNC_SAMP_SHOW_GAME_TEXT = 0xA0B20
    FUNC_SAMP_ADD_MESSAGE = 0x67B60
    FUNC_SAMP_SEND_COMMAND = 0x69340
    FUNC_SAMP_SEND_MESSAGE = 0x5860

    LENGTH_SAMP_USERNAME = 25
