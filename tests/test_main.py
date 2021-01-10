from w3helpers import Etherscan, Uniswap, Token


def test_get_birth_block():
    e = Etherscan()
    assert e.get_birth_block(address='0x6b175474e89094c44da98b954eedeac495271d0f') == 8950398


def test_get_pair_prices():
    u = Uniswap()
    u.get_pair_prices('0x55b0c2eee5d48af6d2a65507319d20453e9f97b6', 100, 10)


def test_get_token_info():
    h = Token.token_info('DAI')
    assert Token.token_info(h) == 'DAI'
    assert Token.token_info('DAI', True) == 18
