from snapshot import build_snapshot

def test_future_fields_do_not_change_snapshot():
    base={'player':'Test','key':'test','pick':10,'year':2020,'type':'ND','drafted_position':'MID','_by':2002,
          'scoring':[{'year':2021,'avg':70,'games':10},{'year':2024,'avg':110,'games':22}]}
    a=build_snapshot(dict(base, future_position='MID', present_position='MID', _retired=False, _club='A'),2021)
    b=build_snapshot(dict(base, future_position='KPF', present_position='FWD', _retired=True, _club='B'),2021)
    assert a==b
    assert a.last_avg==70 and a.total_games==10

def test_post_origin_scoring_is_ignored():
    p={'player':'Test','key':'test','pick':10,'year':2020,'type':'ND','drafted_position':'MID','_by':2002,
       'scoring':[{'year':2021,'avg':70,'games':10},{'year':2022,'avg':100,'games':20}]}
    s=build_snapshot(p,2021)
    assert s.last_avg==70 and s.total_games==10 and s.career_best==70
