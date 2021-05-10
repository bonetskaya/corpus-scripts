# Scripts for data processing in RCPC

`aer_metric.py` — counts aer for two alignments\
`tsv_to_pharaoh.py` — gets pharaoh alignment from tsv file\
`json_to_tokens.py` — gets tokenized sentences from json. output example:

    русский ||| 中文
`em_algorithm.py` — aligns sentences in format above\
`preprocess_sentences.py` — preprocesses sentences in format above (lemmatization, bpe).
for bpe creates `token_map.txt` to restore the alignment\
`map_align.py` — restores the alignment using pharaoh file and `token_map.txt`

### requirements
python 3.9 or higher required

### installation
    pip install -r requirements.txt

### usage
use `-h` for instructions:

    ./scpipt_name.py -h

