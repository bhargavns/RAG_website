import random

class GlossObfuscator:
    """
    Input: A percentage value representing the percentage of terms to obfuscate in each gloss.
    An obfuscated term is replaced with a question mark (?). Obfuscation is done at the morpheme level.

    The obfuscate_line method takes a line of text and returns the obfuscated version of the line.
    The obfuscate_file method reads the input file line by line, obfuscates each line, and writes the obfuscated lines to the output file.

    The input file should contain glosses in the following format:
    \g word1 word2 word3

    The output file will contain the obfuscated glosses in the same format.
    """
    def __init__(self, percentage, input_file='./sources/input.txt', obfuscation_style = "blank"):
        self.percentage = percentage
        self.all_morphemes = []
        self.input_file = input_file
        self.obfuscation_style = obfuscation_style
        with open(self.input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        content = []
        for line in lines:
            if line.startswith('\g'):
                content = line[3:].strip()  # Remove '\g ' prefix
                words = content.split()
                for word in words:
                    self.all_morphemes.extend(word.split('-'))

    def obfuscate_line(self, line):
        if line.startswith('\l'):
            return ''
        
        if not line.startswith('\g'):
            return line

        content = line[3:].strip()  # Remove '\g ' prefix
        words = content.split()
        all_terms = [term for word in words for term in word.split('-')]

        num_to_replace = int(len(all_terms) * (self.percentage / 100))
        indices_to_replace = random.sample(range(len(all_terms)), num_to_replace)

        for index in indices_to_replace:
            if(self.obfuscation_style == "blank"):
                all_terms[index] = '(?)'
            else:
                all_terms[index] = random.choice(self.all_morphemes)

        new_words = []
        term_index = 0
        for word in words:
            num_terms = len(word.split('-'))
            new_word = '-'.join(all_terms[term_index:term_index+num_terms])
            new_words.append(new_word)
            term_index += num_terms

        return '\g ' + ' '.join(new_words) + '\n'

    def obfuscate_file(self, output_file_path):
        with open(self.input_file, 'r', encoding='utf-8') as input_file:
            lines = input_file.readlines()

        obfuscated_lines = [self.obfuscate_line(line) for line in lines]

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.writelines(obfuscated_lines)

# Example usage:
# obfuscator = GlossObfuscator(50)  # 50% obfuscation
# obfuscator.obfuscate_file('input.txt', 'output.txt')