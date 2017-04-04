'''Print Yukon NTS tile names as html table with links, arranged in same order as they appear in a map index.

2015-Aug-19, Matt.Wilkie@gov.yk.ca
License: X/MIT
'''

nts_txt_ordered = '''117C  117D
117B  117A
116NO 116P
116JK 116I 106L 106K
116FG 116H 106E 106F
116BC 116A 106D 106C 106B
115NO 115P 105M 105N 105O 105P
115JK 115I 105L 105K 105J 105I
115FG 115H 105E 105F 105G 105H 095E
115BC 115A 105D 105C 105B 105A 095D 095C
'''

style = '''<style type="text/css">
.ntsgrid {color:#333333;width:auto;border-width: 1px;border-color: #6D92A8;border-collapse: collapse;}
.ntsgrid tr {background-color:#f9fafb;}
.ntsgrid td {border-width: 1px;padding: 0.7em 0.5em;border-style: solid;
    border-color: #6D92A8;
    text-align:center;}
.ntsgrid td:hover {background-color:#FDECC5;}
.ntsgrid a {text-decoration:none}
</style>'''

def link(txt, prefix=None):
    return '<a href="{prefix}{txt}">{txt}</a>'.format(prefix=prefix, txt=txt)


if __name__ == '__main__':
    print style
    print '<table class="ntsgrid">'
    for row in nts_txt_ordered.splitlines():
        print '<tr>'
        for x in row.split():
##            prefix = '/maps/media/uploads/pdf-maps/Administrative_Boundaries_'
            prefix = 'xxx/'
            print '<td>',link(x, prefix),'</td>'
        print '</tr>'
    print '</table>'

