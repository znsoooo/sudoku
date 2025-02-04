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
        self.Disable()


class NumPad(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = parent.sudoku
        self.numbox = None

        self.number = 0

        gbs = wx.GridBagSizer(vgap=5, hgap=5)
        for num in range(1, 10):
            r, c = divmod(num - 1, 3)
            btn = wx.ToggleButton(self, 100 + num, str(num), size=(30, 30))
            btn.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton)
            gbs.Add(btn, (2 - r, c), flag=wx.EXPAND)
        parent.Bind(wx.EVT_CHAR_HOOK, self.OnKeyPress)

        box = wx.BoxSizer()
        box.Add(gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

    def GetItem(self, num):
        assert 1 <= num <= 9, num
        return wx.FindWindowById(100 + num, self)

    def ToggleButton(self, num):
        assert 0 <= num <= 9, num
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
        self.numpad = parent.numpad

        self.prev = None

        gbs = wx.GridBagSizer()
        id = 200
        for r in range(13):
            for c in range(13):
                if r in [0, 4, 8, 12] or c in [0, 4, 8, 12]:
                    item = Border(self, 3)
                else:
                    item = wx.ToggleButton(self, id, size=(30, 30))
                    item.Bind(wx.EVT_TOGGLEBUTTON, self.OnButton)
                    id += 1
                gbs.Add(item, (r, c), flag=wx.EXPAND)

        box = wx.BoxSizer()
        box.Add(gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

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
        self.numpad.SetSelection(int(btn.GetLabel() or 0))

        if evt.GetSelection():
            r, c = divmod(evt.GetId() - 200, 9)
            nums = self.sudoku.GetRow(r) + self.sudoku.GetColumn(c) + self.sudoku.GetBlock(r, c)
            for i in range(3):
                nums.remove(self.sudoku.data[r][c])
            self.numpad.SetEnables(set(range(1, 10)) - set(nums))
        else:
            self.numpad.SetEnables(list(range(1, 10)))

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
                r, c = divmod(i, 9)
                self.SetCell(r, c, 0)
        self.numpad.SetSelection()

    def OnSetNum(self, n):
        if self.prev:
            r, c = divmod(self.prev - 200, 9)
            self.SetCell(r, c, n)

        for r in range(9):
            for c in range(9):
                self.SetCellColour(r, c, COLOUR_GRAY)

        if n:
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
        self.sudoku.Solve()
        self.SetData(self.sudoku.data)
        self.numpad.SetSelection()


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = Sudoku()
        self.numpad = NumPad(self)
        self.numbox = NumBox(self)
        self.numpad.numbox = self.numbox
        self.numpad.SetSelection()

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

        size = self.panel.GetSize()
        self.SetClientSize(size)
        self.SetMaxClientSize(size)
        self.SetMinClientSize(size)
        self.EnableMaximizeButton(False)

        self.Center()
        self.Show()


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
