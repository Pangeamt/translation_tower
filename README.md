# Translation Tower

Translate texts and annotations with bing or deepl 

## Install
Require python 3.8>

```BASH
git clone https://github.com/Pangeamt/translation_tower.git
```

```BASH
cd translation_tower
```

```BASH
pip install -r requirements.txt
```

## Config:
1. Edit data/config/secret_sample.yaml and write valid API Keys for bing or deepl 
2. rename data/config/secret_sample.yaml -> data/config/secret.yaml

## Example 1: translate an uima_cas_xmi file
From Inception download an annotated corpus as "uima cas xmi"
Adapt the translate.xmi.py script to translate the file