from copy import deepcopy


class Rule:
    def __init__(self, rule_string):
        sides = rule_string.split('->')
        self.left = sides[0]
        self.right = sides[1]

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right


# Context-free grammar
class Grammar:
    def __init__(self, rules=[], start='S', term = [], non_term=[]):
        self.rules = rules
        self.start = start
        # Add rule S' -> s
        self.rules += [Rule('#->' + start)]
        self.start = '#'
        self.s_rule = self.rules[-1]
        self.terminals = term
        self.non_terminals = non_term + ['#']

    def get_starting_rule(self):
        return self.s_rule


class Situation:
    def __init__(self, rule, dot_pos, word_pos):
        self.rule = rule
        self.dot_pos = dot_pos
        self.word_pos = word_pos
        self.completed = self.dot_pos >= len(self.rule.right)

    def get_next(self):
        if not self.completed:
            return Situation(self.rule, self.dot_pos + 1, self.word_pos)
        else:
            return deepcopy(self)

    def next(self):
        self.dot_pos += 1
        self.completed = self.dot_pos >= len(self.rule.right)

    def clone(self):
        return Situation(self.rule, self.dot_pos, self.word_pos)

    def __str__(self):
        return self.rule.left + '->' + self.rule.right + ';' + str(self.dot_pos) + ';' + str(self.word_pos)

    def __eq__(self, other):
        return self.rule == other.rule and self.dot_pos == other.dot_pos and self.word_pos == other.word_pos

    def __hash__(self):
        return hash(self.rule.left + '->' + self.rule.right + ';' + str(self.dot_pos) + ';' + str(self.word_pos))


class EarleyParser:
    def __init__(self):
        self.gr = Grammar()
        self.situation_list = []
        self.changed = []

    def fit(self, grammar):
        self.gr = grammar

    def Add(self, situation_set, situation):
        sz = len(situation_set)
        situation_set.add(situation)
        return sz != len(situation_set)

    def Scan(self, pos, word):
        if pos == 0:
            return
        for situation in self.situation_list[pos - 1]:
            if not situation.completed and situation.rule.right[situation.dot_pos] in self.gr.terminals and \
                    situation.rule.right[situation.dot_pos] == word[pos - 1]:
                self.changed[pos] |= self.Add(self.situation_list[pos], situation.get_next())

    def Complete(self, pos):
        sit_l = deepcopy(self.situation_list[pos])
        for situation in sit_l:
            if situation.completed:
                other_sit_l = deepcopy(self.situation_list[situation.word_pos])
                for other_situation in other_sit_l:
                    if not other_situation.completed and \
                            other_situation.rule.right[other_situation.dot_pos] == situation.rule.left:
                        self.changed[pos] |= self.Add(self.situation_list[pos], other_situation.get_next())

    def Predict(self, pos):
        sit_l = deepcopy(self.situation_list[pos])
        for situation in sit_l:
            if not situation.completed and \
                    situation.rule.right[situation.dot_pos] in self.gr.non_terminals:
                for rule in self.gr.rules:
                    if rule.left == situation.rule.right[situation.dot_pos]:
                        self.changed[pos] |= self.Add(self.situation_list[pos], Situation(rule, 0, pos))

    def predict(self, word):
        res = Situation(self.gr.s_rule, 0, 0)
        self.situation_list = [{res.clone()}]
        res.next()
        self.changed = [False for i in range(len(word) + 1)]
        self.changed[0] = True
        for j in range(len(word)):
            self.situation_list.append(set())
        for j in range(len(word) + 1):
            self.Scan(j, word)
            while self.changed[j]:
                self.changed[j] = False
                self.Complete(j)
                self.Predict(j)

        if res in self.situation_list[len(word)]:
            return True
        else:
            return False


if __name__ == '__main__':
    parser = EarleyParser()

    print("Введите количество нетерминальных символов: ", end='')
    N = int(input())
    print("Введите количество терминальных символов: ", end='')
    S = int(input())
    print("Введите количество правил в грамматике: ", end='')
    P = int(input())
    non_terms = []
    print("Введите нетерминальные символы:")
    for i in range(N):
        n = input()
        non_terms += [n]
    terms = []
    print("Введите терминальные символы:")
    for i in range(S):
        t = input()
        terms += [t]
    rules = []
    print("Введите правила грамматики: ")
    for i in range(P):
        r = input()
        rules += [Rule(r)]
    print("Введите стартовый символ: ")
    s = input()
    '''   
# For testing
    rls = [Rule('S->T+S'), Rule('S->T'), Rule('T->F*T'), Rule('T->F'), Rule('F->(S)'), Rule('F->a')]
    t = ['a', '(', ')', '+', '*']
    nt = ['S', 'T', 'F']
    test_grammar_1 = Grammar(rules=[Rule('S->aSbS'), Rule('S->')], start='S', term=['a', 'b'], non_term=['S'])
    test_grammar_2 = Grammar(rules=rls, start='S', term=t, non_term=nt)
#
    '''
    grammar = Grammar(rules, s, terms, non_terms)
    parser.fit(grammar)

    print("Введите количество слов: ", end='')
    m = int(input())
    for i in range(m):
        word = input()
        res = parser.predict(word)
        if res:
            print("Yes")
        else:
            print("No")
