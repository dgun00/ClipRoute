# -*- coding: utf-8 -*-
import pandas as pd
path = r"C:\Users\한동건\Desktop\Clirpoute_admin_page\utils\Clip Route - 강릉.csv"
for enc in ["utf-8-sig","cp949","euc-kr"]:
    try:
        df = pd.read_csv(path, encoding=enc)
        print('ENC', enc)
        print(df.head(5).to_string())
        print('COLUMNS', list(df.columns))
        break
    except Exception as e:
        print('FAIL', enc, e)
