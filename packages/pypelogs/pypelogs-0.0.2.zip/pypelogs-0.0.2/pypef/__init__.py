from bucket import Bucket
from each import Each
from eval import Eval
from groupby import GroupBy
from head import Head
from keep import Keep
from log import Log
from set import Set
from sort import Sort
from split import Split
from tail import Tail

CLASSES = {
    'bucket' : Bucket,
    'each' : Each,
    'eval' : Eval,
    'groupby' : GroupBy,
    'head' : Head,
    'keep' : Keep,
    'log' : Log,
    'set' : Set,
    'sort' : Sort,
    'split' : Split,
    'tail' : Tail,

}

def filter_for(s):
    spec_args = s.split(':', 1)
    clz = CLASSES.get(spec_args[0])
    if not clz:
        raise ValueError("No such filter type: %s", spec_args[0])
    return clz() if len(spec_args) == 1 else clz(spec_args[1])
