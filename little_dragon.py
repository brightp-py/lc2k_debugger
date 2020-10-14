import tkinter as tk
import tkinter.font as tkfont
from tkinter.filedialog import askopenfilename, asksaveasfilename

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

        self.label = {}
        for i, line in enumerate(text.split('\n')[:-1]):
            lab = line.split('\t')[0]
            if lab.isalpha():
                self.label[lab] = i
    
    def saveLines(self, text):

        for i, line in enumerate(text.split('\n')[:-1]):
            # print(line)
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
                
            # print(op)
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
                        # if a2 < 0:
                        #     a2 += (1 << 16)
                else:
                    a2 = int(a2)
                
                if a2 < 0:
                    a2 += (1 << 16)
            
            # print(op)
            total = (op << 23) + (a0 << 19) + (a1 << 16) + a2
            yield total
    
    def runState(self):
        
        line = self.getMem(self.pc)

        # print(line)
        op = (line & (7 << 23)) >> 23
        a0 = (line & (7 << 19)) >> 19
        a1 = (line & (7 << 16)) >> 16
        a2 = line & ((1 << 16) - 1)

        if a2 > (1 << 15):
            a2 -= (1 << 16)

        # print(self.pc, op, a0, a1, a2)
        
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
    
    def getState(self):

        toret = ""

        for i, r in enumerate(self.reg):
            toret += f"r{str(i)} | {str(r)}\n"
        
        toret += "\n-- MEM --\n"

        for i, m in enumerate(self.mem):
            toret += f"{str(i)} | {str(m)}\n"

        toret += "\n-- STACK --\n"

        for i, s in enumerate(self.stack):
            toret += f"{str(i)} | {str(m)}\n"
        
        return toret

class FileText:

    def __init__(self, text, startingLine):

        self.text = [l for l in text if l.split('\t')[1] != '.fill']
        self.data = [l for l in text if l.split('\t')[1] == '.fill']
        self.textStartingLine = startingLine
        self.dataStartingLine = 0
        self.textSize = len(self.text)
        self.dataSize = len(self.data)

    def process(self):

        self.getLabels()
    
    def getLabels(self):

        self.label = {}

        for i, line in enumerate(self.text):
            lab = line.split('\t')[0]
            if len(lab) > 0:
                self.label[lab] = i + self.textStartingLine
        
        for i, line in enumerate(self.data):
            lab = line.split('\t')[0]
            if len(lab) > 0:
                self.label[lab] = i + self.dataStartingLine
    
    def saveLines(self):

        self.Tlines = []

        for i, line in enumerate(self.text):
            lab, op = line.split('\t')[0:2]
            a0, a1, a2 = "", "", ""

            if op in ["add", "nor", "lw", "sw", "beq", "jalr"]:
                a0, a1 = line.split('\t')[2:4]
                if op != "jalr":
                    a2 = line.split('\t')[4]

            if len(lab) > 0 and lab[0].islower():
                lab = ""
            
            if op in ("lw", "sw"):
                if a2[0].islower():
                    a2 = self.label[a2]
            
            if op == "beq":
                if a2[0].islower():
                    a2 = self.label[a2] - (self.textStartingLine + i + 1)
            
            self.Tlines.append(f"{lab}\t{op}\t{a0}\t{a1}\t{str(a2)}")
        
        self.Dlines = []

        for line in self.data:
            
            lab = line.split('\t')[0]
            a2 = line.split('\t')[2]

            if len(lab) > 0 and lab[0].islower():
                lab = ""

            if a2[0].islower():
                a2 = self.label[a2]
            
            self.Dlines.append(f"{lab}\t.fill\t{str(a2)}")

class Interpreter:

    def __init__(self):

        self.sim = Simulator()

    def loadCode(self, text, folder):

        self.files = []
        self.breaks = []
        links = {"this": []}
        order = ["this"]

        for i, line in enumerate(text.split('\n')[:-1]):
            if line[0] == "#":
                if line == "#BREAK":
                    self.breaks.append(i)
                    continue
                code, arg = line.split(' ', 1)
                if code == "#LINK":
                    assert(arg[-3:] == ".as")
                    print(f"Linking {arg}")
                    links[arg] = self.readF(arg, folder).split('\n')[:-1]
                    order.append(arg)
                elif code == "#RUN":
                    assert(arg[-3:] == ".as")
                    print(f"Running {arg}")
                    links[arg] = self.readF(arg, folder).split('\n')[:-1]
                    order.insert(0, arg)
            else:
                links["this"].append(line)
        
        running = 0

        for o in order:
            self.files.append(FileText(links[o], running))
            running += self.files[-1].textSize
        
        for i in range(len(self.files)):
            self.files[i].dataStartingLine = running
            self.files[i].getLabels()
            self.files[i].saveLines()
            running += self.files[i].dataSize
        
        self.program = '\n'.join('\n'.join(f.Tlines) for f in self.files)
        data = '\n'.join('\n'.join(f.Dlines) for f in self.files)
        if len(data) > 0:
            self.program += '\n' + data
        self.program += '\nStack\t.fill\t0\n'

        print(self.program)
    
    def readF(self, file, folder):

        try:
            with open(file, 'r') as f:
                return f.read()
        except Exception:
            try:
                with open(folder + file, 'r') as f:
                    return f.read()
            except Exception as e:
                print(f"Unable to find {file}")
                raise(e)
    
    def run(self):

        self.sim.run(self.program)
    
    def getState(self):

        return self.sim.getState()

class Screen:

    def __init__(self):

        self.window = tk.Tk()
        self.window.title("Little Dragon - LC2K Debugger")

        self.FONT = tkfont.Font(self.window, ("Courier New", 12))

        self.IMAGES = {
            a: tk.PhotoImage(file = f"images/{a}.png") for a in [
                "playbutton",
                "openbutton",
                "linkbutton",
                "parentbutton",
                "skipbutton",
                "nextbutton",
                "stopbutton"
            ]
        }
        
        self.BCOLOR = "gray18"

        self.interpreter = Interpreter()

        self.filename = ""
        self.initdir = ""

        # top bar for control buttons
        self.window.rowconfigure(0, minsize = 50, weight = 0)
        # main row for content
        self.window.rowconfigure(1, minsize = 100, weight = 1)

        # left column for text editing
        self.window.columnconfigure(0, minsize = 200, weight = 2)
        # right column for debugging info
        self.window.columnconfigure(1, minsize = 100, weight = 1)

        self.buildFrames()
        self.buildTextFrame()
        self.buildButtonFrame()
        self.buildDebugFrame()
    
    def runText(self):

        # try:
            text = self.textEditor.get("1.0", tk.END)
            # self.sim.run(text)
            self.interpreter.loadCode(text, self.initdir)
            self.interpreter.run()
            self.printToDebugOut(self.interpreter.getState())
        
        # except Exception as e:
        #     print(str(e))
        #     self.printToDebugOut(str(e))
    
    def openFile(self):

        fname = askopenfilename(initialdir = self.initdir, title = "Select file",
                                filetypes = (("LC2K files",("*.as", "*.asd")),("all files","*.*")))
        
        with open(fname, 'r') as f:
            ntext = '\n'.join(f.read().split('\n')[:-1])
            self.textEditor.delete("1.0", tk.END)
            self.textEditor.insert("1.0", ntext)
        
        self.initdir = '/'.join(fname.split('/')[:-1]) + '/'

        self.window.title(fname)
    
    def linkFile(self):

        fname = askopenfilename(initialdir = self.initdir, title = "Link file",
                                filetypes = [("LC2K files",("*.as"))])
        
        self.textEditor.insert('1.0', f"#LINK {fname}\n")
    
    def addParent(self):

        fname = askopenfilename(initialdir = self.initdir, title = "Link parent",
                                filetypes = [("LC2K files",("*.as"))])
        
        self.textEditor.insert('1.0', f"#RUN {fname}\n")
    
    def createButton(self, imagename, func, frame, size = 50):

        return tk.Button(frame, image = self.IMAGES[imagename],
                         width = size, height = size, bg = self.BCOLOR,
                         relief = tk.FLAT, activebackground = "gray22",
                         command = func)
    
    def printToDebugOut(self, text):

        self.debugOut.config(state = tk.NORMAL)
        self.debugOut.delete("1.0", tk.END)
        self.debugOut.insert("1.0", text)
        self.debugOut.config(state = tk.DISABLED)

    def buildFrames(self):

        # top bar for control buttons
        self.bframe = tk.Frame(self.window, bg = self.BCOLOR)
        self.bframe.grid(row = 0, column = 0, rowspan = 2, columnspan = 2,
                         sticky = "nsew")
        self.bframe.rowconfigure(0, weight = 1)
        self.bframe.columnconfigure(0, weight = 0)
        self.bframe.columnconfigure(1, weight = 0)
        self.bframe.columnconfigure(2, weight = 0)
        self.bframe.columnconfigure(3, weight = 1)
        self.bframe.columnconfigure(4, weight = 0)

        # left side for text editing
        self.tframe = tk.Frame(self.window, bg = "gray10")
        self.tframe.grid(row = 1, column = 0, sticky = "nsew")
        self.tframe.rowconfigure(0, weight = 1)
        self.tframe.columnconfigure(0, weight = 1)
        self.tframe.columnconfigure(1, weight = 0)

        # right side for debugging info
        self.dframe = tk.Frame(self.window, bg = "gray14")
        self.dframe.grid(row = 1, column = 1, sticky = "nsew")
        self.dframe.rowconfigure(0, weight = 0)
        self.dframe.rowconfigure(1, weight = 1)
        self.dframe.columnconfigure(0, weight = 1)
    
    def buildButtonFrame(self):

        self.buttons = {}

        self.buttons["play"] = self.createButton("playbutton", self.runText, self.bframe)
        self.buttons["play"].grid(row = 0, column = 4, sticky = "ne")

        self.buttons["open"] = self.createButton("openbutton", self.openFile, self.bframe)
        self.buttons["open"].grid(row = 0, column = 0, sticky = "nw")

        self.buttons["link"] = self.createButton("linkbutton", self.linkFile, self.bframe)
        self.buttons["link"].grid(row = 0, column = 1, sticky = "nw")

        self.buttons["parent"] = self.createButton("parentbutton", self.addParent, self.bframe)
        self.buttons["parent"].grid(row = 0, column = 2, sticky = "nw")
    
    def buildTextFrame(self):
        
        self.tframe.grid_propagate(False)

        self.textEditor = tk.Text(self.tframe, bg = "gray10", font = self.FONT,
                                  fg = "white", relief = tk.RIDGE,
                                  insertbackground = "white", wrap = tk.NONE)
        self.textEditor.grid(row = 0, column = 0, sticky = "nsew")
    
    def buildDebugFrame(self):

        self.oframe = tk.Frame(self.dframe, bg = "gray14")
        self.oframe.grid(row = 1, column = 0, sticky = "nsew")
        self.oframe.rowconfigure(0, weight = 1)
        self.oframe.columnconfigure(0, weight = 1)

        self.oframe.grid_propagate(False)

        self.debugOut = tk.Text(self.oframe, bg = "gray14", font = self.FONT,
                                fg = "white", relief = tk.FLAT, state = tk.NORMAL,
                                insertbackground = "white")
        self.debugOut.grid(row = 0, column = 0, sticky = "nsew")

        self.debugOut.insert("1.0", "[Debug information]\n")
        self.debugOut.config(state = tk.DISABLED)

        self.dbframe = tk.Frame(self.dframe, bg = self.BCOLOR)
        self.dbframe.grid(row = 0, column = 0, sticky = "nsew")

        self.dbframe.columnconfigure(0, weight = 0)
        self.dbframe.columnconfigure(1, weight = 1)
        self.dbframe.columnconfigure(2, weight = 0)
        self.dbframe.columnconfigure(3, weight = 0)

        self.buttons["stop"] = self.createButton("stopbutton", lambda: 0, self.dbframe)
        self.buttons["stop"].grid(row = 0, column = 0, sticky = "ne")

        self.buttons["skip"] = self.createButton("skipbutton", lambda: 0, self.dbframe)
        self.buttons["skip"].grid(row = 0, column = 2, sticky = "nw")

        self.buttons["next"] = self.createButton("nextbutton", lambda: 0, self.dbframe)
        self.buttons["next"].grid(row = 0, column = 3, sticky = "nw")
    
    def getNumLines(self):

        return int(self.textEditor.index('end-1c').split('.')[0])

    def run(self):
        
        self.window.mainloop()

if __name__ == "__main__":
    Screen().run()