import numpy as np
import pickle
# import pypandoc as pandoc
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

        self.counter = 0
        # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}
        self.doc = dict()


    def main(self, the_count=False):
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

                            tagsec, tagsub, tagpara = self.tag_clash(tagsec, tagsub, tagpara)
                            tag = tagsec + tagsub + tagpara

                            para_clean = []

                            # for aa in range(0, len(para)):
                            #     para_clean.append(pandoc.convert_text(para[aa], 'plain', format='latex'))
                            # para = self.clean_para(para)

                            # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}
                            self.doc[self.para_num] = [[tag], [para], self.sec_num, self.sub_num]
                            if the_count == True:
                                self.word_count(para)
                            tagpara = []

                if '\\end{document}' in line:
                    if the_count == True:
                        self.word_count([], the_count=True)
                    with open('doc_dict.pkl', 'wb') as pickle_file:
                        pickle.dump(self.doc, pickle_file)



    def build_codex(self):
        codex = []
        with open(self.file, 'r') as f:
            for line in f:
                self.codex.append(line)


    def word_count(self, para, the_count=False):
        # very simple word counter
        for line in para:
            for char in line:
                if char == ' ':
                    self.counter += 1
        if the_count == True:
            print(f'The word count for file {self.file} is {self.counter} words')

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
        ii = 0
        # check if \tag{ is at the beginning of the line

        while line[ii] == ' ' or line[ii] == '\t':
            ii += 1
        if line[ii] == '\\' and line[ii+1] == 't' and line[ii+2] == 'a' and line[ii+5] == '{':
            tagcheck = True
        return tagcheck


    def is_begin(self, line):
        begincheck = False
        ii = 0
        heading = ''

        while line[ii] == ' ' or line[ii] == '\t':
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
        check for same tags showing up more than once. Hierarchy is as follows.
        :param tagsec:
        :param tagsub:
        :param tagpara:
        :return:
        """
        # ignore empty tags in sections and subsections
        if '' in tagsec:
            tagsec.remove('')
        if '' in tagsub:
            tagsub.remove('')

        for tsub in tagsub:
            if tsub in tagsec:
                tagsub.remove(tsub)
        for tpara in tagpara:
            if tpara in tagsec:
                # tag_para = [ii for ii in tagpara if ii in tagsec]
                tagpara.remove(tpara)
            elif tpara in tagsub:
                tagpara.remove(tpara)


        return tagsec, tagsub, tagpara


    # def clean_para(self, para):
    #     """
    #     Ideally gets rid of latex word commands and inline math. IMPORTANT: commands/inline math must
    #     begin and end in the same line.
    #
    #     :param para: dirty paragraph
    #     :return: clean paragraph
    #     """
    #     clean = ''
    #     clean_line = []
    #     clean_para = []
    #
    #     for line in para:
    #
    #         char_store = [] # storage for all characters in line
    #
    #         word = [] # word in command
    #         for ii, char in enumerate(line):
    #             master_idx = []
    #
    #             if char == '\\':
    #                 jj = ii
    #                 master_idx.append(ii)
    #
    #                 while line[jj] != ' ':
    #
    #                     master_idx.append(jj)
    #                     jj += 1
    #                     if line[jj] == '{':
    #                         kk = jj
    #                         indices = []
    #                         char_store = []
    #
    #                         while line[kk+1] != '}':
    #                             char_store.append(line[kk+1])
    #                             indices.append(kk+1)
    #                             kk += 1
    #
    #                         if char_store != []:
    #                             # if we have a word in a command
    #
    #                             for ch in char_store:
    #                                 line[jj+1] = str(ch)
    #                                 jj += 1
    #     return para



    def clean_para_inception(self, para):
        level1 = []
        level2 = []
        level3 = []
        clean_char = []
        ii = 0
        for line1 in para:
            codex.append(line)

        for line2 in codex:
            for jj, char1 in enumerate(codex):
                level1.append(char1)

                if char1 == '\\':
                    char2 = ''

                    while char2 != ' ' or char2 != '\n':
                        level2.append()

                        if char2 == '{':
                            char3 == []

                            while char3 != ' ' or char3 != '\n':
                                level3.append(char3)

                                if char3 == '}':
                                    words.append(''.join(level3))



            ii += 1
    def macro_check(self, line):
        char_hold = []
        for char in line:
            char_hold.append(char)



    def inline_check(self, line):



if __name__ == '__main__':
    LTB = Label_Text_Builder('ch01_00.tex')
    LTB.main(the_count=True)
    with open('doc_dict.pkl', 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    for key, value in data.items():
        print(f'key: {key}\nvalue: {value}')
