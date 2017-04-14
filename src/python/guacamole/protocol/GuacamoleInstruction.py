

class GuacamoleInstruction(object):
    def __init__(self, opcode, *instructions):
        self._opcode = opcode
        self._instructions = list(instructions)

    def __str__(self):
        return ','.join([str(len(self._opcode)) + '.' + self._opcode]
                      + [str(len(instruction)) + '.' + instruction for instruction in self._instructions]
                ) + ';'

    @property
    def opcode(self):
        return self._opcode

    @property
    def instructions(self):
        return self._instructions

