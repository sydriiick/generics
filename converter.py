from bs4 import BeautifulSoup
import directories as DIR
import roman
import re
import os


class Converter:

    def __init__(self, conv_path, encoding):
        self.conv_path = conv_path
        self.encoding = encoding

    def init_variables(self):
        self.article_count = 0
        self.green_name = ''
        self.green_zip = ''
        self.mcode = ''
        self.err_log = ''
        self.has_error = False
        self.output = ''
        self.replacement = 'N'

    def set_bsoup_object(self):
        try:
            self.content = ''
            with open(self.combined_file, 'r', encoding=self.encoding) as reader:
                self.content = reader.read()

            self.clean_content()

            self.root = BeautifulSoup(self.content, 'html.parser')
        except Exception as e:
            raise Exception(str(e) + '\n')

    def check_error(self):
        if self.err_log:
            self.has_error = True

    def write_output(self):
        with open(f'{self.conv_path}{DIR.OUTPUT}{self.green_name}', 'w', encoding=self.encoding) as writer:
            writer.write(self.output)

        self.check_error()

        if self.has_error:
            with open(f'{self.conv_path}{DIR.ERROR}{self.green_name}.error', 'w', encoding=self.encoding) as writer:
                writer.write(self.err_log)

    def convert_non_ascii_to_dcodes(self):
        non_ascii_chars = set()
        for char in self.output:
            if ord(char) > 127:
                non_ascii_chars.add(char)

        for na_char in non_ascii_chars:
            dcode = '&#' + str(ord(na_char)) + ';'
            if dcode == '&#160;':
                self.output = self.output.replace(na_char, '')
            else:
                self.output = self.output.replace(na_char, dcode)

    def set_output_name(self, year, month, day):
        self.green_name = f'{self.mcode}{month}{day}.{year[-2:]}'
        self.green_zip = f'{self.mcode}_{year}{month}{day}.zip'

        self.check_replacement()

    def generate_footer(self):
        self.output += f'<TR>\n<NR>{str(self.article_count)}\n</TR>\n'

    def clean_content(self):
        pass

    def load_imagelist(self):
        imagelist = f'{self.conv_path}{DIR.IMAGE}{os.path.basename(self.combined_file)}.imagelist'
        try:
            with open(imagelist, 'r', encoding='utf-8') as reader:
                return set(reader.read().split('\n'))
        except Exception:
            raise 'unable to load imagelist\n'

        return set()

    def check_replacement(self):
        if self.replacement == 'Y':
            self.green_name += 'R'
            self.green_zip = self.green_zip.replace('.zip', 'R.zip')

    def normalize_space(self, content):
        return self.remove_multi_spaces(content).strip()

    def remove_multi_spaces(self, content):
        content = content.replace(chr(8203), '')
        content = self.remove_space_before_puncs(content)
        return re.sub(r'\s+', ' ', content)

    def remove_space_before_puncs(self, content):
        return re.sub(r'\s+([\?\.\!\,\:\;])', r'\g<1>', content)

    def get_node(self, parent_node, node_name, attr=None):
        if attr:
            return parent_node.find(node_name, attr)
        else:
            return parent_node.find(node_name)

    def get_nodes(self, parent_node, node_name, attr=None):
        if attr:
            return parent_node.find_all(node_name, attr)
        else:
            return parent_node.find_all(node_name)

    def get_node_content(self, parent_node, node_name, attr=None):
        node = self.get_node(parent_node, node_name, attr)

        if not node:
            return ''

        node_content = self.normalize_space(node.text)

        return node_content

    def get_attr_value(self, node, attr_name):
        if node and node.has_attr(attr_name):
            return self.normalize_space(node[attr_name])

        return ''

    def create_output_node(self, output_node, content, has_pre_newline):
        if has_pre_newline:
            return f'<{output_node}>\n{content}</{output_node}>\n'
        else:
            return f'<{output_node}>{content}</{output_node}>\n'

    def create_output_header_node(self, output_node, content):
        return f'<{output_node}>{content}\n'

    def create_multi_nodes(self, parent_node, source_node, output_node, attr=None, transform=None,
                           has_pre_newline=False):
        elems = self.get_nodes(parent_node, source_node, attr)
        result = ''

        for elem in elems:
            if transform:
                elem_content = self.normalize_space(transform(elem.text))
            else:
                elem_content = self.normalize_space(elem.text)

            if elem_content:
                result += self.create_output_node(output_node, elem_content, has_pre_newline)

        return result

    def create_simple_node(self, parent_node, source_node, output_node, attr=None, transform=None,
                           has_pre_newline=False):
        node_content = self.get_node_content(parent_node, source_node, attr)

        if transform:
            node_content = transform(node_content)

        if not node_content:
            return ''

        return self.create_output_node(output_node, node_content, has_pre_newline)

    def create_node(self, output_node, content, has_pre_newline=False):
        if not content:
            return ''

        return self.create_output_node(output_node, content, has_pre_newline)

    def create_simple_header_node(self, parent_node, source_node, output_node, attr=None, transform=None):
        node_content = self.get_node_content(parent_node, source_node, attr)

        if transform:
            node_content = transform(node_content)

        if not node_content:
            return ''

        return self.create_output_header_node(output_node, node_content)

    def create_header_node(self, output_node, content):
        if not content:
            return ''

        return self.create_output_header_node(output_node, content)

    def create_link_node(self, node, link_attr, link_allowed=True, content_attr=''):
        node_content = self.normalize_space(node.text)
        link = ''

        if node.has_attr(link_attr):
            link = self.normalize_space(node[link_attr])

        if content_attr:
            node_content = self.get_attr_value(node, content_attr)

        if not node_content:
            node_content = link

        if not link:
            return False, ''

        if (link.startswith('http') or link.startswith('www')) and link_allowed:
            return True, self.create_link_output(node_content, link)

        return False, f' ({link}) {node_content} '

    def create_link_output(self, label, link):
        if label and link:
            return f'<XEB.a href="{link}" style="external">{label}</XEB.a>'

        return ''

    def wrap_para(self, has_link, content, prefix=''):
        content = self.normalize_space(content)
        if has_link and content:
            return f'<XEB.p>{prefix}{content}</XEB.p>\n'
        elif content:
            return f'<P>{prefix}{content}</P>\n'

        return ''

    def wrap_sscript(self, content, script_type, in_body=True):
        if in_body:
            return f'<{script_type}>{content}</{script_type}>'
        else:
            return f'[{script_type}.{content}]'

    def create_entry_tag(self, node, content, colspan_attr='', rowspan_attr='', align_attr='align', valign_attr='valign'):
        attribs = []
        att_values = {'right', 'left', 'center', 'top', 'bottom'}

        if node.has_attr(colspan_attr):
            attribs.append('namest="1"')
            colspan = self.normalize_space(node[colspan_attr])
            attribs.append(f'nameend="{colspan}"')

        if node.has_attr(rowspan_attr):
            rowspan = self.normalize_space(node[rowspan_attr])
            attribs.append(f'morerows="{str(int(rowspan) - 1)}"')

        if node.has_attr(align_attr):
            if node[align_attr] in att_values:
                align = self.normalize_space(node[align_attr])
                attribs.append(f'align="{align}"')

        if node.has_attr(valign_attr):
            if node[valign_attr] in att_values:
                valign = self.normalize_space(node[valign_attr])
                attribs.append(f'valign="{valign}"')

        if len(attribs):
            entry_attribs = ' '.join(attribs)
            return f'<entry {entry_attribs}>{content}</entry>\n'
        else:
            return f'<entry>{content}</entry>\n'

    def wrap_table(self, content):
        return f'<table>\n<tgroup cols="1">\n{content}</tgroup>\n</table>\n'

    def generate_list_prefix(self, n, list_type):
        '''
        * list types are 'unordered', 'ordered', 'alpha-lower', 'alpha-upper', 'roman-lower',  and 'roman-upper'

        * default type is 'unordered'; any other type is also considered as 'unordered'
        '''
        if list_type == 'ordered':
            for x in range(1, n + 1):
                yield str(x) + '.'
        elif list_type == 'alpha-lower':
            for x in range(97, 97 + n + 1):
                yield chr(x) + '.'
        elif list_type == 'alpha-upper':
            for x in range(65, 65 + n + 1):
                yield chr(x) + '.'
        elif list_type == 'roman-lower':
            for x in range(1, n + 1):
                yield roman.toRoman(x).lower() + '.'
        elif list_type == 'roman-upper':
            for x in range(1, n + 1):
                yield roman.toRoman(x) + '.'
        else:
            for _ in range(n):
                yield '*'
