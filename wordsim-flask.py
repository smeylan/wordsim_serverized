from flask import Flask, jsonify, render_template, request
import time
import os
import gensim
import pandas as pd 
import numpy as np
import pdb
from flask_cors import CORS

# HTTP API
app = Flask(__name__)
CORS(app)
#app.debug = True

parameters = {}
parameters['getNclosestNodes'] = {
    'word':'specifying the word to retrieve similar words',
    'nsim': 'specifying the number of nodes to return',
    'adult_surprisal_filter': 'specifying the minimum unigram surprisal in adult language to allow in the analysis',
    'child_surprisal_filter':'specifying the minimum unigram surprisal in child language to allow in the analysis',    
    'nretrieve': 'specifying the top n nodes to retrieve for any given word'
    }


#load lexical resources, cull useless stuff (keep median aoa, etc.)
lexiconch = pd.read_csv('lexiconch.csv', encoding='utf-8')[['word','lic_frequency','childes_parentUnigramSurprisal','childes_childUnigramSurprisal','wordbank_median_aoa','kpm_aoa_kup','propuse_childes_24','wn_lemma']]
lexiconch['gb12_unigram_surprisal'] = -1 * np.log2(lexiconch['lic_frequency'] / np.sum(lexiconch['lic_frequency']))
#lexiconch = lexiconch.loc[(lexiconch['childes_parentUnigramSurprisal'] < 20) | (lexiconch['childes_childUnigramSurprisal'] < 20) | (lexiconch['gb12_unigram_surprisal'] < 25 )]
lexiconch['adult_surprisal'] = lexiconch['childes_parentUnigramSurprisal']
lexiconch['child_surprisal'] = lexiconch['childes_childUnigramSurprisal']



# Lexiconch can also be addressed as a database
#load W2V
w2v = gensim.models.Word2Vec.load('w2v/model')

def getNclosestForWord(node_index, retrieve_n, adult_surprisal_filter,  child_surprisal_filter, nodes, edges):
    word = nodes[node_index]['word']
    lemma = nodes[node_index]['wn_lemma']
    most_similar = pd.DataFrame(w2v.most_similar(positive=[word], topn=50))
    most_similar.columns = ['word','similarity']

    #merge in the metadata    
    words_df = most_similar.merge(lexiconch)
    
    # remove anything with the same lemma as the seed word
    words_df = words_df.loc[words_df.wn_lemma != lemma] 

    #filter
    words_df = words_df.loc[(words_df.adult_surprisal <= adult_surprisal_filter) &  (words_df.child_surprisal <= child_surprisal_filter)]
    
    #sort
    words_df = words_df.sort_values(by=['adult_surprisal'])

    #take the top n
    words_df = words_df.iloc[0:retrieve_n]

    #map everthing to its lemma. This means filtering was done with specific forms, but then we choose the lemmas
    lemmas_df = words_df[['word','similarity']].merge(lexiconch)
    words_df = lemmas_df
    
    if words_df.shape[0] > 0:
        most_similar_words = words_df.to_dict(orient='records')

        for similar_word in most_similar_words:
            if similar_word['word'] in [x['word'] for x in nodes]:
                # node is already present
                target_index = np.where([x['word'] == similar_word['word'] for x in nodes])[0][0]            
            else:
                #node is new
                nodes.append(similar_word)                
                target_index = np.where([x['word'] == similar_word['word'] for x in nodes])[0][0]
                nodes[target_index]['query_word'] = 0
                nodes[target_index]['index'] = target_index

            # after checking for redundancy, add edges
            if all([(x['target'] != node_index) & (x['source'] != target_index) for x in edges]):
                edges.append({'source':node_index, 'target': target_index, 'similarity':nodes[target_index]['similarity']})    

    return(nodes,edges)

def getMetadataForWord(word):
    words_df = lexiconch.loc[lexiconch.word == word]
    return(words_df.to_dict(orient='records')[0])

@app.route('/api/getNclosestNodes', methods=['POST'])
def getNclosestNodes(): #word, nsim, adult_surprisal_filter,  child_surprisal_filter
    json = request.get_json()
    
    for key, value in parameters['getNclosestNodes'].iteritems():
        if not key in json:       
            return(jsonify({'error':'/api/getNclosestNodes requires a json with a `'+key+'` key '+value}))

    edges = []
    nodes = []    
    #get the target word represented as a node
    nodes.append(getMetadataForWord(json['word']))      
    nodes[0]['query_word'] = 1
    nodes[0]['index'] = 0

    node_index = -1
    while len(nodes) <= json['nsim']:        
        node_index += 1
        nodes, edges = getNclosestForWord(node_index, json['nretrieve'], json['adult_surprisal_filter'],  json['child_surprisal_filter'], nodes, edges)
    #!!! as of 10/17, this is a simplification that puts downstream words on a queue using the node list, when we should evaluate all nodes within a diameter and take the top n        
    return jsonify({'nodes':nodes,'edges':edges})

@app.route('/')
def main():
    return "flask is running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)    