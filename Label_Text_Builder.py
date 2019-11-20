import numpy as np
import pickle
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
- pickle to save dictionary
    - need pickle to unpack as well
    
- electronics library is split into chapters
- add chapters to the dictionary
    - if multiple files given how do we handle that

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

        # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}
        self.doc = dict()


    def main(self):
        self.build_codex()
        tagsec = []
        tagsub = []
        tagpara = []
        with open(self.file, 'r') as f:
            for kk, line in enumerate(f):

                ###########################################
                ################ SECTION ##################
                if '\\section{' in line:
                    heading = self.is_begin(line) # check if \\section{ is at the beginning
                    if heading == 'sec': # confirm this is a true instance of \\section{}
                        tagsec = [] # open list for section tags
                        self.sec_num += 1 # increment section number
                        if '\\tags{' not in self.codex[kk+1]:
                            print(f'Untagged section in line {kk+2} of {self.file}')

                ###########################################
                ############### SUBSECTION ################
                elif '\\subsection{' in line:
                    heading = self.is_begin(line)
                    if heading == 'sub':
                        tagsub = []
                        self.sub_num += 1
                        if '\\tags{' not in self.codex[kk+1]:
                            print(f'Untagged subsection in line {kk+2} of {self.file}')

                ###########################################
                ################### TAG ###################

                elif '\\tags{' in line: # if \tag{ is in line
                    tagcheck = self.tag_begins_line(line)

                    if tagcheck == True:
                        if '\\section{' in self.codex[kk-1]:
                            # it it a section tag???
                            # assuming section/subsection tags are in the line directly below
                            tagsec = self.grab_tagname(line)

                        elif '\\subsection{' in self.codex[kk-1]:
                            # is it a subsection tag?
                            tagsub = self.grab_tagname(line)
                        else:
                            # assuming tags are the line right after a paragraph
                            self.para_num += 1
                            tag = [] # empty tag
                            para = []  # empty para
                            while self.codex[kk-1] != '\n': # reverse through lines until empty line
                                # grab paragraph above tag
                                para.append(self.codex[kk-1])
                                kk -= 1


                            # grab the tag name for the paragraph
                            tagpara = self.grab_tagname(line)

                            tagsub, tagpara = self.tag_clash(tagsec, tagsub, tagpara)
                            tag = tagsec + tagsub + tagpara

                            # handles duplicate tags and (bad tags not implemented!)

                            # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}
                            self.doc[self.para_num] = [[tag], [para], self.sec_num, self.sub_num]

                            tagpara = []

                if '\\end{document}' in line:
                    with open('doc_dict.pkl', 'wb') as pickle_file:
                        pickle.dump(self.doc, pickle_file)



    def build_codex(self):
        codex = []
        with open(self.file, 'r') as f:
            for line in f:
                self.codex.append(line)


    def grab_tagname(self, line):
        ii = 0
        char_pad = 0
        tagnum = 0
        tagchar = []
        tag = []
        while line[ii] != '}':
            # grab name of tags
            if ii >= 6:

                if line[ii] == ',' and line[ii + 1] != '}':
                    # if there is multiple tags
                    tag.append(''.join(tagchar))
                    tagchar = []
                    tagnum += 1
                elif line[ii] == ' ':
                    pass
                else:
                    tagchar.append(line[ii])

            ii += 1
        if tagchar == []:
            tagchar = ''
        tag.append(''.join(tagchar))
        return tag

    def tag_begins_line(self, line):
        tagcheck = False
        assert '\\tags{' in line


        # check if \tag{ is at the beginning of the line
        ii = 0
        while line[ii] == ' ' or line[ii] == '\t':
            ii += 1
        if line[ii] == '\\' and line[ii+1] == 't' and line[ii+2] == 'a' and line[ii+5] == '{':
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


    def tag_clash(self, tagsec, tagsub, tagpara):
        """
        check for tag clashes. Hierarchy is as follows.
        :param tagsec:
        :param tagsub:
        :param tagpara:
        :return:
        """

        for tsub in tagsub:
            if tsub in tagsec:
                tagsub.remove(tsub)
        for tpara in tagpara:
            if tpara in tagsec:
                # tag_para = [ii for ii in tagpara if ii in tagsec]
                tagpara.remove(tpara)
            elif tpara in tagsub:
                tagpara.remove(tpara)


        return tagsub, tagpara


    # def clean_para(self, para):
    #     for line in para:
    #         char_store = []
    #
    #         word = []
    #         for ii, char in enumerate(line):
    #             char_store.append(char)
    #             if char == '{':
    #                 # might be a word command
    #                 command = False
    #                 char_count = ii
    #                 start_idx = ii
    #                 while char_store(char_count) != ' ' or char_count != 0 or command == False:
    #                     # while characters remain constant, not the beginning of the line or a command is not detected
    #                     char_count -= 1
    #                     if char_store(char_count) == '\\':
    #                         # we know its a word command
    #                         char_want = []
    #                         command = True
    #                         char_count = start_idx+1
    #                         jj = 0
    #                         while char_store[char_count] != '}':
    #                             char_want[jj] = char_store[char_count]
    #
    #                             jj += 1
    #                             char_count += 1
    #                         word.append(''.join(char_want))
    #
    #
    #
    #
    #
    #             elif char == '$':
    #                 pass







        # for ii, tsec in enumerate(tagsec):
        #     if tsec in tagsub:
        #
        #     if tsec in tagpara:
        #
        # for ii, tsub in enumerate(tagsub):
        #     if tsub in tagpara:




    # def section_tags(self, line):
    #     tagcheck = False
    #     tagcheck = self.tag_begins_line()
    #     if tagcheck == True:





if __name__ == '__main__':
    LTB = Label_Text_Builder('ch01_00.tex')
    LTB.main()
    with open('doc_dict.pkl', 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    for key, value in data.items():
        print(f'key: {key}\nvalue: {value}')







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
