import re
import time
import v2d_utils as v2d
__author__='Ramana'
#%%
''' sample data for testing '''
src_lines = \
'''
000001      TRUE
000002         WHEN NORMAL
000003              MOVE ABCD-RULE TO FILTER-RULE
000003*              MOVE ABCD-RULE TO FILTER-RULE                                                  
000004              EXEC CICS READ
000005                   DATASET('ABCD-FILE'
000005*                   DATASET('ABCD-FILE')

000005                                      )
000006                   RIDFLD(ABCD-KEY)
AAAAAA                   LENGTH(length

                           of 10)
000007                   KEYLENGTH(9)
000008                   RESP(CICS-RESP)
000009              END-EXEC        .
          XXXXXXXXX
              PERFORM
000010              EVALUATE TRUE
000011                   WHEN NORMAL
000012                        CONTINUE
000013                   WHEN OTHER
000014                        SET ABCD-SW TO TRUE
000015
000016         WHEN OTHER
000017              STRING 'CICS-ERRORO' ABCD
                   'ON SIZE.'
000018
          END-PERFORM.
'''
#%%
regex_nodes = []  #indivual regex nodes/expressions
regex_blks = []

def regex_node(tpl,kwd=True,eof=False):
   '''*******************************************
      creates regular expression for each node
      *******************************************'''

   pos_frmt       = r'''(?P<{0}>(?:{1}))'''
   kwd_frmt       = r'''(?:(?:{1})\s*\(\s*(?P<{0}>\w+)\s*\))'''
   no_nm_kwd_frmt = r'''(?:(?:{1})\s*\(\s*(?:\w+)\s*\))'''
   item_frmt      = r'''(?:\s*{})'''

   var_frmt = r'''(?:LENGTH\s*OF\s*)?[-A-Z0-9$#'".]'''
   left_frmt = r'''(?:\s*.{9}^.{6}(?:[*D/].{65}.{9}^.{6})*?)*?\s'''


   (prm_nm, prm_ptrn) = tpl

   if kwd == 'None' :
       regex_nd = prm_ptrn
   elif kwd == True :
      if prm_nm =='':
         regex_nd = item_frmt.format(no_nm_kwd_frmt.format(prm_nm,prm_ptrn))
      else:
         regex_nd = item_frmt.format(kwd_frmt.format(prm_nm,prm_ptrn))
   else :
      if prm_nm =='':
         regex_nd = item_frmt.format(prm_ptrn)
      else:
         regex_nd = item_frmt.format(pos_frmt.format(prm_nm,prm_ptrn))

   if eof == 'or':
       regex_nd = regex_nd + '|'

   regex_nodes.append(regex_nd)

   if eof:
        regex_blks.append('\n'.join(regex_nodes))
        regex_nodes.clear()


   # change space to include blnaks, comments, sequence nos
   if kwd!= 'None':
      regex_nd = regex_nd.replace('\w',var_frmt)  # replace with cobol variable format
      regex_nd = regex_nd.replace('\s',left_frmt)
      regex_nd = regex_nd.replace('.*','\s*')     # workaround to prevent formatting

   return regex_nd
#%% 
def ret_regex():
    prm_dict ={}
    prm_list = []

    '''*******************************************
       returns regex for vsam statements
       *******************************************'''
    stmt_ptrn         = r'''(?P<stmt>'''
    vsam_stmt_ptrn    = r'''(?P<vsam_stmt>^(?!VSM).{6}\s+'''
    cond_beg_ptrn     = r'''(.*?(?P<cond_stmt>^.{6}\s+(?:'''
    cond_end_ptrn     = r''')(?:\s*[.])?.*?$))?'''

    cics_beg_prtn     = r'''EXEC\s+CICS'''
    cics_end_ptrn     = r'''(?:\s*(?P<cics_term>(?:(?:END-EXEC|[.])(?:.*[.])?)).*?$))'''

    if_blk_ptrn       =\
    r'''(?P<if_blk>(?:IF.*?(?:NORMAL|(?P=resp_prm)).*?(?:IF.*?(?:END-IF|[.]))*?.*?(?:END-IF|[.])))'''
    eval_blk_ptrn     =\
    r'''(?P<eval_blk>(?:EVALUATE.*?(?:NORMAL|(?P=resp_prm)).*?(?:EVALUATE.*?(?:END-EVALUATE|[.]))*?.*?(?:END-EVALUATE|[.])))'''
    if_blk_ptrn   = if_blk_ptrn.replace('.*',r'''(?:.*?['"].*["'])*.*''')
    eval_blk_ptrn = eval_blk_ptrn.replace('.*',r'''(?:.*?['"].*["'])*.*''')
    cics_beg_tpl      = ('', cics_beg_prtn)
    cmd_tpl           = ('cmd_prm',r'''DELETE|READ\b|WRITE\b|REWRITE|STARTBR|RESETBR|ENDBR|LOCK|UNLOCK''')

    prm_dict[(1,'file_prm')]      = ('FILE|FI|DATASET|DA','kwd')
    prm_dict[(2,'ridfld_prm')]    = ('RIDFLD','kwd')
    prm_dict[(3,'into_prm')]      = ('INTO','kwd')
    prm_dict[(4,'length_prm')]    = ('LENGTH','kwd')
    prm_dict[(5,'from_prm')]      = ('FROM','kwd')
    prm_dict[(6,'resp_prm')]      = ('RESP','kwd')
    prm_dict[(7,'keylength_prm')] = ('KEYLENGTH','kwd')
    prm_dict[(8,'generic_prm')]   = ('GENERIC','pos')
    prm_dict[(9,'gteq_eql_prm')]  = ('GTEQ|EQUAL','pos')
    prm_dict[(10,'update_prm')]   = ('UPDATE','pos')
    prm_dict[(11,'reqid_prm')]    = ('REQID','kwd')
    prm_dict[(12,'set_prm')]      = ('SET','kwd')
    prm_dict[(13,'nosus_prm')]    = ('NOSUSPEND','pos')
    prm_dict[(14,'sysid_prm')]    = ('SYSID','kwd')
    prm_dict[(15,'token_prm')]    = ('TOKEN','kwd')


    prm_list = list(prm_dict.items())

    blk_beg_tpl       = ('','(?:(?P<recgn_blk>(?:')
    blk_end_tpl       = ('',')*)')
    unrecgn_tpl         = ('',r'''|(?P<unrecgn_blk>.+?))''')
    cics_end_tpl      = ('',cics_end_ptrn)
    cond_end_tpl      = ('',cond_end_ptrn)
    stmt_tpl          = ('',stmt_ptrn)
    cond_beg_tpl      = ('',cond_beg_ptrn)

    if_blk_tpl        = ('',if_blk_ptrn)
    eval_blk_tpl      = ('',eval_blk_ptrn)

    vsam_stmt = regex_node(('',vsam_stmt_ptrn),'None')   +\
         regex_node(cics_beg_tpl, 'None')                 +\
         regex_node(cmd_tpl,False)                       +\
         regex_node(blk_beg_tpl,'None')

    t_eof = 'or'
    for i in prm_list:
        t_tpl = (i[0][1], i[1][0])
        if i[1][1] == 'kwd':
            t_kwd = True
        else:
            t_kwd = False

        if i == prm_list[-1]:
            t_eof = False

        vsam_stmt = vsam_stmt + regex_node(t_tpl,t_kwd,t_eof)

    vsam_stmt = vsam_stmt                                +\
           regex_node(blk_end_tpl,'None')                +\
           regex_node(unrecgn_tpl,'None')                +\
           regex_node(cics_end_tpl,False,True)

    cond_stmt = regex_node(cond_beg_tpl,'None')          +\
           regex_node(eval_blk_tpl,'None','or')          +\
           regex_node(if_blk_tpl,'None')                 +\
           regex_node(cond_end_tpl,'None',True)

    stmt = regex_node(stmt_tpl,'None')                   +\
           vsam_stmt + cond_stmt                         +\
           regex_node(('',')'),'None',True)

    print('\nRegular expression: \n',stmt)
    print('\nRegex Raw:\n\n{}'.format('\n'.join(regex_blks)))

    start = time.perf_counter()
    regex = re.compile(stmt, re.MULTILINE | re.VERBOSE | re.DOTALL | re.IGNORECASE)
    cmpl = time.perf_counter()

    print('\nRegex Compile Time {0:0.5f} '.format(cmpl-start))

    return(regex)
#%%
'''*************************************
   main logic to test regex
   *************************************'''
if __name__== "__main__":

    prg_name = 'example'

    proj = v2d.project('project')

    src_lines = proj.fread(prg_name,"cics")

    stmt = ret_regex()
    print('\nRecognized statement:\n')
    i = 0
    cmpl = time.perf_counter()
    for m in re.finditer(stmt,src_lines):
        i = i + 1
        print('\n *** Match ***', i,'\n')
        for name, n in sorted(m.re.groupindex.items(), key=lambda x: x[1]):
            if m.group(n) :
               print('\n',name, m.group(n))

    exec = time.perf_counter()
    print('\nNumber of VSAM statements: ',i)
    print('\nRegex Exec Time {0:0.5f} '.format(exec-cmpl))
