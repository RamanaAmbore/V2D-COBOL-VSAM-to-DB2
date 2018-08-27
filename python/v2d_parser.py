import re
import time
import v2d_utils as v2d
import v2d_regex as vdre
import sql_tmpl as stmpl
import v2d_regex as vdrg
__author__ = 'Ramana'

prg_name = 'example'

if __name__ == '__main__':
    proj = v2d.project('project')
    regex = vdrg.ret_regex()
    
    src_lines = v2d.char80(proj.fread(prg_name,"cics"))
 
    m = True
    while m:
        m = regex.search(src_lines)
        if m:
            if m.group('recgn_blk') :
                vsam_stmt = m.group('vsam_stmt')
                repl_tmpl = stmpl.sql_tmpl_dict[m.group('cmd_prm')]
                if '.' in m.group('cics_term'):               #handle period
                    term='.'
                else:
                    term=''
                    
                s = ' ' * (vsam_stmt.find('EXEC')  - 7)    
                
                repl_tmpl = repl_tmpl.format(seq='###',s=s,cols='cols',hostv='host',tbl='tbl',where='whr',term=term) 
                    
                new_upd=m.group('stmt').replace(m.group('vsam_stmt'),repl_tmpl)
                src_lines = regex.sub(new_upd,src_lines,1)
                print(m.group('stmt'))
                print(new_upd)
            else:
                print('Unrecgn block of code found: {}'.format(m.group('uncecgn_blk')))
    
    src_lines = proj.fwrite(src_lines,prg_name,"cics-out")                            


