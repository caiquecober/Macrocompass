import streamlit as st
import pandas as pd
#pacotes utilizados
import numpy as np
from datetime import date
import json
#import plotly
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from urllib.request import urlopen
import pandas as pd
import requests
from io import StringIO, BytesIO
import base64
import io
api_key = 'daece1e7e3daf0bcd26c06cdef0009bb'
############################################################## Streamlit APP ##################################################################################################
html_header="""
<head>
<style> @import url('https://fonts.googleapis.com/css2?family=Mulish:wght@400;500;600;700;800&display=swap'); 
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&display=swap'); </style>
<title>StoneX - Energy </title>
<meta charset="utf-8">
<meta name="keywords" content="StoneX, visualizer, data">
<meta name="description" content="c0data project Data Project">
<meta name="author" content="@Cober">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<h1 style="font-size:300%; color:#034B88; font-family:Mulish; font-weight:800"> MacroCompass  Fred Visualizer   
 <hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1px;"></h1>
"""

html_line_2="""
<br>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
"""

html_br="""
<br>
"""

#cofigs inciais
link_imagem_stonex = 'https://raw.githubusercontent.com/caiquecober/Research/master/35131080148.png'

st.set_page_config(page_title="MacroCompass", page_icon=link_imagem_stonex, layout="wide")

st.markdown('<style>body{background-color: #D2D5D4}</style>',unsafe_allow_html=True)
st.markdown(html_header, unsafe_allow_html=True)
st.markdown(""" <style> 
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style> """, unsafe_allow_html=True)


## funções utilizadas na aplicação!
def ts_plot_mc(code, nome, source, units, chart):
    df  =  get_obs(code)
    df =  df.set_index('date')

    # define what type of chart will be made!
    
    if chart == 'percent_change_12':
        df = df.pct_change(12)
        units = 'Year over year percent change'
    elif chart =='percent_change':
         df = df.pct_change()
         units = 'Percent change(%)'
    elif chart == 'nominal_diff':
         df = df.diff()
         units=  'first diference'
    else: 
        print('Normal Config')

    
    fig = go.Figure()
    #colors = [ '#0A3254', '#B2292E','#E0D253','#7AADD4','#336094']
    colors = ['#034B88', '#B55802', '#000000']


    for i in range(len(df.columns)):
        fig.add_trace(go.Scatter(
                x=df.index, y=df.iloc[:, i], line=dict(color=colors[i], width=3), name=df.columns[i]))

    
    fig.add_annotation(
    text = (f"{source}")
    , showarrow=False
    , x = 0
    , y = -0.2
    , xref='paper'
    , yref='paper' 
    , xanchor='left'
    , yanchor='bottom'
    , xshift=-1
    , yshift=-5
    , font=dict(size=10, color="grey")
    , font_family= "Verdana"
    , align="left"
    ,)
    

    fig.update_layout(title={ 'text': '<b>'+ nome+'<b>','y':0.9,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                            paper_bgcolor='rgba(0,0,0,0)', #added the backround collor to the plot 
                            plot_bgcolor='rgba(0,0,0,0)',
                             title_font_size=14,
                             font_color = '#0D1018',
                             #xaxis_title=f"{source}",
                             yaxis_title=units, 
                             template='plotly_white',
                             font_family="Verdana",
                             images=[dict(source='https://raw.githubusercontent.com/caiquecober/Research/master/35131080148.png',
                                 xref="paper", yref="paper",
                                 x=0.5, y=0.5,
                                 sizex=0.75, sizey=0.75,
                                 opacity=0.2,
                                 xanchor="center",
                                 yanchor="middle",
                                 sizing="contain",
                                 visible=True,
                                 layer="below")],
                             legend=dict(
                                 orientation="h",
                                 yanchor="bottom",
                                 y=-0.29,
                                 xanchor="center",
                                 x=0.5,
                                 font_family='Verdana'),
                                 autosize=True,height=500,
                                 #yaxis_tickformat = ',.0%'                                
    
                                 )
    
    if chart =='percent_change' or  chart == 'percent_change_12':
            fig.update_layout(yaxis= { 'tickformat': ',.2%'})
                                 
    return fig

def get_obs(series_title):
    '''gets the time series values and cleans it'''
    endpoint = 'https://api.stlouisfed.org/fred/series/observations'

    series_id = series_title

    params = {
    'series_id': series_id,
    'api_key': api_key,
    'file_type': 'json',
    'limit': 100000
                }
    
    r = requests.get(endpoint,params=params)
    json = r.json()
    df = pd.DataFrame.from_dict(json.get('observations')[0:])
    df = clean(df)
    
    return  df

def clean(df):
    df= df[['date', 'value']].copy()
    df['date'] = pd.to_datetime(df['date'])
    df.value = df.value.replace('.',np.nan)
    df = df[df.date>'2000-01-01']
    #df = df.set_index('date')
    print(df)
    df.value = df.value.fillna( method='ffill')
    df.value = df.value.replace(',','').astype(float)
    return df
    

def get_series(id_selected):
    '''gets the time series values and cleans it'''
    endpoint = 'https://api.stlouisfed.org/fred/series?'

    params = {
    'series_id': id_selected,
    'api_key': api_key,
    'file_type': 'json',
    'limit': 100000
                }
    
    r = requests.get(endpoint,params=params)
    json = r.json()
    titulo  = json.get('seriess')[0].get('title')
    units_short=  json.get('seriess')[0].get('units_short')
    return titulo, units_short


################################################ Streamlit App #########################################################################

#Options headers
col1, col2,_, col3 = st.columns((2,2,1,2))
fred_code = col1.text_input('FRED code', value="CPILFESL")
titulo = col2.text_input('Chart Title', value="US inflation - ex energy and food")

st.markdown(html_line_2, unsafe_allow_html=True)

title , units  = get_series(fred_code)
col3.markdown(f'**Sugested Title:** <br> {title}')

#generate figures
fig = ts_plot_mc(fred_code, titulo, 'Source: FRED, MacroCompass.',units,  'Normal')
fig1 = ts_plot_mc(fred_code, titulo, 'Source: FRED, MacroCompass.', units, 'percent_change')
fig2 = ts_plot_mc(fred_code, titulo, 'Source: FRED, Macro Compass.', units, 'percent_change_12')
fig3 = ts_plot_mc(fred_code, titulo, 'Source: FRED, Macro Compass.', units, 'nominal_diff')

col1, col2 = st.columns(2)
col1.plotly_chart(fig,use_container_width=True)
col2.plotly_chart(fig1,use_container_width=True)
col1.plotly_chart(fig2,use_container_width=True)
col2.plotly_chart(fig3,use_container_width=True)

#################################### download button ###################################################################################

#codificando os gráficos
buffer = io.StringIO()
fig.write_html(buffer, include_plotlyjs='cdn')
html_bytes = buffer.getvalue().encode()

buffer = io.StringIO()
fig1.write_html(buffer, include_plotlyjs='cdn')
html_bytes1 = buffer.getvalue().encode()

buffer = io.StringIO()
fig2.write_html(buffer, include_plotlyjs='cdn')
html_bytes2 = buffer.getvalue().encode()

buffer = io.StringIO()
fig3.write_html(buffer, include_plotlyjs='cdn')
html_bytes3 = buffer.getvalue().encode()


#layout dos bottons
st.markdown(html_line_2, unsafe_allow_html=True)
st.markdown(html_br, unsafe_allow_html=True)
col1,col2, col3, col4 = st.columns(4)

col1.download_button(
    label='Download HTML fig',
    data=html_bytes,
    file_name=f'{fred_code}.html',
    mime='text/html')

col2.download_button(
    label='Download HTML fig1',
    data=html_bytes1,
    file_name=f'{fred_code}.html',
    mime='text/html')



col3.download_button(
    label='Download HTML fig2',
    data=html_bytes2,
    file_name=f'{fred_code}.html',
    mime='text/html')

col4.download_button(
    label='Download HTML fig3',
    data=html_bytes3,
    file_name=f'{fred_code}.html',
    mime='text/html')


########################################### banner final ###############################

st.markdown(html_br, unsafe_allow_html=True)

html_line="""
<br>
<br>
<br>
<br>
<p style="color:Gainsboro; text-align: left;">Fonte: FRED.</p>
<hr style= "  display: block;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
  margin-left: auto;
  margin-right: auto;
  border-style: inset;
  border-width: 1.5px;">
<p style="color:Gainsboro; text-align: right;">Desenvolvido por: Caíque Cober</p>
"""
st.markdown(html_line, unsafe_allow_html=True)



    

  


