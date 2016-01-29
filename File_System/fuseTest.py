from covertfs import CovertFS
from memfuse import MemFS
m = CovertFS()
bytestring = b'/ testfile.txt,url.txt,1453390554.8954098\n'
m.loadfs(bytestring.decode())
m.tree()
f = MemFS(m)
print(f.getattr('/testfile.txt'))
import memfuse
mp = memfuse.mount(f,'temp')