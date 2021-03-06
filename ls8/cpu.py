"""CPU functionality."""

import sys

# All instructions will be class constants, to keep conditionals readable
# Instructions
HLT =  0b00000001
LDI =  0b10000010
PRN =  0b01000111
NOP =  0b00000000
PUSH = 0b01000101
POP =  0b01000110
CALL = 0b01010000
RET =  0b00010001
JMP =  0b01010100
JEQ =  0b01010101
JNE =  0b01010110

# Arithemtic
MUL =  0b10100010
ADD =  0b10100000
CMP =  0b10100111

# Flags
EQUAL = 0b00000001
LESSTHAN = 0b00000100
GREATERTHAN = 0b00000010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.registers = [0] * 8
        self.registers[7] = 0xF4
        self.int_registers = [0] * 5
        self.ram = [0b00000000] * 256

        self.dispatch = {}
        self.dispatch[NOP] = self.nop
        self.dispatch[LDI] = self.ldi
        self.dispatch[PRN] = self.prn
        self.dispatch[MUL] = self.alu
        self.dispatch[ADD] = self.alu
        self.dispatch[PUSH] = self.push
        self.dispatch[POP] = self.pop
        self.dispatch[CALL] = self.call
        self.dispatch[RET] = self.ret
        self.dispatch[ADD] = self.alu
        self.dispatch[CMP] = self.alu
        self.dispatch[JMP] = self.jmp
        self.dispatch[JEQ] = self.jeq
        self.dispatch[JNE] = self.jne

###############################################################################
########################## Register Properties ################################

########################## Internal ###########################################
    @property
    def pc(self):
        '''Returns the Program Counter, address of currently executing
        instruction'''
        return self.int_registers[0]

    @pc.setter
    def pc(self, value):
        self.int_registers[0] = value

    @property
    def ir(self):
        '''Instruction Register, contains copy of currently executing 
        instruction'''
        return self.int_registers[1]

    @ir.setter
    def ir(self, value):
        self.int_registers[1] = value

    @property
    def mar(self):
        '''Memory Address Register, holds the memory address being read or 
        written to.'''
        return self.int_registers[2]

    @mar.setter
    def mar(self, value):
        self.int_registers[2]

    @property
    def mdr(self):
        '''Memory Data Register, holds the value to write or the value read'''
        return self.int_registers[3]

    @mdr.setter
    def mdr(self, value):
        self.int_registers[3]

    @property
    def fl(self):
        '''Flags register for storing less than greather than or equal flags'''
        return self.int_registers[4]

    @fl.setter
    def fl(self, value):
        self.int_registers[4] = value

################## User-accessible registers ##################################

    @property
    def sp(self):
        return self.registers[7]

    @sp.setter
    def sp(self, value):
        self.registers[7] = value

###############################################################################
############################## Instructions ###################################

    def ldi(self, op, op_a, op_b):
        '''
        Set the register at addres op_a to an integer value (op_b)
        op not used, for consistent usage accross instructions and alu
        '''
        self.registers[op_a] = op_b
        self.pc += 3

    def prn(self, op, op_a, op_b):
        '''
        Print register - Prints value stored at register a. Register b is not
        used, and keeping with usage convention
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        print(self.registers[op_a])
        self.pc += 2

    def nop(self, op, op_a, op_b):
        '''
        No Operation
        '''
        self.pc += 1

    def push(self, op, op_a, op_b):
        '''
        Push value stored in at register address in op_a to the stack
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        self.sp -= 1
        self.ram_write(self.registers[op_a], self.sp)
        self.pc += 2

    def pop(self, op, op_a, op_b):
        '''
        Pops the value at the top of the stack into register address op_a
        '''
        self.registers[op_a] = self.ram_read(self.sp)
        self.sp += 1
        self.pc += 2

    def call(self, op, op_a, op_b):
        '''
        Calls a subroutine at the address stored in the register op_a
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        # push next instruction in memory to the stack
        # self.pc + 2, because address + 1 is used for op_a (register address)
        self.sp -= 1
        self.ram_write(self.pc + 2, self.sp)
        self.pc = self.registers[op_a]

    def ret(self, op, op_a, op_b):
        '''
        Returns from subroutine
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        # I don't know what registers have important values, so I need to
        # manually pop in here instead of calling pop
        self.pc = self.ram_read(self.sp)
        self.sp += 1

    def jmp(self, op, op_a, op_b):
        '''
        Jump to the address stored in the register at address op_a
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        self.pc = self.registers[op_a]

    def jeq(self, op, op_a, op_b):
        '''
        If the equal flag is set, jump to the address stored in the register at
        address op_a
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        if self.fl == EQUAL:
            self.pc = self.registers[op_a]
        else:
            self.pc += 2

    def jne(self, op, op_a, op_b):
        '''
        If the equal flag is clear, jump to the address stored in the register
        at address op_a
        op and op_b not used, for consistent usage accross instructions and alu
        '''
        if self.fl != EQUAL:
            self.pc = self.registers[op_a]
        else:
            self.pc += 2



###############################################################################
####################### Arithmetic Logic Unit #################################

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.registers[reg_a] += self.registers[reg_b]
            self.pc += 3
        elif op == MUL:
            self.registers[reg_a] *= self.registers[reg_b]
            self.pc += 3
        elif op == CMP:
            if self.registers[reg_a] == self.registers[reg_b]:
                self.fl = EQUAL
            elif self.registers[reg_a] < self.registers[reg_b]:
                self.fl = LESSTHAN
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.fl = GREATERTHAN
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

###############################################################################

    def ram_read(self, mar):
        '''
        Returns the value stored at the Memory Addres Register (mar)
        Spec specifies that mdr and mar are explicitely passed in as variables
        '''
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        '''
        Writes the value stored in the Memory Data Register (mdr) to the 
        location specified by the Memory Address Register(mar). Spec specifies
        that mdr and mar are explicitely passed in as variables.
        '''
        self.ram[mar] = mdr

    def load(self, program):
        """Load a program into memory."""

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ir,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            self.ir = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if self.ir == HLT:
                running = False #Not necessary, keeping with convetion
                break

            #print(self.ir)
            self.dispatch[self.ir](self.ir, operand_a, operand_b)
