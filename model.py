import pandas as pd
import numpy as np

def calculate(d,base=2000):
    d=d.copy(); factor=((1+d.inflation_IN/100)/(1+d.inflation_US/100)).cumprod(); k=d.year.eq(base)
    d['PPP']=d.loc[k,'spot'].iloc[0]*factor/factor[k].iloc[0]
    d['misalignment']=100*(d.PPP/d.spot-1)
    d['yield_diff']=d.rate_IN-d.rate_US
    d['inflation_diff']=d.inflation_IN-d.inflation_US
    d['spot_change']=100*d.spot.pct_change()
    a=1+d.rate_IN.shift()/100; b=1+d.rate_US.shift()/100
    d['prior_yield_diff']=d.yield_diff.shift()
    d['CIP_forward']=d.spot.shift()*a/b
    d['carry_return']=100*(a/b*d.spot.shift()/d.spot-1)
    d['carry_index']=100*(1+d.carry_return.fillna(0)/100).cumprod()
    return d
