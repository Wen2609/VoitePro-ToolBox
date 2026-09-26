# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
csfp = r'D:\doubao space\VioletToolBox\VioletToolBox\MainWindow.xaml.cs'
t = io.open(csfp, 'r', encoding='utf-8').read()
old = """                var r = dt.LoadContent() as FrameworkElement;
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " after\\r\\n"); } catch { }
                return r;
            }
            catch { return null; }"""
new = """                var r = dt.LoadContent() as FrameworkElement;
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " after\\r\\n"); } catch { }
                return r;
            }
            catch (Exception _lcex)
            {
                try { System.IO.File.AppendAllText(System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "startup.log"), "LC " + viewName + " EX: " + _lcex.GetType().Name + ": " + _lcex.Message + "\\r\\n"); } catch { }
                return null;
            }"""
assert old in t, 'anchor NOT FOUND'
t = t.replace(old, new, 1)
io.open(csfp, 'w', encoding='utf-8', newline='').write(t)
print('InstantiatePage exception logging added')
