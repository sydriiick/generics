import re


class Validator:

    def __init__(self, gfile):
        reader = open(gfile, 'r', encoding='utf-8')
        content = reader.read()
        reader.close()
        content = self.clean_content(content)
        self.lines = content.split('\n')
        self.line_count = len(self.lines)
        self.itr = 0

    def clean_content(self, content):
        def remove_newlines_in_entries(match):
            return match.group(1).replace('\n', '')

        content = re.sub(r'(<entry( [^>]*?)?>[^\000]*?</entry>)', remove_newlines_in_entries, content)

        return content

    def expect_opening(self, tag):
        if self.itr < self.line_count and re.match(rf'<{tag}( [^>]*?)?>', self.lines[self.itr]):
            self.itr += 1
            return

        raise Exception(f'<{tag}> is expected; found {self.lines[self.itr]}')

    def expect_closing(self, tag):
        if self.itr < self.line_count and re.match(rf'</{tag}>', self.lines[self.itr]):
            self.itr += 1
            return

        raise Exception(f'</{tag}> is expected; found {self.lines[self.itr]}')

    def expect_header_tag(self, tag):
        result = False
        if self.itr < self.line_count and re.match(rf'<{tag}>.+', self.lines[self.itr]):
            result = True

        if not result:
            raise Exception(f'<{tag}> with content is expected; found {self.lines[self.itr]}')

        self.itr += 1

    def expect_tag(self, tag, can_be_empty=False):
        result = False

        if self.itr < self.line_count:
            tag_matcher = re.match(rf'<{tag}(?: [^>]*?)?>(.*)</{tag}>', self.lines[self.itr])

            if tag_matcher:
                result = True
                tag_content = tag_matcher.group(1)
                if tag_content.strip() == '' and not can_be_empty:
                    raise Exception(f'<{tag}> must not be empty')

        if not result:
            raise Exception(f'<{tag}>content</{tag}> is expected; found {self.lines[self.itr]}')

        self.itr += 1

    def peek(self, tag):
        if self.itr < self.line_count and self.lines[self.itr].startswith(tag):
            return True

        return False

    def validate_table(self):
        self.expect_opening('table')
        self.expect_opening('tgroup')

        while not self.peek('</tgroup>'):
            if self.peek('<thead'):
                self.expect_opening('thead')
                while not self.peek('</thead>'):
                    self.validate_table_entry()
                self.expect_closing('thead')

                self.expect_opening('tbody')
                while not self.peek('</tbody>'):
                    self.validate_table_entry()
                self.expect_closing('tbody')

            elif self.peek('<tbody'):
                self.expect_opening('tbody')
                while not self.peek('</tbody>'):
                    self.validate_table_entry()
                self.expect_closing('tbody')

            else:
                self.validate_table_entry()

        self.expect_closing('tgroup')
        self.expect_closing('table')

    def validate_table_entry(self):
        self.expect_opening('row')
        while not self.peek('</row>'):
            if self.peek('<entry'):
                self.expect_tag('entry', can_be_empty=True)
            else:
                raise Exception(f'Unexpected content; found {self.lines[self.itr]}')

        self.expect_closing('row')



    def validate_block(self, block):
        self.expect_opening(block)
        while not self.peek(f'</{block}>'):
            if self.peek('<P>'):
                self.expect_tag('P')
            elif self.peek('<XEB.p>'):
                self.expect_tag('XEB.p')
            elif self.peek('<table>'):
                self.validate_table()
            else:
                raise Exception(f'Unexpected content; found {self.lines[self.itr]}')

        self.expect_closing(block)

        return True

    def validate(self):
        try:
            self.expect_opening('HD')

            self.expect_header_tag('JN')

            self.expect_header_tag('DA')

            if self.peek('<VO>'):
                self.expect_header_tag('VO')

            if self.peek('<IS>'):
                self.expect_header_tag('IS')

            self.expect_header_tag('ID')

            self.expect_closing('HD')

            ar_count = 0

            while self.peek('<AR>'):

                self.expect_opening('AR')

                self.expect_tag('TI')

                while self.peek('<TA>'):
                    self.expect_tag('TA')

                self.expect_tag('PN')

                if self.peek('<PF>'):
                    self.expect_tag('PF')

                if self.peek('<AU>'):
                    self.expect_tag('AU')

                if self.peek('<RE>'):
                    self.expect_tag('RE')

                if self.peek('<DO>'):
                    self.expect_tag('DO')

                self.expect_tag('RP')

                if self.peek('<PD>'):
                    self.expect_tag('PD')

                aa = False
                tx = False

                if self.peek('<AA>'):
                    aa = self.validate_block('AA')

                if self.peek('<TX>'):
                    tx = self.validate_block('TX')

                if not tx and not aa:
                    return 'must contain either <TX> or <AA>'

                self.expect_closing('AR')

                ar_count += 1

            if not ar_count:
                return '<AR> is required'
        except Exception as e:
            return str(e)

        return ''
