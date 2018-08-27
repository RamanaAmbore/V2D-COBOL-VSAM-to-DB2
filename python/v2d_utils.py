# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 21:03:38 2018
@author: Ramana Rao Ambore
Description: utility functions for VSAM to DB2
"""
__author__ = 'Ramana'
import yaml
import os.path
import pandas as pd

# %%
class project:
    """
    create project spedific object which is used to read or write
    data into out of files
    """

    c_path = os.path.dirname(os.getcwd())

    def __init__(self, proj_id):
        self.proj_id = proj_id

        self.proj_yml_file = os.path.join(
            project.c_path, self.proj_id, 'config', 'yml', 'config.yml')

        with open(self.proj_yml_file, 'r') as f: self.proj = yaml.load(f)

# %%
    def fpath(self, name, type=''):
        '''
        generates appropriate path for files based on type of the file
        '''
        if type == '': type = name

        if '.' not in name:
            if type in ['xref', 'template', 'regex', 'format', 'variable']:
                name = name + '.xlsx'
            else:
                name = name + '.txt'

        f_name = os.path.join(project.c_path, self.proj_id, self.proj[type], name)

        if os.path.isfile(f_name):
            print(f_name)
            return f_name
        else:
            print(f_name)
            return os.path.join(project.c_path, self.proj[type], name)

# %%
    def fread(self, name, type='', slist=False, c80=True):
        '''
        reads the files and formats them into either dataframe, list of string
        '''
        if type == '': type = name

        if type in ['xref', 'template', 'regex', 'format', 'variable']:
            df = pd.read_excel(self.fpath(name, type), sheetname=name).applymap(str)
            if type == 'xref': df = df.applmap(lambda x: x.strip())
            return df

        with open(self.fpath(name, type), 'r') as f:
            if slist:
                return f.readlines()
            else:
                return char80(f.read() if c80 else f.read())
# %%

    def fwrite(self, text, name, type, slist=False, c80=True):
        '''
        write the file
        '''
        with open(self.fpath(name, type), 'w') as f:
            if slist:
                return f.writelines(text)
            else:
                f.write(char80(text) if c80 else text)

# %%


def char80(src):
    '''
    converts every line to 80 characters
    '''
    return '\n'.join([i.ljust(80) for i in src.split('\n')])


#    return('\n'.join(src80_list))
# %%
def dequote(s):
    '''
    remove quotes
    '''
    if (s[0] == s[-1]) and s.startswith("'", '"'): return s[1:-1]


#    return('\n'.join(src80_list))
# %%
if __name__ == '__main__':
    proj = project('project')
    print(proj.fread('example', 'cics', False))
# %%
