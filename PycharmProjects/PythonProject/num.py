
import numpy as np
import pandas as pd

a = np.arange(20).reshape(4, 5)

print(a)
print(a.shape)
print(a.ndim)
print(a.size)

print(np.random.rand(10))

s = pd.Series(np.random.random(5), pd.date_range('1/1/2000', periods=5))
print(s.T)
print(s + s)


