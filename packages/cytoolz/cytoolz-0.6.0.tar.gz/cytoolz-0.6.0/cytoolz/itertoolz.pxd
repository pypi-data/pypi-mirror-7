cdef class remove:
    cdef object predicate
    cdef object iter_seq


cdef class accumulate:
    cdef object binop
    cdef object iter_seq
    cdef object result


cpdef dict groupby(object func, object seq)


cdef class _merge_sorted:
    cdef list pq
    cdef object shortcut


cdef class _merge_sorted_key:
    cdef list pq
    cdef object key
    cdef object shortcut


cdef object c_merge_sorted(object seqs, object key=*)


cdef class interleave:
    cdef list iters
    cdef list newiters
    cdef tuple pass_exceptions
    cdef int i
    cdef int n


cdef class _unique_key:
    cdef object key
    cdef object iter_seq
    cdef object seen


cdef class _unique_identity:
    cdef object iter_seq
    cdef object seen


cpdef object unique(object seq, object key=*)


cpdef object isiterable(object x)


cpdef object isdistinct(object seq)


cpdef object take(int n, object seq)


cpdef object drop(int n, object seq)


cpdef object take_nth(int n, object seq)


cpdef object first(object seq)


cpdef object second(object seq)


cpdef object nth(int n, object seq)


cpdef object last(object seq)


cpdef object rest(object seq)


cpdef object get(object ind, object seq, object default=*)


cpdef object cons(object el, object seq)


cpdef object mapcat(object func, object seqs)


cdef class interpose:
    cdef object el
    cdef object iter_seq
    cdef object val
    cdef bint do_el


cpdef dict frequencies(object seq)


cpdef dict reduceby(object key, object binop, object seq, object init)


cdef class iterate:
    cdef object func
    cdef object x
    cdef object val


cdef class sliding_window:
    cdef object iterseq
    cdef tuple prev
    cdef int n


cpdef object partition(int n, object seq, object pad=*)


cdef class partition_all:
    cdef int n
    cdef object iterseq


cpdef object count(object seq)


cdef class _pluck_index:
    cdef object ind
    cdef object iterseqs


cdef class _pluck_index_default:
    cdef object ind
    cdef object iterseqs
    cdef object default


cdef class _pluck_list:
    cdef list ind
    cdef object iterseqs
    cdef int n


cdef class _pluck_list_default:
    cdef list ind
    cdef object iterseqs
    cdef object default
    cdef int n


cpdef object pluck(object ind, object seqs, object default=*)
