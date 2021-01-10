from dotmap import DotMap
import pandas as pd
from environs import Env
from tqdm import trange
import requests
from datetime import datetime
from web3 import Web3
import matplotlib.pyplot as plt
import time


class Etherscan:
    env = Env()

    def __init__(self):
        self.key = self.env('ETHERSCAN_TOKEN')
        self.url = 'https://api.etherscan.io/api?'

    def _query(self, module, params: DotMap):

        query = f'module={module}'
        for key, value in params.items():
            query += f'&{key}={value}'

        url = f'{self.url}{query}&apikey={self.key}'

        try:
            r = requests.get(url, timeout=3)
            r.raise_for_status()
            r = r.json()
        except requests.exceptions.RequestException as err:
            return err
        except requests.exceptions.HTTPError as err:
            return err
        except requests.exceptions.ConnectionError as err:
            return err
        except requests.exceptions.Timeout as err:
            return err
        except requests.HTTPError as err:
            return err
        else:
            if r['status'] == '1':
                return r['result']

    def get_birth_block(self, address):
        module = 'account'
        params = DotMap()
        params.action = 'txlist'
        params.address = address
        params.startblock = '0'
        params.endblock = '99999999'
        params.order = 'asc'
        response = self._query(module, params)
        return int(response[0]['blockNumber'])

    def get_events(self, contract, event):
        module = 'logs'
        params = DotMap()
        first_block = self.get_birth_block(contract)
        params.action = 'getLogs'
        params.fromBlock = str(first_block)
        params.toBlock = 'latest'
        params.address = contract
        params.topic0 = event
        return self._query(module, params)

    def get_block_countdown(self, block):
        module = 'block'
        params = DotMap()
        params.action = 'getblockcountdown'
        params.blockno = block
        response = self._query(module, params)
        return response['EstimateTimeInSec']


class Uniswap:
    env = Env()

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(self.env('WEB3_HTTP_URI')))

    def get_pair_prices(self, pair, block=None, step=None):

        pair = Web3.toChecksumAddress(pair)

        with open('UniPair.json', 'r') as f:
            abi = f.read()
        pair_contract = self.w3.eth.contract(abi=abi, address=pair)

        with open('ERC20.json', 'r') as f:
            abi = f.read()

        token0_contract = self.w3.eth.contract(abi=abi, address=pair_contract.functions.token0().call())
        token1_contract = self.w3.eth.contract(abi=abi, address=pair_contract.functions.token1().call())

        token0_decimals = int(token0_contract.functions.decimals().call())
        token1_decimals = int(token1_contract.functions.decimals().call())

        if not block:
            reserves = pair_contract.functions.getReserves().call()
            reserve0 = int(reserves[0]) / 10 ** token0_decimals
            reserve1 = int(reserves[1]) / 10 ** token1_decimals
            return reserve1 / reserve0
        else:
            prices_list = []
            max_block = self.w3.eth.blockNumber
            min_block = max_block - block
            for i in trange(min_block, max_block, step):
                if i > max_block:
                    break

                b = min(i, max_block)
                reserves = pair_contract.functions.getReserves().call(block_identifier=b)
                reserve0 = int(reserves[0]) / 10 ** token0_decimals
                reserve1 = int(reserves[1]) / 10 ** token1_decimals
                date = datetime.utcfromtimestamp(float(reserves[2]))
                price = reserve1 / reserve0
                prices_list.append({'date': date, 'price': price})

            df = pd.DataFrame(prices_list)
            return df

    def plot_prices(self, pair, block, step):
        df = self.get_pair_prices(pair, block, step)
        df.plot(x='date', y='price')
        plt.show()


class Token:

    def __init__(self):
        pass

    @staticmethod
    def token_info(data, decimals=False):
        """
        :param decimals:
        :param data: either symbol (dont'care for upper/lowercase, or address (checks for starting with 0x and decides)
        :return: list of [symbol or address, decimals]
        """
        url = "https://tokens.coingecko.com/uniswap/all.json"
        r = None

        while True:
            try:
                r = requests.get(url).json()
            except requests.exceptions.Timeout:
                time.sleep(5)
                continue
            except requests.exceptions.TooManyRedirects as e:
                print(f"URL cannot be reached. {e}")
                break
            except requests.exceptions.RequestException as e:
                raise SystemExit(e)
            else:
                break

        r = pd.DataFrame(r["tokens"])

        if data.startswith("0x"):
            ret = r.loc[r["address"] == data, ["symbol", "decimals"]]
            ret.reset_index(drop=True, inplace=True)
            return ret.loc[0].symbol if decimals is False else ret.loc[0].decimals

        else:
            data = str(data).upper()
            ret = r.loc[r["symbol"] == data, ["address", "decimals"]]
            ret.reset_index(drop=True, inplace=True)
            return ret.loc[0].address if decimals is False else ret.loc[0].decimals
