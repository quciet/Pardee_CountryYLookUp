import pickle
import copy
import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def IFs_map(IFs_file='IFsMapping.p'):
    '''Load the IFs concordance dictionary.'''
    with open(IFs_file, 'rb') as fp:
        IFs_mapping = pickle.load(fp)
    return IFs_mapping

def CountryColumn(data,column_names,mapping):
    '''If the state names are in the colunms.'''

    if type(column_names)==str:
        column_names=[column_names]

    mapper={}
    no_match=set()
    #matched=set()
    ifs_country=mapping.keys()
    #no_match_ifs=set(ifs_country)
    data_country=set()

    for i in column_names:
        data_country=data_country | set(data[i].str.strip().dropna())

    for j in data_country:
        if j not in ifs_country:
            mapper[j]=None
            no_match.add(j)
        else:
            mapper[j]=j
            #matched.add(j)
            #no_match_ifs.discard(j)

    #no_match_final=copy.deepcopy(no_match)
    #no_match_ifs_final=copy.deepcopy(no_match_ifs)
    #matched_final=copy.deepcopy(matched)

    for j in no_match:
        for k in ifs_country:
            if j in mapping[k]['Name']:
                mapper[j]=k
                #no_match_ifs_final.discard(k)
                #no_match_final.discard(j)
                #matched_final.add(j)

    Data_Dict={'IFs':[],'Country':[],'Match':[],'Score':[]}
    for i in mapper: 
        Data_Dict['Country'].append(i)
        if mapper[i]:
            Data_Dict['IFs'].append(mapper[i])
            Data_Dict['Match'].append("Y")
            Data_Dict['Score'].append(fuzz.ratio(i,mapper[i]))
        else:
            Data_Dict['Match'].append("N")
            picked=process.extractOne(i,ifs_country)
            Data_Dict['IFs'].append(picked[0])
            Data_Dict['Score'].append(picked[1])

    return Data_Dict
