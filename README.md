# Scripts for data processing in RCPC

`aer_metric.py` — counts aer for two alignments\
`tsv_to_pharaoh.py` — gets pharaoh alignment from tsv file\
`json_to_tokens.py` — gets tokenized sentences from json. output example:

    русский ||| 中文
`preprocess_sentences.py` — preprocesses sentences in format above (lemmatization, bpe)\
`em_algorithm.py` — aligns sentences in format above
### requirements
python 3.9 or higher required

### installation
    pip install -r requirements.txt

### usage
use `-h` for instructions:

    ./scpipt_name.py -h

