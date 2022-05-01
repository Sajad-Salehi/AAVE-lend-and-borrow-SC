from brownie import accounts, interface


def get_weth():
    
    account = accounts.load('mywaalet')
    weth = interface.IWeth("0xd0A1E359811322d97991E03f863a0C30C2cF029C")
    tx = weth.deposit({"from": account, "value": 0.01 * 10 ** 18 })
    tx.wait(2)
    return tx
