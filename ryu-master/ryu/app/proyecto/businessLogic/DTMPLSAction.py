'''
Created on Feb 25, 2015

@author: efviodo
'''


class DTMPLSAction(object):
    '''
    classdocs

    DTMPLSAction represent a simple MPLS ACTION like PUSH label, POP label swap label
    For action we use the following convention:
        0 -> represents PUSH action
        1 -> represents POP action
        2 -> represents SWAP action
    '''


    def __init__(self, label_a, action):
        '''
        Constructor
        '''
        
        self.label = label_a
        self.action = action
        
        
        