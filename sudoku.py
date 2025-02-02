# TODO
# 分割线 标色 数字小键盘
# 编辑 清除 撤销 重做

import wx


class Sudoku:
    def __init__(self, data=None):
        self.data = data or [[0] * 9 for i in range(9)]

    def GetRow(self, id):
        return self.data[id][:]

    def GetColumn(self, id):
        return [row[id] for row in self.data]

    def GetBlockRC(self, r, c):
        r1 = r // 3 * 3
        c1 = c // 3 * 3
        for r in range(r1, r1 + 3):
            for c in range(c1, c1 + 3):
                yield r, c

    def GetBlock(self, *id):
        if len(id) == 1:
            r, c = divmod(id[0], 3)
        elif len(id) == 2:  # r, c
            r = id[0] // 3
            c = id[1] // 3
        return [self.data[r][c] for r, c in self.GetBlockRC(r * 3, c * 3)]

    def GetPossibles(self, r, c):
        if not self.data[r][c]:
            nums = self.GetRow(r) + self.GetColumn(c) + self.GetBlock(r, c)
            return [num for num in range(1, 10) if num not in nums]
        else:
            return []

    def CheckRepeat(self, nums):
        for num in range(1, 10):
            if nums.count(num) > 1:
                return num

    def CheckError(self):
        for i in range(9):
            num = self.CheckRepeat(self.GetRow(i))
            if num:
                return f'Error: Multiple num {num} in row {i + 1}'
            num = self.CheckRepeat(self.GetColumn(i))
            if num:
                return f'Error: Multiple num {num} in column {i + 1}'
            num = self.CheckRepeat(self.GetBlock(i))
            if num:
                return f'Error: Multiple num {num} in block {i + 1}'

    def CheckFinished(self):
        return all(sum(self.data, [])) and not self.CheckError()

    def SolveOne(self):
        count = 0
        for i in range(81):
            r, c = divmod(i, 9)
            if self.data[r][c]:
                continue
            possibles = self.GetPossibles(r, c)
            if len(possibles) == 1:
                self.data[r][c] = possibles[0]
                count += 1
            else:
                for num in possibles:
                    if (
                        sum(num in self.GetPossibles(r2, c) for r2 in range(9)) == 1 or
                        sum(num in self.GetPossibles(r, c2) for c2 in range(9)) == 1 or
                        sum(num in self.GetPossibles(r2, c2) for r2, c2 in self.GetBlockRC(r, c)) == 1
                    ):
                        self.data[r][c] = num
                        count += 1
                        break
        return count

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


class NumPad(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.gbs = wx.GridBagSizer(vgap=5, hgap=5)

        for r in range(3):
            for c in range(3):
                n = 3 * r + c + 1
                btn = wx.ToggleButton(self, 100 + n, str(n), size=(30, 30))
                btn.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton)
                self.gbs.Add(btn, (r, c), flag=wx.EXPAND)

        box = wx.BoxSizer()
        box.Add(self.gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

    def OnButton(self, evt):
        n1 = evt.GetId() - 100
        for n2 in range(1, 10):
            if n1 != n2:
                btn = wx.FindWindowById(100 + n2, self)
                btn.SetValue(False)
        self.parent.OnSetNum(evt.GetSelection() and n1)

    def SetSelection(self, n):
        for n2 in range(1, 10):
            btn = wx.FindWindowById(100 + n2, self)
            btn.SetValue(n == n2)

    def SetEnables(self, ns):
        for n2 in range(1, 10):
            btn = wx.FindWindowById(100 + n2, self)
            btn.Enable(n2 in ns)


class NumBox(wx.Panel):
    def __init__(self, parent, sudoku):
        wx.Panel.__init__(self, parent)

        self.parent = parent

        self.hint = True
        self.prev = None
        self.sudoku = sudoku

        self.gbs = wx.GridBagSizer()

        id = 200
        for r in range(13):
            for c in range(13):
                if r in (0, 4, 8, 12) or c in (0, 4, 8, 12):
                    item = Border(self, 3)
                else:
                    item = wx.ToggleButton(self, id, size=(30, 30))
                    item.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton)
                    id += 1
                self.gbs.Add(item, (r, c), flag=wx.EXPAND)

        box = wx.BoxSizer()
        box.Add(self.gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

        self.SetData([
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
        self.SetLock()

    def GetItem(self, r, c):
        assert (0, 0) <= (r, c) <= (8, 8), (r, c)
        return wx.FindWindowById(200 + 9 * r + c, self)

    def GetItems(self):
        for i in range(81):
            yield wx.FindWindowById(200 + i, self)

    def OnButton(self, evt):
        if self.prev:
            item = wx.FindWindowById(self.prev, self)
            item.SetValue(False)
        self.prev = evt.GetSelection() and evt.GetId()

        btn = evt.GetEventObject()
        self.parent.SetSelection(int(btn.GetLabel() or 0))

        if self.hint and evt.GetSelection():
            r, c = divmod(evt.GetId() - 200, 9)
            nums = self.sudoku.GetRow(r) + self.sudoku.GetColumn(c) + self.sudoku.GetBlock(r, c)
            for i in range(3):
                nums.remove(self.sudoku.data[r][c])
            self.parent.SetEnables(set(range(1, 10)) - set(nums))
        else:
            self.parent.SetEnables(list(range(1, 10)))

    def SetCell(self, r, c, n):
        self.sudoku.data[r][c] = n
        self.GetItem(r, c).SetLabel(str(n or ''))

    def SetCellColour(self, r, c, colour):
        self.GetItem(r, c).SetBackgroundColour(colour)

    def SetData(self, data):
        for r in range(9):
            for c in range(9):
                self.SetCell(r, c, data[r][c])

    def SetLock(self):
        for item in self.GetItems():
            if item.GetLabel():
                item.Disable()

    def SetUnlock(self):
        for item in self.GetItems():
            item.Enable()

    def ClearUnlocked(self):
        for i, item in enumerate(self.GetItems()):
            if item.IsEnabled():
                r, c = divmod(i, 9)
                self.SetCell(r, c, 0)

    def OnSetNum(self, n):
        if self.prev:
            r, c = divmod(self.prev - 200, 9)
            self.SetCell(r, c, n)

        if self.hint:
            for r in range(9):
                for c in range(9):
                    self.SetCellColour(r, c, COLOUR_GRAY)

        if self.hint and n:
            for r in range(9):
                if n in self.sudoku.GetRow(r):
                    for c in range(9):
                        self.SetCellColour(r, c, COLOUR_GREEN)

            for c in range(9):
                if n in self.sudoku.GetColumn(c):
                    for r in range(9):
                        self.SetCellColour(r, c, COLOUR_GREEN)

            for r1 in range(0, 9, 3):
                for c1 in range(0, 9, 3):
                    if n in self.sudoku.GetBlock(r1, c1):
                        for r in range(r1, r1 + 3):
                            for c in range(c1, c1 + 3):
                                self.SetCellColour(r, c, COLOUR_GREEN)

    def AutoComplete(self):
        if self.sudoku.CheckError():
            return "Exist error, can't auto complete."
        self.sudoku.Solve()
        self.SetData(self.sudoku.data)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = Sudoku()
        self.numbox = NumBox(self, self.sudoku)
        self.numpad = NumPad(self)

        self.OnSetNum = self.numbox.OnSetNum
        self.SetEnables = self.numpad.SetEnables
        self.SetSelection = self.numpad.SetSelection

        btn1 = wx.Button(self, -1, '锁定')
        btn2 = wx.Button(self, -1, '解锁')
        btn3 = wx.Button(self, -1, '清除')
        btn5 = wx.Button(self, -1, '自动')
        btn6 = wx.Button(self, -1, '检查')

        toolbar = wx.BoxSizer(wx.VERTICAL)
        toolbar.Add(self.numpad, 0, wx.EXPAND)
        toolbar.Add(0, 1, wx.EXPAND)
        toolbar.Add(btn1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        toolbar.Add(btn2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        toolbar.Add(btn3, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        toolbar.Add(btn5, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)
        toolbar.Add(btn6, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5)

        btn1.Bind(wx.EVT_BUTTON, lambda e: self.numbox.SetLock())
        btn2.Bind(wx.EVT_BUTTON, lambda e: self.numbox.SetUnlock())
        btn3.Bind(wx.EVT_BUTTON, lambda e: self.numbox.ClearUnlocked())
        btn5.Bind(wx.EVT_BUTTON, lambda e: self.numbox.AutoComplete())
        btn6.Bind(wx.EVT_BUTTON, lambda e: wx.MessageBox(self.sudoku.CheckError() or 'No error found!', 'Error'))

        box = wx.BoxSizer()
        box.Add(self.numbox)
        box.Add(toolbar, 0, wx.ALL | wx.EXPAND)
        self.SetSizerAndFit(box)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Sudoku')
        self.panel = MyPanel(self)
        size = self.panel.GetSize()
        self.SetClientSize(size)
        self.SetMaxClientSize(size)
        self.SetMinClientSize(size)
        self.EnableMaximizeButton(False)
        self.Center()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame()
    app.MainLoop()
