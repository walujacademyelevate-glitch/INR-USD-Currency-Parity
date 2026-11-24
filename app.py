import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from model import calculate
st.set_page_config(page_title='INR / USD | Parity Lab',page_icon='📈',layout='wide')
st.title('INR / USD • Currency Parity Lab')
st.caption('International Finance | FRED annual data | 2000–2024 | INR per USD')
raw=pd.read_csv(Path(__file__).with_name('fred_dataset.csv'))
base=st.sidebar.selectbox('PPP anchor year',raw.year.tolist(),index=0)
lo,hi=st.sidebar.slider('Display years',2000,2024,(2000,2024))
d=calculate(raw,base); v=d[d.year.between(lo,hi)]; z=v.iloc[-1]
st.sidebar.download_button('Download source dataset',raw.to_csv(index=False),'fred_dataset.csv','text/csv')
st.sidebar.download_button('Download calculated dataset',d.to_csv(index=False),'calculated_dataset.csv','text/csv')
a,b,c=st.tabs(['PPP & Currency Misalignment','IRP & Carry Trade Tracker','International Fisher Effect'])
def line(fields,labels):
    q=v[['year']+fields].rename(columns=dict(zip(fields,labels)))
    st.plotly_chart(px.line(q,x='year',y=labels,markers=True,template='plotly_white'),use_container_width=True)
with a:
    st.subheader('Relative purchasing power parity')
    x,y,w=st.columns(3); x.metric('Actual INR per USD',f'{z.spot:.2f}'); y.metric('PPP implied',f'{z.PPP:.2f}'); w.metric('INR valuation gap',f'{z.misalignment:+.2f}%')
    status='Near parity' if abs(z.misalignment)<=1 else ('INR overvalued' if z.misalignment>0 else 'INR undervalued')
    st.info(f'{int(z.year)} • {status} (±1% tolerance; relative to anchor {base})')
    line(['spot','PPP'],['Actual spot rate','PPP implied spot rate'])
    st.caption('Relative PPP is anchor-dependent, not an absolute fair-value estimate. A positive gap means INR is stronger than the PPP benchmark.')
with b:
    st.subheader('Interest parity and USD-funded INR carry')
    x,y,w=st.columns(3); x.metric('Prior-year yield spread',f'{z.prior_yield_diff:.2f} pp'); y.metric('Carry excess return',f'{z.carry_return:+.2f}%'); w.metric('Carry profitability index',f'{z.carry_index:.2f}')
    line(['prior_yield_diff','spot_change'],['Prior-year yield differential (pp)','USD appreciation / INR depreciation (%)'])
    line(['carry_index'],['Compounded carry index (2000 = 100)'])
    line(['CIP_forward','spot'],['CIP-implied forward (prior year)','Realized spot'])
    st.warning('CIP forward is theoretical; without observed forward quotes CIP cannot be empirically tested. Annual average spot and overnight rates are proxies, not executable one-year returns.')
    st.caption('UIP comparison uses prior-year rates against subsequent annual spot change. Carry return is relative to USD funding, excluding costs.')
with c:
    st.subheader('International Fisher Effect diagnostic')
    r=v.inflation_diff.corr(v.yield_diff); st.metric('Pearson correlation',f'{r:.3f}')
    fig=px.scatter(v,x='inflation_diff',y='yield_diff',hover_name='year',labels={'inflation_diff':'Inflation differential (pp)','yield_diff':'Interest differential (pp)'},template='plotly_white')
    low=min(v.inflation_diff.min(),v.yield_diff.min()); high=max(v.inflation_diff.max(),v.yield_diff.max()); fig.add_trace(go.Scatter(x=[low,high],y=[low,high],mode='lines',name='Equality benchmark'))
    st.plotly_chart(fig,use_container_width=True)
    st.caption('Realized inflation is a proxy for expected inflation; equality assumes equal real interest rates. Correlation is descriptive, not causal.')
with st.expander('Sources and data'):
    for s in ['AEXINUS','FPCPITOTLZGIND','FPCPITOTLZGUSA','IRSTCI01INA156N','IRSTCI01USA156N']: st.markdown(f'[{s}](https://fred.stlouisfed.org/series/{s})')
    st.dataframe(v,use_container_width=True)
