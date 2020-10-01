import tkinter as tk
import tkinter.font as tfont

OPCODES = {
    "add":   0,
    "nor":   1,
    "lw":    2,
    "sw":    3,
    "beq":   4,
    "jalr":  5,
    "halt":  6,
    "noop":  7,
    ".fill": 0
}

class Simulator:

    def __init__(self):

        self.label = {}

        self.reg = [0, 0, 0, 0, 0, 0, 0, 0]
        self.mem = []
        self.stack = []
        self.pc = 0
    
    def getMem(self, address):

        if address < len(self.mem):
            return self.mem[address]
        
        address -= len(self.mem)
        
        if address < len(self.stack):
            return self.stack[address]
        
        return 0
    
    def setMem(self, address, value):

        if address < len(self.mem):
            self.mem[address] = value
        
        address -= len(self.mem)

        if address < len(self.stack):
            self.stack[address] = value
        
        while address > len(self.stack):
            self.stack.append(0)
        
        self.stack.append(value)
    
    def getLabels(self, text):

        for i, line in enumerate(text.split('\n')[:-1]):
            lab = line.split('\t')[0]
            if lab.isalpha():
                self.label[lab] = i
        self.label["Stack"] = i + 1
    
    def saveLines(self, text):

        for i, line in enumerate(text.split('\n')[:-1]):
            print(line)
            op = line.split('\t')[1]
            a0, a1, a2 = 0, 0, 0

            if op == ".fill":
                a2 = line.split('\t')[2]
                if a2.isalpha():
                    a2 = self.label[a2]
                else:
                    a2 = int(a2)
                yield a2
                continue

            op = OPCODES[op]

            if op < 6:
                a0, a1 = line.split('\t')[2:4]
                a0 = int(a0)
                a1 = int(a1)
            
            if op < 5:
                a2 = line.split('\t')[4]
                if a2.isalpha():
                    a2 = self.label[a2]
                    if op == OPCODES["beq"]:
                        a2 -= (i + 1)
                else:
                    a2 = int(a2)
            
            total = (op << 23) + (a0 << 19) + (a1 << 16) + a2
            yield total
    
    def runState(self):

        line = self.getMem(self.pc)
        op = (line & (7 << 23)) >> 23
        a0 = (line & (7 << 19)) >> 19
        a1 = (line & (7 << 16)) >> 16
        a2 = line & ((1 << 16) - 1)

        print(self.pc, op, a0, a1, a2)
        
        if op == 0:
            self.reg[a2] = self.reg[a0] + self.reg[a1]
        
        elif op == 1:
            self.reg[a2] = not (self.reg[a0] or self.reg[a1])
        
        elif op == 2:
            address = self.reg[a0] + a2
            self.reg[a1] = self.getMem(address)
        
        elif op == 3:
            address = self.reg[a0] + a2
            self.setMem(address, self.reg[a1])
        
        elif op == 4:
            if self.reg[a0] == self.reg[a1]:
                self.pc += a2
        
        elif op == 5:
            self.reg[a1] = self.pc + 1
            self.pc = self.reg[a0] - 1
        
        elif op == 6:
            self.halted = True

        self.pc += 1
    
    def resetState(self, reg = [0,0,0,0,0,0,0,0]):

        self.reg = reg
        self.pc = 0
        self.halted = False
    
    def loadCode(self, text):

        self.getLabels(text)
        self.mem = list(self.saveLines(text))

    def run(self, text, reg = [0,0,0,0,0,0,0,0]):

        self.loadCode(text)
        self.resetState(reg)
        while not self.halted:
            self.runState()

if __name__ == "__main__":
    with open("test.as", 'r') as f:
        sim = Simulator()
        sim.run(f.read())