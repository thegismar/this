from w3helpers import Etherscan

def test_get_birth_block():
    e = Etherscan()
    assert e.get_birth_block(address='0x6b175474e89094c44da98b954eedeac495271d0f') == 8950398
