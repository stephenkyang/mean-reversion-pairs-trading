import numpy as np
import pandas as pd
import statsmodels
np.random.seed(87)
import matplotlib.pyplot as plt
Xreturns = np.random.normal(0, 1, 100)
# sum them and shift all the prices up
X = pd.Series(np.cumsum(Xreturns), name='X') + 50
X.plot(figsize=(15,7))
plt.show()
