import wx
import itertools


class Sudoku:
    def __init__(self, data=None):
        self.data = data or [[0] * 9 for _ in range(9)]

    def GetRow(self, id):
        return self.data[id][:]

    def GetColumn(self, id):
        return [row[id] for row in self.data]

    def GetBlockRC(self, row, col):
        row2 = row // 3 * 3
        col2 = col // 3 * 3
        return itertools.product(range(row2, row2 + 3), range(col2, col2 + 3))

    def GetBlock(self, row, col):
        return [self.data[row][col] for row, col in self.GetBlockRC(row // 3 * 3, col // 3 * 3)]

    def GetPossibles(self, row, col):
        if not self.data[row][col]:
            nums = self.GetRow(row) + self.GetColumn(col) + self.GetBlock(row, col)
            return [num for num in range(1, 10) if num not in nums]
        else:
            return []

    def SetCell(self, row, col, num):
        self.data[row][col] = num
        return True

    def SolveOne(self):
        for row, col in itertools.product(range(9), repeat=2):
            if self.data[row][col]:
                continue
            possibles = self.GetPossibles(row, col)
            if len(possibles) == 1:
                return self.SetCell(row, col, possibles[0])
            else:
                for num in possibles:
                    if (
                        sum(num in self.GetPossibles(row2, col) for row2 in range(9)) == 1 or
                        sum(num in self.GetPossibles(row, col2) for col2 in range(9)) == 1 or
                        sum(num in self.GetPossibles(row2, col2) for row2, col2 in self.GetBlockRC(row, col)) == 1
                    ):
                        return self.SetCell(row, col, num)

    def Solve(self):
        while self.SolveOne():
            pass


COLOUR_GRAY  = '#E0E0E0'
COLOUR_BLACK = '#000000'
COLOUR_GREEN = '#D0F0D0'


class Border(wx.Panel):
    def __init__(self, parent, width):
        wx.Panel.__init__(self, parent)
        box = wx.BoxSizer()
        box.Add((width, width), 1, wx.EXPAND)
        self.SetSizer(box)
        self.SetBackgroundColour(COLOUR_BLACK)
        self.Disable()


class NumPad(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = parent.sudoku
        self.numbox = None

        self.number = 0

        gbs = wx.GridBagSizer(vgap=5, hgap=5)
        for row, col in itertools.product(range(3), repeat=2):
            num = (2 - row) * 3 + col + 1
            btn = wx.ToggleButton(self, 100 + num, str(num), size=(30, 30))
            btn.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton)
            gbs.Add(btn, (row, col), flag=wx.EXPAND)
        parent.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        box = wx.BoxSizer()
        box.Add(gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

    def GetItem(self, num):
        return wx.FindWindowById(100 + num, self)

    def ToggleButton(self, num):
        if num == 0:
            self.SetSelection(0)
        elif self.GetItem(num).IsEnabled():
            self.SetSelection(0 if self.GetItem(num).GetValue() else num)

    def OnButton(self, evt):
        btn = evt.GetEventObject()
        btn.SetValue(not btn.GetValue())
        self.ToggleButton(evt.GetId() - 100)

    def OnKeyPress(self, evt):
        key = evt.GetKeyCode()
        if wx.WXK_NUMPAD0 <= key <= wx.WXK_NUMPAD9:
            self.ToggleButton(key - wx.WXK_NUMPAD0)
        elif ord('0') <= key <= ord('9'):
            self.ToggleButton(key - ord('0'))
        evt.Skip()

    def SetSelection(self, num=None):
        num = self.number = self.number if num is None else num
        for num2 in range(1, 10):
            self.GetItem(num2).SetValue(num == num2)
        self.numbox.OnSetNum(num)

    def SetEnables(self, nums):
        for num2 in range(1, 10):
            self.GetItem(num2).Enable(num2 in nums)


class NumBox(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = parent.sudoku
        self.numpad = None

        self.prev = None

        gbs = wx.GridBagSizer()
        id = 200
        skip = range(0, 13, 4)
        for row, col in itertools.product(range(13), repeat=2):
            if row in skip or col in skip:
                item = Border(self, 3)
            else:
                item = wx.ToggleButton(self, id, size=(30, 30))
                item.SetBackgroundColour(COLOUR_GRAY)
                item.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton)
                id += 1
            gbs.Add(item, (row, col), flag=wx.EXPAND)

        box = wx.BoxSizer()
        box.Add(gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

    def GetItem(self, row, col):
        return wx.FindWindowById(200 + 9 * row + col, self)

    def GetItems(self):
        for i in range(81):
            yield wx.FindWindowById(200 + i, self)

    def OnButton(self, evt):
        if self.prev:
            item = wx.FindWindowById(self.prev, self)
            item.SetValue(False)
        self.prev = evt.GetSelection() and evt.GetId()

        btn = evt.GetEventObject()
        self.numpad.SetSelection(int(btn.GetLabel() or 0))

        if evt.GetSelection():
            row, col = divmod(evt.GetId() - 200, 9)
            nums = self.sudoku.GetRow(row) + self.sudoku.GetColumn(col) + self.sudoku.GetBlock(row, col)
            [nums.remove(self.sudoku.data[row][col]) for _ in range(3)]
            self.numpad.SetEnables(set(range(1, 10)) - set(nums))
        else:
            self.numpad.SetEnables(list(range(1, 10)))

    def SetCell(self, row, col, num):
        self.sudoku.SetCell(row, col, num)
        self.GetItem(row, col).SetLabel(str(num or ''))

    def SetCellColour(self, row, col, colour):
        self.GetItem(row, col).SetBackgroundColour(colour)

    def SetData(self, data):
        for row, col in itertools.product(range(9), repeat=2):
            self.SetCell(row, col, data[row][col])

    def SetLock(self):
        if any(item.IsEnabled() and item.GetLabel() for item in self.GetItems()):
            for item in self.GetItems():
                if item.GetLabel():
                    item.Disable()
        else:
            for item in self.GetItems():
                item.Enable()

    def ClearUnlocked(self):
        for i, item in enumerate(self.GetItems()):
            if item.IsEnabled():
                row, col = divmod(i, 9)
                self.SetCell(row, col, 0)
        self.numpad.SetSelection()

    def OnSetNum(self, num):
        if self.prev:
            row, col = divmod(self.prev - 200, 9)
            self.SetCell(row, col, num)

        for row, col in itertools.product(range(9), repeat=2):
            self.SetCellColour(row, col, COLOUR_GRAY)

        if not num:
            return

        for row, col in itertools.product(range(9), repeat=2):
            if num in self.sudoku.GetRow(row) + self.sudoku.GetColumn(col) + self.sudoku.GetBlock(row, col):
                self.SetCellColour(row, col, COLOUR_GREEN)
            else:
                self.SetCellColour(row, col, COLOUR_GRAY)

    def AutoComplete(self):
        self.sudoku.Solve()
        self.SetData(self.sudoku.data)
        self.numpad.SetSelection()


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = Sudoku()
        self.numbox = NumBox(self)  # define first for right focus sequence
        self.numpad = NumPad(self)

        self.numbox.numpad = self.numpad
        self.numpad.numbox = self.numbox

        btn1 = wx.Button(self, -1, '锁定')
        btn2 = wx.Button(self, -1, '自动')
        btn3 = wx.Button(self, -1, '清除')

        toolbar = wx.BoxSizer(wx.VERTICAL)
        toolbar.Add(self.numpad, 0, wx.EXPAND)
        toolbar.Add(0, 1, wx.EXPAND)
        toolbar.Add(btn1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        toolbar.Add(btn2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        toolbar.Add(btn3, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)

        btn1.Bind(wx.EVT_BUTTON, lambda e: self.numbox.SetLock())
        btn2.Bind(wx.EVT_BUTTON, lambda e: self.numbox.AutoComplete())
        btn3.Bind(wx.EVT_BUTTON, lambda e: self.numbox.ClearUnlocked())

        box = wx.BoxSizer()
        box.Add(self.numbox)
        box.Add(toolbar, 0, wx.ALL | wx.EXPAND)
        self.SetSizerAndFit(box)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Sudoku')

        self.panel = MyPanel(self)

        self.SetFixedSize()
        self.Center()
        self.Show()

        self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

    def OnKeyPress(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.Destroy()
        evt.Skip()

    def SetFixedSize(self):
        size = self.panel.GetSize()
        self.SetClientSize(size)
        self.SetMaxClientSize(size)
        self.SetMinClientSize(size)
        self.EnableMaximizeButton(False)


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()

    frame.panel.numbox.SetData([
        [7, 0, 0, 0, 0, 4, 0, 0, 0],
        [0, 4, 0, 0, 0, 5, 9, 0, 0],
        [8, 0, 0, 0, 0, 0, 0, 2, 0],
        [0, 0, 6, 0, 9, 0, 0, 0, 4],
        [0, 1, 0, 0, 0, 0, 0, 3, 0],
        [2, 0, 0, 0, 8, 0, 5, 0, 0],
        [0, 5, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 3, 7, 0, 0, 0, 8, 0],
        [0, 0, 0, 2, 0, 0, 0, 0, 6],
    ])
    frame.panel.numbox.SetLock()

    app.MainLoop()
