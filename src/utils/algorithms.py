

def binary_search(seq, target, cmp_func, is_lower_bound=True):
    l = 0
    r = len(seq)-1
    while l < r-1:
        m = (l+r)/2
        cur = seq[m]
        cmp_res = cmp_func(cur, target)
        if cmp_res == -1:
            l = m+1
        elif cmp_res == 1:
            r = m-1
        elif is_lower_bound:
            r = m
        else:
            l = m
    
    if l == r:
        return l
    cmp_res = cmp_func(seq[l], target)
    if cmp_res == -1:
        return r
    elif cmp_res == 1:
        return -1
    elif is_lower_bound:
        return l
    cmp_res = cmp_func(seq[r], target)
    if cmp_res == -1:
        return len(seq)
    else:
        return r