import wx


class Sudoku(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        choices = [''] + list('123456789')
        self.gbs = wx.GridBagSizer(vgap=5, hgap=5)

        for r in range(9):
            for c in range(9):
                choice = wx.Choice(self, choices=choices)
                self.gbs.Add(choice, (r, c), flag=wx.EXPAND)

        box = wx.BoxSizer()
        box.Add(self.gbs, 1, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(box)

    def GetData(self):
        data = []
        for i, item in enumerate(self.gbs.GetChildren()):
            choice = item.GetWindow()
            num = int(choice.GetStringSelection() or 0)
            if i % 9 == 0:
                data.append([])
            data[-1].append(num)
        return data

    def GetRow(self, row):
        return self.GetData()[row]

    def GetCol(self, col):
        return [row[col] for row in self.GetData()]


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sudoku = Sudoku(self)
        self.toolbar = wx.BoxSizer(wx.VERTICAL)

        btn1 = wx.Button(self, -1, '锁定')
        btn2 = wx.Button(self, -1, '解锁')
        btn3 = wx.Button(self, -1, '报错')
        btn4 = wx.Button(self, -1, '提示')
        btn5 = wx.Button(self, -1, '自动')
        btn6 = wx.Button(self, -1, '检查')

        self.toolbar.Add(0, 1, wx.EXPAND)
        self.toolbar.Add(btn1, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn3, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn4, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn5, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.toolbar.Add(btn6, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        box = wx.BoxSizer()
        box.Add(self.sudoku)
        box.Add(self.toolbar, 0, wx.ALL | wx.EXPAND)
        self.SetSizerAndFit(box)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Sudoku')
        self.panel = MyPanel(self)
        self.SetClientSize(self.panel.GetSize())
        self.Center()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame()
    app.MainLoop()
