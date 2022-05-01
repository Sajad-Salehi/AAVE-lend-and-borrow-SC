from re import A
from scripts.get_weth import get_weth
from brownie import accounts, interface
from web3 import Web3


def main():
    
    account = accounts.load('mywaalet')
    amount = Web3.toWei(0.1, "ether")
    erc20_address = "0xd0A1E359811322d97991E03f863a0C30C2cF029C"
    
    lending_pool = get_lending_pool()
    print(lending_pool)
    approve_erc20(amount, lending_pool, erc20_address, account)
    
    get_weth()
    print("depositing ...")
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {'from': account})
    tx.wait(2)
    print("deposited")
    
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    
    erc20_eth_price = get_asset_price()
    amount_erc20_to_borrow = (1 / erc20_eth_price) * (borrowable_eth * 0.9)
    print(f"We are going to borrow {amount_erc20_to_borrow} DAI")
    
    borrow_erc20(lending_pool, amount_erc20_to_borrow, account, erc20_address)
    

    
    dai_address = "0x04D8A950066454035B04FE5E8f851F7045F0E6B3"
    borrow_tx = lending_pool.borrow(dai_address, Web3.toWei(amount_erc20_to_borrow, "ether"), 1, 0, account.address, {"from": account})
    borrow_tx.wait(2)
    print("you borrowed some DAI.")
    get_borrowable_data(lending_pool, account)
    
    repay(amount_erc20_to_borrow, lending_pool, account)
    get_borrowable_data(lending_pool, account)

    
def get_lending_pool():
    
    lending_pool_addresses_privider = interface.ILendingPoolAddressesProvider("0x88757f2f99175387aB4C6a4b3067c77A695b0349")
    lending_pool_address = lending_pool_addresses_privider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool


def approve_erc20(amount, spender, erc20_address, account):
    
    print("Approving your Erc20 token... ")
    erc20 = interface.IERC20("0xd0A1E359811322d97991E03f863a0C30C2cF029C")
    tx = erc20.approve(spender, amount, {'from': account})
    tx.wait(2)
    print("Approved !")
    return tx


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        tlv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price():
    
    dai_eth_price_feed = interface.AggregatorV3Interface("0x22B58f1EbEDfCA50feF632bD73368b2FdA96D541")
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"The DAI/ETH price is {latest_price}")
    return float(latest_price)


def repay(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        "0x04D8A950066454035B04FE5E8f851F7045F0E6B3",
        account,
    )
    tx = lending_pool.repay(
        "0x04D8A950066454035B04FE5E8f851F7045F0E6B3",
        Web3.toWei(amount, "ether"),
        1,
        account.address,
        {"from": account},
    )
    tx.wait(2)
    print("Repaid!")

def borrow_erc20(lending_pool, amount, account, erc20_address):
    
    tx = lending_pool.borrow(
        
        erc20_address,
        Web3.toWei(amount, "ether"),
        1,
        0,
        account.address,
        {"from": account, "gasPrice": 5000},      
    )
    
    tx.wait(2)
    print(f"Congratulations! We have just borrowed {amount}")
