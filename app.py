import time
from web3 import Web3
from solcx import install_solc, set_solc_version, compile_source
from colorama import init, Fore
import emoji
from dotenv import load_dotenv
import os

# Load konfigurasi dan inisialisasi Colorama
load_dotenv()
init(autoreset=True)

# Versi Solidity
install_solc('0.8.0')
set_solc_version('0.8.0')

# Koneksi ke RPC OnFinality Zenchain Testnet
rpc_url = os.getenv('RPC_URL')
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Kode kontrak Solidity
contract_source_code = '''
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 storedData;

    constructor() {
        storedData = 100;
    }

    function set(uint256 x) public {
        storedData = x;
    }

    function get() public view returns (uint256) {
        return storedData;
    }
}
'''

# Fungsi untuk mendeploy kontrak pintar
def deploy_contract(account_address, private_key):
    try:
        # Compile kontrak
        compiled_sol = compile_source(contract_source_code)
        contract_interface = compiled_sol['<stdin>:SimpleStorage']

        abi = contract_interface['abi']
        bytecode = contract_interface['bin']

        # Buat instance kontrak
        SimpleStorage = web3.eth.contract(abi=abi, bytecode=bytecode)

        # Estimasi gas
        gas_estimate = SimpleStorage.constructor().estimate_gas()

        # Bangun transaksi
        transaction = SimpleStorage.constructor().build_transaction({
            'from': account_address,
            'nonce': web3.eth.get_transaction_count(account_address),
            'gas': gas_estimate,
            'gasPrice': web3.eth.gas_price
        })

        # Tanda tangan transaksi
        signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress

        print(Fore.BLUE + emoji.emojize(':check_mark_button:') +
              f' Kontrak berhasil di-deploy untuk akun {account_address} di alamat: {contract_address}')

    except Exception as e:
        print(Fore.BLUE + emoji.emojize(':cross_mark:') +
              f' Gagal deploy kontrak untuk akun {account_address}: {str(e)}')

# Fungsi untuk membaca akun dari file .env
def get_accounts():
    accounts = []
    i = 1
    while True:
        account_address = os.getenv(f'ACCOUNT_ADDRESS_{i}')
        private_key = os.getenv(f'PRIVATE_KEY_{i}')
        if not account_address or not private_key:
            break
        accounts.append((account_address, private_key))
        i += 1
    return accounts

# Loop utama untuk deploy kontrak
while True:
    if web3.is_connected():
        print(Fore.BLUE + "Memulai proses deploy kontrak ke Zenchain Testnet...")
        accounts = get_accounts()
        for account_address, private_key in accounts:
            deploy_contract(account_address, private_key)
    else:
        print(Fore.BLUE + emoji.emojize(':cross_mark:') +
              " Tidak dapat terhubung ke node RPC Zenchain Testnet.")

    time.sleep(10)  # Tunggu 10 detik sebelum mencoba lagi