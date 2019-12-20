import numpy as np
import pickle
import re
from os import path
import psycopg2 as psy
import json

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


- definately add chapters into this dictionary
- change current value to a dictionary
    - Dictionary(keys: para #, value: dictionaries)
        - keys: tags, values: "tags"
        - keys: para, values: "paragraphs"
        - keys: section, values: section #
        - keys: subsection, values: sub #
        - keys: chapter, values: chap #
        
        
- look into python based utilities for text processing
    - regular expressions? regx?
    - allows searches and replacements based on matching strings

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
    - Need to add counting chapters and handling multiple files.
    - need to ignore lines beginning in %
    
    """




    tagcheck = False
    match = r'\tag{'
    st = ''

    tag = []
    jj = 0
    def __init__(self, *args):
        self.args = args
        self.codex = []
        self.para_num = 0
        self.sec_num = 0
        self.sub_num = 0
        self.chap_num = 0

        self.sec_tags = []
        self.sub_tags = []

        self.counter = 0
        # doc = {self.para_num: [[tags], [para], self.sec_num, self.sub_num]}

        self.master = dict()


        # need to add some sort of grand master dictionary that keeps chapters and textbook separate


    def main(self, the_count=False):
        tagsec = []
        tagsub = []
        tagpara = []
        self.codex = []

        for file in self.args:
            self.chap_num += 1
            with open(file, 'r') as f:

                self.build_codex(file)

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
                                print(f'Untagged subsection in line {kk+2} of {file}')

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
                                empty = False
                                while empty == False: # reverse through lines until empty line
                                    empty = self.slashn(self.codex[kk-1])
                                    # grab paragraph above tag
                                    if empty == True:
                                        pass
                                    elif empty == False:
                                        para.append(self.codex[kk-1])
                                        kk -= 1


                                # grab the tag name for the paragraph
                                tagpara = self.grab_tagname(line)

                                tagsec, tagsub, tagpara = self.tag_clash(tagsec, tagsub, tagpara)
                                tag = tagsec + tagsub + tagpara

                                para_clean = []

                                para_clean = self.clean_para(para)

                                # build vocab set
                                self.chapter_vocab(para_clean)


                                chapter = dict()
                                section = dict()
                                subsection = dict()
                                tag_dict = dict()
                                para_dict = dict()

                                section['section'] = self.sec_num
                                subsection['subsection'] = self.sub_num
                                chapter['chapter'] = self.chap_num
                                tag_dict['tags'] = [tag]
                                para_dict['paragraph'] = [para_clean]



                                self.master[self.para_num] = [chapter, section, subsection, tag_dict, para_dict]
                                if the_count == True:
                                    self.word_count(para)
                                tagpara = []

                    if '\\end{document}' in line:
                        self.partition()

                        if the_count == True:
                            self.word_count([], the_count=True)
                        with open('doc_dict.pkl', 'wb') as pickle_file:
                            pickle.dump(self.master, pickle_file)



    def partition(self, train=80, test=20):
        if train + test == 100:
            randomizer = dict()
            train_dict = dict()
            test_dict = dict()
            print(len(self.master))

            for key, value in self.master.items():
                if np.random.random() <= train/100:
                    train_dict[key] = value
                else:
                    test_dict[key] = value

            with open('training_dict.pkl', 'wb') as f1:
                pickle.dump(train_dict, f1)
            with open('testing_dict.pkl', 'wb') as f2:
                pickle.dump(test_dict, f2)

        else:
            print('train + test need to equal 100')


    def dump(self):
        with open('training_dict.pkl', 'rb') as f1:
            train = pickle.load(f1)
            with open('train_data.json', 'w') as f3:
                json.dump(train, f3)

        with open('testing_dict.pkl', 'rb') as f2:
            test = pickle.load(f2)
            with open('test_data', 'w') as f4:
                json.dump(test, f4)


    # def create_database(self):
    #     con = psy.connect(database="postgres", user="postgres", password="", host="127.0.0.1",
    #                       port="5432")
    #     cur = con.cursor()
    #     cur.execute('''CREATE TABLE GRAND
    #     (BOOK INT PRIMARY KEY   NOT NULL,
    #     CHAPTER INT   NOT NULL,
    #     PARANUM INT   NOT NULL,
    #     SECNUM INT   NOT NULL,
    #     SUBSECNUM INT   NOT NULL,
    #     PARA TEXT NOT NULL
    #     );''')
    #
    #
    # def add_to_database(self):
    #     con = psy.connect(database="postgres", user="postgres", password="", host="127.0.0.1",
    #                       port="5432")
    #     cur = con.cursor()
    #
    #     cur.execute("INSERT INTO GRAND (BOOK,CHAPTER,PARANUM,SECNUM,SUBSECNUM,PARA) VALUES (")














    def slashn(self, line):
        ii = 0
        while line[ii] == ' ' or line[ii] == '\t' or line[ii] == '\r' or line[ii] == '':
            ii += 1

        if line[ii] == '\n':
            return True
        elif line[ii] != '\n':
            return False



    def build_codex(self, file):
        codex = []
        with open(file, 'r') as f:
            for line in f:
                self.codex.append(line)


    def word_count(self, para, the_count=False):
        # very simple word counter
        for line in para:
            for char in line:
                if char == ' ':
                    self.counter += 1
        if the_count == True:
            print(f'The word count for file {self.args[self.chap_num - 1]} is {self.counter} words')

    def grab_tagname(self, line):
        ii = 0
        pad = 0
        tagnum = 0
        tagchar = []
        tag = []
        while line[pad] == ' ' or line[pad] == '\t':
            pad += 1
        while line[ii+pad] != '}':



            # grab name of tags
            if ii >= 6 + pad:

                if line[ii+pad] == ',' and line[ii+pad + 1] != '}':
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


    def clean_para(self, para):
        """

        :param para:
        :return:
        """
        # pattern = re.compile(r'\\[a-z]\w+\{([a-z]+)\}')
        patterns = []
        patterns.append(re.compile(r'\\[a-zA-Z]+\{([a-zA-Z]+\s?[a-zA-Z]*)\}'))

        # patterns.append(re.compile(r'\\[a-z]+\[([a-z]*)\]\{([a-z]+)\}'))
        # pattern3 = re.compile(r'\\[a-z]+\{([a-z]+)\s([a-z]+)\}')
        clean_para = []
        for line in para:
            clean_hold = []
            for pattern in patterns:
                if clean_hold == []:
                    pass
                else:
                    line = clean_hold

                clean_line = []
                start_macro = []
                end_macro = []
                start_arg = []
                end_arg = []
                macro_num = 0
                matches = re.finditer(pattern, line)

                macro_idx = [(m.start(0), m.end(0)) for m in re.finditer(pattern, line)]
                arg_idx = [(m.start(1), m.end(1)) for m in re.finditer(pattern, line)]

                for idx in macro_idx:
                    start_macro.append(idx[0])
                    end_macro.append(idx[1])

                for idx in arg_idx:
                    start_arg.append(idx[0])
                    end_arg.append(idx[1])

                ii = 0

                while macro_num < len(start_macro):
                    if ii >= start_macro[macro_num] and ii < end_macro[macro_num]:
                        if ii >= start_arg[macro_num] and ii < end_arg[macro_num]:
                            clean_line.append(line[ii])


                    elif ii != len(line) or ii != len(line) - 1:
                        clean_line.append(line[ii])

                    if ii == end_macro[macro_num]:
                        macro_num += 1

                    ii += 1

                while ii < len(line):
                    clean_line.append(line[ii])
                    ii += 1

                clean_hold = ''.join(clean_line)

            clean_para.append(''.join(clean_line))

        # clean_para = self.clean_inline(clean_para)
        return clean_para


    def chapter_vocab(self, para):
        space = False
        # need to check if a vocab file has been created yet

        if path.exists('vocab.pkl'):
            with open('vocab.pkl', 'rb') as voc:
                vocab = pickle.load(voc)
        else:
            vocab = dict()

        build_word = []
        words = []
        matches = []
        space_pat = re.compile(r'\s+')
        word_pat = re.compile(r'\w+')
        num_pat = re.compile(r'\d+')
        for line in para:
            for char in line:
                char = char.lower()
                if char == ' ' or char == '\n':
                    # if the only character in build_word is a space
                    if build_word == []:
                        break
                    elif re.findall(space_pat, build_word[0]):
                        pass
                    else:

                        if re.findall(word_pat, ''.join(build_word)):
                            hold = []
                            for c in build_word:
                                if re.match(word_pat, c):
                                    hold.append(c)
                                else:
                                    hold.append(' ')

                            build_word = hold
                        if re.findall(num_pat, ''.join(build_word)):
                            hold = []
                            for c in build_word:
                                if re.match(num_pat, c):
                                    hold.append(c)
                                else:
                                    hold.append(' ')
                            build_word = hold
                    hold = []

                    # break up multiple words
                    if ' ' in build_word:
                        space = True
                        for s in build_word:
                            if s == ' ':
                                words.append(''.join(hold))
                                hold = []
                            else:
                                hold.append(s)

                        if hold != []:
                            ''.join(hold)


                    if space == False:
                        words.append(''.join(build_word))
                    else:
                        space == False
                    build_word = []
                elif char == '\t':
                    continue
                else:
                    build_word.append(char)

        for word in words:
            if '{' in word or '}' in word:
                continue
            elif word not in vocab:
                vocab[word] = 1
            elif word in vocab:
                vocab[word] = vocab[word] + 1


        with open('vocab.pkl', 'wb') as pickle_file:
            pickle.dump(vocab, pickle_file)

        pickle_file.close()



if __name__ == '__main__':
    num_of_books = 1

    chap_dict = dict()
    book_dict = dict()

    # need to loop through all the chapters and all of the books
    LTB = Label_Text_Builder('ch01_00.tex')
    LTB.main(the_count=True)
    with open('doc_dict.pkl', 'rb') as pickle_file:
        data = pickle.load(pickle_file)
    for key, value in data.items():
        print(f'key: {key}\nvalue: {value}')

    with open('vocab.pkl', 'rb') as voc:
        vocab = pickle.load(voc)
    for key, value in vocab.items():
        print(f'word: {key}\nusage: {value}')

    pickle_file.close()
    voc.close()



