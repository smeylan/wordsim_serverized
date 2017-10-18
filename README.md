# Word Similarity Graph Server


# Local Installation

This assumes OS X or Ubuntu and an installation of Python 2.7.x with `pip` available on the path, and `wget` available through the package manager (apt or homebrew).

Update python dependencies
```
pip install --upgrade pip
pip install virtualenv
```

To clone the repo and install requirements:
```
git clone https://github.com/smeylan/wordsim-serverized.git # clone
cd wordsim-serverized
virtualenv ws-serverized # make a virtual environemnt
source ws-serverized/bin/activate # activate the virtual environment
pip install -r requirements.txt # install dependencies
```

# Downloading lexical resources and similarity model

In the `wordsim-serverized` directory, download the lexical resources .csv from Lexicoch:

```
wget https://npki6wuti1el2a1bun7.ddns.net/s/lzqsthLEfbnVZYr/download
```

Also download the Word2Vec skipgram similarity data (.zip) from TASA:
```
wget https://npki6wuti1el2a1bun7.ddns.net/s/TC0XKnOKT0451hv/download
```
Unzip this into a folder `w2v`

# Starting the server
Once the virtual environment has been activated with `source ws-serverized/bin/activate`, then start the server with:

```
python wordsim_flask.py
```

To exit the virtualenvironment, use `deactivate`

# Sample Query  
From the command line, hit the endpoint with CURL and an appropriate json
```
curl -vX POST http://0.0.0.0:8000/api/getNclosestNodes -d @test.json --header "Content-Type: application/json"
```

CORS is enabled so asyncronous calls should be possible from (M|L)AMP-hosted javascript on the same development machine.

# Structure of the response
Response will be a plaintext JSON.

`nodes`: (numeric order corresponds to index) 
- `index`: numeric index of the node
- `word`: plaintext of word identity
- `adult_surprisal`: unigram surprisal, in bits, of the word among CHILDES adult speech
- `child_surprisal`: unigram surprisal, in bits, of the word among CHILDES child speech
- `gb12_unigram_surprisal`: unigram surprisal, in bits, under Google Books 2012 English
- `kpm_aoa_kup`: normed age of acquisition from Kuperman et al.
- `lic_frequency`: frequency in Google Books 2012
- `propuse_childes_24`: proportion of children in the sample of children in CHILDES who have used this word by 24 months 
- `query_word`: is this the query word (the center of the graph). 0 indicates false.
- `similarity`: similarity to attached source under model
- `wn_lemma`: lemma according to WordNet for this word. Generally accurate for high frequency nouns, unreliable for verbs
- `wordbank_median_aoa`: median age of acquisition among kids in Wordbank


`edges`:
- `source`: index of the source node  
- `target`: index of the target node  
- `similarity`: cosine similarity for source and target (symmetric under W2V and GLoVE)  