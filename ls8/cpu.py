"""CPU functionality."""

import sys


### OP-Codes ###
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011

PUSH = 0b01000101
POP = 0b01000110

CALL = 0b01010000
RET = 0b00010001

CMP = 0b10100111

JEQ = 0b01010101
JMP = 0b01010100
JNE = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 bytes of memory
        self.reg = [0] * 8 # 8 general purpose registers
        self.PC = 0 # Program Counter - index current instructio
        self.IR = None # Instruction Register - copy of current instruction
        self.MAR = 0 # Memory Address Register - holds memory address being read/written
        self.MDR = None # Memory Data Register - holds value being read/written
        self.FL = 0b00000000 # Flag Register - holds flag status

        self.reg[7] = 0xF4 # Init stack pointer to address 0xF4

        
        self.running = True

        self.branchtable = {} # init branch table
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[PRN] = self.handle_PRN

        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[POP] = self.handle_POP

        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[RET] = self.handle_RET

        self.branchtable[CMP] = self.handle_CMP

        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE


    def load(self):
        """Load a program into memory."""
        
        if len(sys.argv) != 2:
            print("Usage: cpu.py filename")
            sys.exit()

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    split_line = line.split('#') # split array
                    string = split_line[0]

                    if string == '':
                        continue

                    if string[0] == '1' or string[0] == '0':
                        instruction = string[:8]
                        self.ram[self.MAR] = int(instruction, 2)
                        self.MAR += 1

        except FileNotFoundError:
                print(f'{sys.argv[1]} not found')
                sys.exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == DIV:
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == CMP:
            # Reset
            self.fl = 0b00000000
            # if reg a = reg b 
            if self.reg[reg_a] == self.reg[reg_b]:
                # set E flag to 1 or 0
                self.fl = self.fl | 0b00000001

            # if reg a >  reg b 
            if self.reg[reg_a] == self.reg[reg_b]:
                # set G flag to 1 or 0
                self.fl = self.fl | 0b00000010

            # if reg a <  reg b 
            if self.reg[reg_a] == self.reg[reg_b]:
                # set F flag to 1 or 0
                self.fl = self.fl | 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        self.MAR = address
        self.MDR = self.ram[self.MAR]

        return self.MDR

    def ram_write(self, address, value):
        self.MAR = address
        self.MDR = value

        self.ram[self.MAR] = self.MDR

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to CALL this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.FL,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def handle_HLT(self):
        self.running = False
        sys.exit()

    def handle_LDI(self):
        register = self.ram_read(self.PC + 1)
        value = self.ram_read(self.PC + 2)

        self.reg[register] = value

    def handle_PRN(self):
        register = self.ram_read(self.PC + 1)
        print(self.reg[register])

    def handle_POP(self):
        value = self.ram_read(self.reg[7])
        register = self.ram_read(self.PC + 1)
        self.reg[register] = value

        self.reg[7] += 1

    def handle_PUSH(self):
        self.reg[7] -= 1
        register = self.ram_read(self.PC + 1)
        value = self.reg[register]

        self.ram_write(self.reg[7], value)

    def handle_CALL(self):
        return_address = self.PC + 2
        self.reg[7] -= 1
        self.ram_write(self.reg[7], return_address)
        reg_value = self.ram_read(self.PC + 1)
        address = self.reg[reg_value]

        self.PC = address

    def handle_RET(self):
        address = self.ram_read(self.reg[7])
        self.reg[7] += 1

        self.PC = address

    # def handle_CMP(self):
    #     pass
    
    def handle_JEQ(self):
        pass

    def handle_JMP(self):
        pass

    def handle_JNE(self):
        pass

    def run(self):
        """Run the CPU."""
        while self.running:
            instruction = self.ram_read(self.PC)
            self.IR = instruction

            operands = instruction >> 6

            operand_a = self.ram_read(self.PC + 1)
            operand_b = self.ram_read(self.PC + 2)

            alu_op = (instruction >> 5) & 0b1

            if alu_op:
                self.alu(self.IR, operand_a, operand_b)
            else:
                self.branchtable[self.IR]()

            PC_op = (instruction >> 4) & 0b0001

            if not PC_op:
                self.PC += operands + 1
        
        sys.exit()