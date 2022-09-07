import re
from collections import OrderedDict

surname_prefix_pattern = "(McDonald\s|Blevins\s|af\s|Am\s|Aus\'m\s|D\'\s*|Da\s|da\s|De\s|de\s|De\sla\s|de\sla\s|de\slas\s|Del\s|del\s|Della\s|den\s|Des\s|Di\s|di\s|Dos\s|dos\s|Du\s|La\s|Las\s|Le\s|le\s|Li\s|Lo\s|op\sde\s|Ten\s|ter\s|Van\s|van\s|van\s*\'t\s|Van\sde\s|van\sden\s|Van\sder\s|van\sder\s|Ver\s|Vom\s|Von\s|von\sder\s|von\sund\szu\s|Zum\s|Zur\s)"

begin_titles = '(Adm\.|Admiral|Brig\.\s+Gen\.|Brigadier\s+General|Capt\.|Captain|Col\.|Colonel|Comdr\.|Commander|Cpl\.|Corporal|Dame|Doctor|Dr\.|Father|Fr\.|Gen\.|General|Gov\.|Governor|Judge|Lady|Lieutenant\s+Colonel|Lieutenant\s+Governor|Lieutenant|Lord|Lt\.\s+Col\.|Lt\.\s+Gov\.|Lt\.|Maj\.|Major\.\s+Gen\.|Major\s+General|Major|Mayor|Mr\.|Mrs\.|Ms\.|Prof\.|Professor|Rabbi|Rep\.|Representative|Rev\.|Reverend|Sen\.|Senator|Sir|Sister)'

end_titles = '(FAANP|GS\-C|GNP\-BC|CNP|AHC|ANP\-BC|FACHE|LPC|RPh|PharmD|MS|MBA|DNP|FNP\-BC|ENP\-C|CNE|CHSE|MSN|APRN|ACNP\-BC|D\.D\.S\.|DDS|D\.V\.M\.|DVM|Esq\.|J\.D\.|JD|M\.D\.|MD|M\.P\.|MP|R\.N\.|RN|O\.F\.M\.|OFM|O\.P\.|OP|Ph\.D|PhD|S\.J\.|SJ|U\.S\.A\.F\.\s*\(ret\.\)|USAF\s*\(ret\.\)|U\.S\.M\.C\.\s*\(ret\.\)|USMC\s*\(ret\.\)|U\.S\.N\.\s*\(ret\.\)|USN\s*\(ret\.\)|U\.S\.A\.F\.|U\.S\.M\.C\.|U\.S\.N\.|USAF|USMC|USN)'


def num2roman(num):
    roman = OrderedDict()
    roman[1000] = "M"
    roman[900] = "CM"
    roman[500] = "D"
    roman[400] = "CD"
    roman[100] = "C"
    roman[90] = "XC"
    roman[50] = "L"
    roman[40] = "XL"
    roman[10] = "X"
    roman[9] = "IX"
    roman[5] = "V"
    roman[4] = "IV"
    roman[1] = "I"

    def roman_num(num):
        for r in roman.keys():
            x, y = divmod(num, r)
            yield roman[r] * x
            num -= (r * x)
            if num <= 0:
                break

    return "".join([a for a in roman_num(num)])


def upper_repl(match):
    return match.group(1) + match.group(2).upper()


def convert_author(name):
    original = name

    name = name.lower()

    end_title_rgx = r',\s*{}\s*$'.format(end_titles)
    name = re.sub(r',\s*' + end_titles.lower() + '\s*', '', name)

    postfix = ''
    postfix_matcher = re.search(r'(,\s*((?:j|s)r\.?)\s*$)', name)
    if postfix_matcher:
        name = name.replace(postfix_matcher.group(1), '')
        postfix = postfix_matcher.group(2).title()

    inverted_matcher = re.search(r'([^,]+),\s*([^,]+)(?:,\s*(.*))?', name)
    if inverted_matcher:
        n = len(inverted_matcher.groups())
        name = inverted_matcher.group(2) + ' ' + inverted_matcher.group(1)
        if n == 4:
            name += ' ' + inverted_matcher.group(3)

    name = re.sub(r'^\s*' + begin_titles.lower() + '\s+', '', name)

    name = re.sub(r'\s+' + end_titles.lower() + '\s*$', '', name)

    if not postfix:
        postfix_matcher = re.search(r'(\b((?:s|j)r\b\.?)\s*$)', name)
        if postfix_matcher:
            name = name.replace(postfix_matcher.group(1), '')
            postfix = postfix_matcher.group(2).title()

    if not postfix:
        postfix_matcher = re.search(r'(\b(\d+)(?:st|nd|rd|th)\b)', name)
        if postfix_matcher:
            name = name.replace(postfix_matcher.group(1), '')
            postfix = num2roman(int(postfix_matcher.group(2))).upper()

    if not postfix:
        postfix_matcher = re.search(r'(\b([ixvIXV]+)\s*$)', name)
        if postfix_matcher:
            name = name.replace(postfix_matcher.group(1), '')
            postfix = postfix_matcher.group(2).upper()

    name = name.strip()
    name = re.sub(r'\s+', ' ', name)

    initials_matcher = re.search(r'([a-z]\.(?:\s+[a-z]\.)+)', name)
    if initials_matcher:
        initials = re.sub(r'\s+', '', initials_matcher.group(1))
        name = name.replace(initials_matcher.group(1), initials)

    names = name.split()

    surname_prefix = ''
    surname = ''
    surname_prefix_matcher = re.search(r'(\s' + surname_prefix_pattern.lower() + '([^\s]+)$)', name)
    if surname_prefix_matcher:
        name = name.replace(surname_prefix_matcher.group(1), '')
        surname_prefix = surname_prefix_matcher.group(2)
        surname = surname_prefix_matcher.group(3)

    if not surname_prefix:
        names = name.split()
        if len(names) > 1:
            surname = names[-1]
            name = ' '.join(names[:-1])
    else:
        surname = surname_prefix + ' ' + surname
        surname = re.sub(r'\s+', ' ', surname)
        surname = surname.strip()

    surname = re.sub(r"(-|')([a-z])", upper_repl, surname)

    result = []
    if surname:
        # append postfix to surname
        surname = surname.title()
        if postfix:
            surname = surname + ' ' + postfix
        result.append(surname)

    if name:
        name = name.title()
        # add . to middle initial if missing
        name = re.sub(r'([, ][A-Z])(\s*)$', r'\g<1>.\g<2>', name)
        result.append(name)
    else:
        return original

    return ', '.join(result)
