from pygears.typing import Integer, Tuple, Queue, Int, typeof, Uint
from pygears import gear, alternative
from pygears.common import ccat, fmap, cart, permuted_apply
from pygears import module
from pygears.util.utils import quiter

TCfg = Tuple[{
    'start': Integer['w_start'],
    'cnt': Integer['w_cnt'],
    'incr': Integer['w_incr']
}]


def rng_out_type(cfg, cnt_steps):
    if cnt_steps:
        return cfg[0] + cfg[1] + cfg[2]
    else:
        return max(cfg[0], cfg[1])


@gear(svgen={'svmod_fn': 'rng_w_rst.sv'})
async def sv_rng_w_rst(
        cfg: TCfg,
        rst_in: Uint[1],
        *,
        signed=b'typeof(cfg[0], Int)',
        cnt_one_more=False,
        cnt_steps=False,
        incr_steps=False) -> Queue['rng_out_type(cfg, cnt_steps)']:
    def sign(x):
        return -1 if x < 0 else 1

    async with cfg as (start, cnt, incr):

        if not cnt_steps:
            rng_cfg = [int(start), int(cnt), int(incr)]
        else:
            rng_cfg = [
                int(start),
                int(start) + int(cnt) * int(incr),
                int(incr)
            ]

        rng_cfg[1] += sign(int(incr)) * cnt_one_more

        for data, last in quiter(range(*rng_cfg)):
            yield module().tout((data, last))


@gear
def rng_w_rst(cfg: TCfg,
              rst_in: Uint[1],
              *,
              cnt_steps=False,
              incr_steps=False,
              cnt_one_more=False):

    any_signed = any([typeof(d, Int) for d in cfg.dtype])
    all_signed = all([typeof(d, Int) for d in cfg.dtype])
    if any_signed and not all_signed:
        cfg = cfg | fmap(f=(Int, ) * len(cfg.dtype))

    return cfg | sv_rng_w_rst(
        rst_in=rst_in,
        signed=any_signed,
        cnt_steps=cnt_steps,
        incr_steps=incr_steps,
        cnt_one_more=cnt_one_more)
