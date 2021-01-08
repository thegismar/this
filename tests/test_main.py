from w3helpers import Etherscan


def test_get_birth_block():
    e = Etherscan()
    assert e.get_birth_block(address='0x6b175474e89094c44da98b954eedeac495271d0f') == 8950398


def test_get_event():
    e = Etherscan()
    assert e.get_event('0x33990122638b9132ca29c723bdf037f1a891a70c',
                       '0xf63780e752c6a54a94fc52715dbc5518a3b4c3c2833d301a204226548a2a8545', 0) == 1443092926
    assert e.get_event('0x33990122638b9132ca29c723bdf037f1a891a70c',
                       '0xf63780e752c6a54a94fc52715dbc5518a3b4c3c2833d301a204226548a2a8545', -1) == 1474935644
