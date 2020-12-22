from collections import defaultdict
from graphviz import Digraph
from tqdm import tqdm

N = 2000


def mergeIdiomsByRule(rule, dictionary):
    '''
    For each idiom list in the given dictionary, merge all idioms failing the
    rule into one.
    '''
    for key, this_idioms in dictionary.items():
        # Collect idioms based on test result.
        failed_idioms = []
        passed_idioms = []
        for idiom in this_idioms:
            (passed_idioms if rule(idiom) else failed_idioms).append(idiom)
        # Update the entry to be the list connecting idioms extended with
        # a combined idiom.
        if len(failed_idioms) > 0:
            dictionary[key] = passed_idioms
            dictionary[key].append('\n'.join(failed_idioms))


if __name__ == "__main__":
    with open('idioms.txt', 'r') as file:
        # Remove new lines.
        idioms = map(lambda x: x.strip(), file)
        # Filter for 4-letter idioms only.
        idioms = filter(lambda x: len(x) == 4, idioms)
        # Make sure that there's not repetitions. Due to lazy evaluation, this
        # is the first time a line will be read from the file.
        idioms = set(idioms)
    # Only take the first N idioms.
    idioms = list(idioms)[:N]

    beginnings = defaultdict(list)
    endings = defaultdict(list)
    for idiom in idioms:
        beginnings[idiom[0]].append(idiom)
        endings[idiom[-1]].append(idiom)

    mergeIdiomsByRule(
        rule=lambda idiom: idiom[0] in endings, dictionary=endings)
    mergeIdiomsByRule(
        rule=lambda idiom: idiom[-1] in beginnings, dictionary=beginnings)

    num_iterations = sum(len(starting_idioms) * len(endings[key])
                         for key, starting_idioms in beginnings.items())
    g = Digraph(name='Idioms', node_attr={'shape': 'plaintext'}, strict=True)
    with tqdm(total=num_iterations, desc='Generating graph') as pbar:
        for key, starting_idioms in beginnings.items():
            for starting_idiom in starting_idioms:
                for ending_idiom in endings[key]:
                    pbar.update()
                    g.node(key, shape='circle')
                    g.edge(ending_idiom, key)
                    g.edge(key, starting_idiom)
    print('Rendering...')
    g.render()
    print('Done!')
