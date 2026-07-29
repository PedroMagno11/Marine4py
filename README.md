# marine4py

Framework genérico e multi-dialeto para parsing e geração de sentenças NMEA em Python — suporta NMEA-0183, AIS e dialetos definidos pelo usuário, com especificação explícita de dialeto.

## Instalação

```bash
pip install marine4py
```

## Uso rápido

```python
from marine4py import parse

sentence = parse(
    "$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
    dialect="gps",
)
print(sentence.latitude, sentence.longitude)
```

## Status

Projeto em fase inicial (alpha). Sentenças NMEA-0183 implementadas hoje: `GGA`, `RMC`, `VTG`, `GSA`, `GSV`, `ZDA`, `GLL`, `HDT`, além de suporte a AIS e a sentenças proprietárias (`$P...`).

## Estrutura

```
marine4py/
├── core/                  
│   ├── assembler.py
│   ├── checksum.py        
│   ├── error.py           
│   ├── field.py           
│   ├── framing.py         
│   ├── nmea.py
│   ├── registry.py            
│   └── stream.py          
├── dialects/
    ├── ais/   
    ├── gps/               
    └── proprietary/               

```