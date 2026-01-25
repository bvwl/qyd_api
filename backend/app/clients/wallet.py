import aiohttp
from eth_account import Account
import asyncio
from nacl.signing import SigningKey

import base58


class WalletClient:

    # solana钱包创建
    async def solana_create(self):
        """
        solana钱包创建
        :return: private_key, public_key, address, mnemonic
        """
        signing = SigningKey.generate()
        public_key = base58.b58encode(signing.verify_key.encode()).decode('utf-8')
        private_key = base58.b58encode(signing._signing_key).decode('utf-8')
        return private_key, public_key, None

    # eth钱包创建
    async def eth_create(self):
        """
        创建一个 Ethereum 钱包
        :return: private_key, public_key, address, mnemonic
        """
        # 生成助记词
        Account.enable_unaudited_hdwallet_features()
        account, mnemonic = Account.create_with_mnemonic()
        # 获取地址
        address = account.address
        private_key = account._private_key.hex()

        # 打印相关信息
        # print("mnemonic:", mnemonic)
        # print("address:", address)
        # print("private_key:", private_key)
        #
        return private_key, address, mnemonic
