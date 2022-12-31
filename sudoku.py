# TODO
# 分割线 标色 数字小键盘
# 编辑 清除 撤销 重做

import wx


def repeat(nums):
    for n in range(1, 10):
        if nums.count(n) > 1:
            return n


class NumPad(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.parent = parent
        self.gbs = wx.GridBagSizer(vgap=5, hgap=5)

        for r in range(3):
            for c in range(3):
                n = 3 * r + c + 1
                btn = wx.ToggleButton(self, 100 + n, str(n), size=(30, -1))
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


class Sudoku(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        choices = [''] + list('123456789')
        self.gbs = wx.GridBagSizer(vgap=5, hgap=5)
        self.data = [[0] * 9] * 9

        for r in range(9):
            for c in range(9):
                choice = wx.Choice(self, choices=choices)
                choice.Bind(wx.EVT_CHOICE, lambda e: self.GetData())
                self.gbs.Add(choice, (r, c), flag=wx.EXPAND)

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

    def GetData(self):
        data = []
        for i, item in enumerate(self.gbs.GetChildren()):
            choice = item.GetWindow()
            num = int(choice.GetStringSelection() or 0)
            if i % 9 == 0:
                data.append([])
            data[-1].append(num)
        self.data = data

    def SetData(self, data):
        self.data = data
        children = iter(self.gbs.GetChildren())
        for r in range(9):
            for c in range(9):
                choice = next(children).GetWindow()
                choice.SetSelection(data[r][c])

    def SetCell(self, r, c, n):
        self.data[r][c] = n
        id = r * 9 + c
        choice = list(self.gbs.GetChildren())[id].GetWindow()
        choice.SetSelection(n)

    def SetLock(self):
        for item in self.gbs.GetChildren():
            choice = item.GetWindow()
            if choice.GetStringSelection():
                choice.Disable()

    def SetUnlock(self):
        for item in self.gbs.GetChildren():
            choice = item.GetWindow()
            choice.Enable()

    def OnSetNum(self, n):
        print(n)

    def CheckError(self):
        for r in range(9):
            arr = self.data[r]
            num = repeat(arr)
            if num:
                return f'Error: Multiple num {num} in row {r + 1}'
        for c in range(9):
            arr = [row[c] for row in self.data]
            num = repeat(arr)
            if num:
                return f'Error: Multiple num {num} in column {c + 1}'
        for r in range(3):
            for c in range(3):
                arr = sum([row[3*c:3*c+3] for row in self.data[3*r:3*r+3]], [])
                num = repeat(arr)
                if num:
                    return f'Error: Multiple num {num} in block {r + 1}-{c + 1}'

    def CheckFinish(self):
        return all(sum(self.data, [])) and not self.CheckError()

    def AutoComplete(self):
        if self.CheckError():
            return "Exist error, can't auto complete."
        while True:
            exist = False
            for r in range(9):
                for c in range(9):
                    if not self.data[r][c]:
                        row = self.data[r]
                        col = [row[c] for row in self.data]
                        r1 = r // 3 * 3
                        c1 = c // 3 * 3
                        block = sum([row[c1:c1+3] for row in self.data[r1:r1+3]], [])
                        choices = set(range(1, 10)) - set(row + col + block)
                        print((r, c, choices))
                        if len(choices) == 1:
                            exist = True
                            self.SetCell(r, c, choices.pop())
            if not exist:
                break


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sudoku = Sudoku(self)
        self.numpad = NumPad(self)
        self.toolbar = wx.BoxSizer(wx.VERTICAL)

        self.OnSetNum = self.sudoku.OnSetNum

        btn1 = wx.Button(self, -1, '锁定')
        btn2 = wx.Button(self, -1, '解锁')
        btn3 = wx.Button(self, -1, '报错')
        btn4 = wx.Button(self, -1, '提示')
        btn5 = wx.Button(self, -1, '自动')
        btn6 = wx.Button(self, -1, '检查')

        self.toolbar.Add(self.numpad, 0, wx.EXPAND)
        self.toolbar.Add(0, 1, wx.EXPAND)
        self.toolbar.Add(btn1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn3, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn4, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn5, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn6, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        btn1.Bind(wx.EVT_BUTTON, lambda e: self.sudoku.SetLock())
        btn2.Bind(wx.EVT_BUTTON, lambda e: self.sudoku.SetUnlock())
        btn5.Bind(wx.EVT_BUTTON, lambda e: self.sudoku.AutoComplete())
        btn6.Bind(wx.EVT_BUTTON, lambda e: wx.MessageBox(self.sudoku.CheckError() or 'No error found!', 'Error'))

        box = wx.BoxSizer()
        box.Add(self.sudoku)
        box.Add(self.toolbar, 0, wx.ALL | wx.EXPAND)
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
