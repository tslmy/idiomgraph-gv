"""IdiomGraph-gv: Draw a graph of Chinese four-character idioms.

Usage:
  main.py (-h | --help)
  main.py --version
  main.py generate [--limit_num_idioms=<n>] [--limit_char_nodes=<c>] [--limit_num_idioms_each_node=<e>]

Options:
  -h --help                         Show this screen.
  --version                         Show version.
  --limit_num_idioms=<n>            Max number of idioms to consider [default: 2000]. Disable sub-sampling by setting this with a non-positive value.
  --limit_char_nodes=<c>            Only use the top X frequently used character-nodes [default: -1].
  --limit_num_idioms_each_node=<e>  Max number of idioms to display at each idiom-node [default: 10].

"""
from docopt import docopt
from collections import defaultdict
from graphviz import Digraph
from tqdm import tqdm
from random import sample


def mergeIdiomsByRule(rule, dictionary, limit=10):
    '''
    For each idiom list in the given dictionary, merge all idioms failing the
    rule into one.
    Nodes with more than `limit` failed idioms will be truncated.
    '''
    for key, this_idioms in dictionary.items():
        # Collect idioms based on test result.
        failed_idioms = []
        passed_idioms = []
        for idiom in this_idioms:
            (passed_idioms if rule(idiom) else failed_idioms).append(idiom)
        # Update the entry to be the list connecting idioms extended with
        # a combined idiom.
        if len(failed_idioms) == 0:
            # No idioms failed the test; early return.
            continue
        # else:
        # Truncate the node of the failed idioms, if too many:
        if limit > 0 and len(failed_idioms) > limit:
            num_truncated = len(failed_idioms) - limit
            failed_idioms = failed_idioms[:limit]
            failed_idioms.append(f'（余下 {num_truncated} 个）')
        failed_idioms_as_one = '\n'.join(failed_idioms)
        dictionary[key] = passed_idioms
        dictionary[key].append(failed_idioms_as_one)


def truncateDictForTopLen(dictionary, n=7):
    '''
    Notice that this does not work in-place.
    Adopted from https://stackoverflow.com/a/613218/1147061.
    '''
    s = sorted(dictionary.items(), key=lambda item: -len(item[1]))
    # Only take the first n items.
    s = s[:n]
    return defaultdict(list, s)


if __name__ == "__main__":
    arguments = docopt(__doc__, version='IdiomGraph-gv 1.0')
    with open('idioms.txt', 'r') as file:
        # Remove new lines.
        idioms = map(lambda x: x.strip(), file)
        # Filter for 4-letter idioms only.
        idioms = filter(lambda x: len(x) == 4, idioms)
        # Make sure that there's not repetitions. Due to lazy evaluation, this
        # is the first time a line will be read from the file.
        idioms = list(set(idioms))

    print(f'A total of {len(idioms)} idioms are loaded.')
    n = int(arguments['--limit_num_idioms'])
    if n > 0:
        idioms = sample(idioms, n)
        print(f'A total of {len(idioms)} idioms are sampled.')

    # Build dictionaries from first (last) characters to list of idioms that
    # start (end) with them.
    beginnings = defaultdict(list)
    endings = defaultdict(list)
    for idiom in idioms:
        beginnings[idiom[0]].append(idiom)
        endings[idiom[-1]].append(idiom)

    mergeIdiomsByRule(
        rule=lambda idiom: idiom[0] in endings,
        dictionary=endings,
        limit=int(arguments['--limit_num_idioms_each_node']),
    )
    mergeIdiomsByRule(
        rule=lambda idiom: idiom[-1] in beginnings,
        dictionary=beginnings,
        limit=int(arguments['--limit_num_idioms_each_node']),
    )
    print(f'A total of {len(beginnings)} first-characters are processed.')
    print(f'A total of {len(endings)} forth-characters are processed.')

    if int(arguments['--limit_char_nodes']) > 0:
        beginnings = truncateDictForTopLen(beginnings)
        endings = truncateDictForTopLen(endings)
        print(f'A total of {len(beginnings)} first-characters remained.')
        print(f'A total of {len(endings)} forth-characters remained.')

    # Estimate iterations needed.
    num_iterations = sum(len(starting_idioms) * len(endings[key])
                         for key, starting_idioms in beginnings.items())
    # Create the graph.
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
