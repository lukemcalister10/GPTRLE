import pandas as pd

def test_targets_present_and_nested():
 d=pd.read_csv('output/annual_rows.csv',nrows=1000)
 for l in range(1,6):
  assert f'l{l}_meaningful' in d
  for t in (80,90,100,110,120): assert f'l{l}_{t}' in d
  assert ((d[f'l{l}_120']<=d[f'l{l}_110']) & (d[f'l{l}_110']<=d[f'l{l}_100']) & (d[f'l{l}_100']<=d[f'l{l}_90']) & (d[f'l{l}_90']<=d[f'l{l}_80'])).all()
