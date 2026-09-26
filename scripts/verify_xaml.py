# -*- coding: utf-8 -*-
"""验证改造后的 XAML 结构"""
import io, sys
import xml.parsers.expat
sys.stdout.reconfigure(encoding='utf-8')

XAML = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml'
c = io.open(XAML, 'r', encoding='utf-8').read()

counts = {
    'PageHost': c.count('x:Name="PageHost"'),
    'DataTemplate Page_': c.count('DataTemplate x:Key="Page_'),
    'HomeView': c.count('Name="HomeView"'),
    '残留 View 块 (EdlFlashView 非模板)': len([m for m in __import__('re').finditer(r'Name="EdlFlashView"', c)]),
    'FastbootCardGroupBoxStyle': c.count('FastbootCardGroupBoxStyle'),
    'Window.Resources close': c.count('</FrameworkElement.Resources>'),
    'FrameworkElement.Resources open': c.count('<FrameworkElement.Resources>'),
}
for k, v in counts.items():
    print(f'{k}: {v}')

# XML 良构验证
class P:
    def __init__(self):
        self.stack = []
        self.maxdepth = 0
    def start(self, tag, attrs):
        self.stack.append(tag)
        self.maxdepth = max(self.maxdepth, len(self.stack))
    def end(self, tag):
        self.stack.pop()
p = P()
parser = xml.parsers.expat.ParserCreate(); parser.buffer_text = True
p.p = parser
parser.StartElementHandler = p.start; parser.EndElementHandler = p.end
try:
    parser.Parse(c, True)
    print(f'XML OK, max depth {p.maxdepth}, remaining stack {len(p.stack)}')
except Exception as e:
    print('XML ERROR:', e, 'line', parser.CurrentLineNumber)
