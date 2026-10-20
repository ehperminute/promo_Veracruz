from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import MonthLocator, DateFormatter
P=Path(__file__).resolve().parent
O=P/'outputs'
data=pd.read_csv(O/'datatur_2025_2026_observado.csv');data['fecha']=pd.to_datetime(data.fecha)
fig,ax=plt.subplots(figsize=(9.6,3.0))
for center,g in data.groupby('centro',sort=False):
    g=g.set_index('fecha').asfreq('MS')
    ax.plot(g.index,g.ocupacion_pct,marker='o',markersize=3,label=center,linewidth=1.5)
for v in [40,50]:ax.axhline(v,ls='--',lw=.8,alpha=.5)
ax.set_title('Ocupación mensual observada: tres centros DataTur (2025–2026)')
ax.set_ylabel('Ocupación (%)')
ax.set_ylim(25,70)
ax.grid(alpha=.2)
ax.xaxis.set_major_locator(MonthLocator(interval=2));ax.xaxis.set_major_formatter(DateFormatter('%b %y'))
ax.tick_params(axis='x',labelrotation=35)
ax.legend(fontsize=8,ncol=3,loc='upper right')
fig.tight_layout();fig.savefig(P/'ocupacion_serie.png',dpi=160);plt.close(fig)
sm=pd.read_csv(O/'resumen_validacion_markov.csv')
fig,ax=plt.subplots(figsize=(8.7,3.0))
x=list(range(len(sm)));width=.34
ax.bar([i-width/2 for i in x],100*sm.markov_accuracy,width,label='Markov')
ax.bar([i+width/2 for i in x],100*sm.persistence_accuracy,width,label='Persistencia')
ax.set_xticks(x,sm.centro.to_list());ax.set_ylim(0,90);ax.set_ylabel('Exactitud en estados (%)');ax.legend();ax.grid(axis='y',alpha=.15)
ax.set_title('Validación 2026: clasificación del estado de ocupación')
for i,r in enumerate(sm.itertuples()):
    ax.text(i-width/2,100*r.markov_accuracy+3,f'{r.markov_correct}/{r._asdict().get("_4",7)}' if False else f'{r.markov_correct}',ha='center',fontsize=8)
fig.tight_layout();fig.savefig(P/'comparacion_validacion.png',dpi=160);plt.close(fig)
