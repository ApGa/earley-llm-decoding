from earley import EarleyParser
from grammar import Grammar, Rule, Terminal

if __name__ == '__main__':
    grammar = Grammar(
        start_symbol='Sum',
        rules= [
            Rule('Sum', ('Sum', Terminal('[+-]'), 'Product')),
            Rule('Sum', ('Product',)),
            Rule('Product', ('Product', Terminal('[*/]'), 'Factor')),
            Rule('Product', ('Factor',)),
            Rule('Factor', (Terminal(r'\('), 'Sum', Terminal(r'\)'))),
            Rule('Factor', ('Number',)),
            Rule('Number', (Terminal('[0-9]'), 'Number')),
            Rule('Number', (Terminal('[0-9]'),)),
        ]
    )
    
    parser = EarleyParser(grammar)
    
    print(parser.try_accept_tokens("1+", 'Sum'))
    print(parser.try_accept_tokens("*", 'Sum'))
    print(parser.try_accept_tokens("(2*3", 'Sum'))
    print(parser.try_accept_tokens("-4)", 'Sum'))
    
    print(parser.chart)
    