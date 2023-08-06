"""Typing error correction for commands using Damerau-Levenshtein distance."""

import operator
import sys

from mercurial import cmdutil, error, ui


def replace_attribute(mod_or_class):
    """Replace the function on mod_or_class the name of the decorated function."""

    def decorator(func):
        local_fname = func.__name__
        setattr(func, "orig", getattr(mod_or_class, local_fname))
        setattr(mod_or_class, local_fname, func)
        return func
    return decorator


def get_similar(name, table, accepted_distance):
    similar = set()
    for names in table.keys():
        names = cmdutil.parsealiases(names)

        for corrected in names:
            distance = damerau_levenshtein(name, corrected)
            if distance <= accepted_distance:
                similar.add((distance, corrected))
    return sorted(similar, key=operator.itemgetter(0))


@replace_attribute(cmdutil)
def findcmd(name, table, strict=True):
    # if it's not the command the user is running, go with default behaviour.
    usercmd = len(sys.argv) > 1 and sys.argv[1] or None
    if name != usercmd:
        return findcmd.orig(name, table, strict=strict)

    # try and find the command before correcting. Stops ci being converted to
    # co, for example.
    try:
        return findcmd.orig(name, table, strict=strict)
    except error.UnknownCommand as e:
        myui = ui.ui()

        distance = myui.configint('canttype', 'distance', default=1)

        similar = get_similar(name, table, distance)

        if not similar:
            raise e

        suggest = myui.configbool('canttype', 'suggest', default=False)

        if suggest or len(similar) > 1:
            similar = sorted(similar, key=operator.itemgetter(1))

            myui.status("hg: unknown command %r\n\n" % name)
            myui.status("Did you mean this?\n")

            for d, s in similar:
                myui.status("\t%s\n" % s)

            sys.exit(1)
        else:
            edit_step, corrected = similar[0]
            myui.status("Correcting %r to %r\n" % (name, corrected))
            return findcmd.orig(corrected, table, strict=strict)


def damerau_levenshtein(first_string, second_string):
    """Returns the Damerau-Levenshtein edit distance between two strings."""
    previous = None
    prev_a = None

    current = [i for i, x in enumerate(second_string, 1)] + [0]

    for a_pos, a in enumerate(first_string):
        prev_b = None
        previously_previous, previous, current = previous, current, [0] * len(second_string) + [a_pos+1]

        for b_pos, b in enumerate(second_string):
            cost = int(a != b)
            deletion = previous[b_pos] + 1
            insertion = current[b_pos-1] + 1
            substitution = previous[b_pos-1] + cost

            current[b_pos] = min(deletion, insertion, substitution)

            if prev_b and prev_a and a == prev_b and b == prev_a and a != b:
                current[b_pos] = min(current[b_pos], previously_previous[b_pos-2] + cost)

            prev_b = b
        prev_a = a
    return current[len(second_string) - 1]
