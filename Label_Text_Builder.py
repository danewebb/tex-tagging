import numpy as np

"""
QUESTIONS
- non alpha-numeric text (delete/ignore/clean)
    - \\emph{}, \\textit{}, \\keyword{}?
    - tables, figures
    - references
    
    
    answers
    - pandoc: can do conversions between latex and markdown or html or whatever
        - could run everything through it
    - could check if anyone has built some latex filtering 
    
    
- Tagging every paragraph
    - if not how do we discern between a new paragraph
        - if we don't require tags for a paragraph how do we discern between figs, tables, etc.? maybe search for 
            \\begin{ and \\end{
            
    answers
    - most paragraph should have tags, don't forget section and subsection level tags
    - after block is there a tag command
        - we are going to require a tag on every paragraph
    
    
- Why don't we just sequentially number paragraphs
    - other than use hashes
        - if we do use hashes how do we recall that hash?
        
        
    answers
    - sequential is fine

"""



"""
NOTES

"""
class Label_Text_Builder():
    """
    ###################################################################################################################
    #############################################   Requires .tex file   ##############################################
    ###################################################################################################################

    Grabs paragraphs and its associated tags, sections, subsections, and paragraph numbers. Places all of these into
    a dictionary.

    This is built to mine a corpus constructed by Dr. Rico A.R. Picone that was tagged by Dr. Rico A.R. Picone and
    Dane Webb during the 2019-2020 academic year at Saint Martin's University.

    """


    """
    #########################################   DEV NOTES   ###########################################################
    - Have named sections, I think we only care about the names of the tags
    
    
    """
    # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}
    doc = dict()



    tagcheck = False
    match = r'\tag{'
    st = ''

    tag = []
    jj = 0
    def __init__(self, file):
        self.file = file
        self.codex = []
        self.para_num = 0
        self.sec_num = 0
        self.sub_num = 0

        self.sec_tags = []
        self.sub_tags = []


    def main(self):
        self.build_codex()

        with open(self.file, 'r') as f:
            for kk, line in enumerate(f):
                ###########################################
                ################ SECTION ##################
                if '\\section{' in line:
                    heading = self.is_begin(line)
                    if heading == 'sec':
                        self.sec_num += 1

                    # add section key
                ###########################################
                ############### SUBSECTION ################
                elif '\\subsection{' in line:
                    heading = self.is_begin(line)
                    if heading == 'sub':
                        self.sub_num += 1

                ###########################################
                ################### TAG ###################

                elif '\\tag{' in line: # if \tag{ is in line
                    tagcheck = self.tag_begins_line(line)

                    if tagcheck == True:
                        self.para_num += 1
                        tag = []
                        para = []  # empty para
                        while self.codex[kk] != '\n': # reverse through lines until empty line
                            # grab paragraph above tag
                            para.append(self.codex[kk])
                            kk -= 1
                        tag = self.grab_tagname(line)

                        # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}
                        doc[str(self.para_num)] = [[tag], [para], self.sec_num, self.sub_num]



    def build_codex(self):
        codex = []
        with open(self.file, 'r') as f:
            for line in f:
                self.codex.append(line)


    def grab_tagname(self, line):
        ii = 0
        tagnum = 0
        tagchar = []
        tag = []
        while line[ii] != '}':
            # grab name of tags
            if ii >= 5:
                if line[ii] == ',' and line[ii + 1] != '}':
                    # if there is multiple tags
                    tag[tagnum] = ''.join(tagchar)
                    tagchar = []
                    tagnum += 1

                tagchar.append(line[ii])

            ii += 1
        tag[tagnum] = ''.join(tagchar)
        return tag

    def tag_begins_line(self, line):
        tagcheck = False
        assert '\\tag{' in line


        # check if \tag{ is at the beginning of the line
        ii = 0
        while line[ii] == ' ' or line[ii] == '\t':
            ii += 1
        if line[ii] == '\\' and line[ii+1] == 't' and line[ii+2] == 'a' and line[ii+4] == '{':
            tagcheck = True
        return tagcheck


    def is_begin(self, line):
        begincheck = False
        ii = 0
        heading = ''
        while line[ii] == ' ' or line[ii] == '\\t':
            ii += 1
        if '\\subsection{' in line:
            if line[ii+3] == 'b' and line[ii+4] == 's' and line[ii+5] == 'e':
                # subsection
                # if heading == 'sub':
                    # section remains the same
                heading = 'sub'
                return heading

        elif '\\section{' in line:
            if line[ii+2] == 'e' and line[ii+3] == 'c' and line[ii+4] == 't':
                # section
                heading = 'sec'
                return heading


    def section_tags(self, line):
        tagcheck = False
        tagcheck = self.tag_begins_line()
        if tagcheck == True:




if __name__ == '__main__':
    LTB = Label_Text_Builder('report.tex')
    LTB.main()








    # def grab_name(self, line, heading):
    #     ii = 0
    #     char = []
    #     word = []
    #     wordnum = 0
    #     while line[ii] == ' ' or line[ii] == '\\t':
    #         ii += 1
    #
    #     if heading == 'sec':
    #         ii += len('\\section{')
    #     elif heading == 'sub':
    #         ii += len('\\subsection{')
    #     else:
    #         raise AssertionError
    #
    #     while line[ii] != '}':
    #         char.append(line(ii))
    #
    #
    #     return ''.join(char)