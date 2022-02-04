from brownie import (
    Contract,
    accounts,
    chain,
    rpc,
    web3,
    history,
    interface,
    Wei,
    ZERO_ADDRESS,
)



def rip_pair():
    return Contract('0x9ce8e9b090e8AF873e793e0b78C484076F8CEECE')
def paper_pair():
    return Contract('0x5BfFC514670263c4c0858B00E4618c729fef6c59')
def print_wftm():
    return Contract("0x28F2fB6730d5dbeFc4FF9eB375Bbf33BcB36e774")

def rip_token():
    return Contract(rip_usdc().emissionToken())

def paper_token():
    return Contract(print_wftm().emissionToken())

def rip_usdc():
    return Contract("0x2327585bc4E6E505459C61CBF9a358a3558D6600")



def rip_wftm():
    return Contract("0x2327585bc4E6E505459C61CBF9a358a3558D6600")
def rip_weth():
    return Contract("0xE635905E321e404027bC369fF7FD5Ad63C26975f")
def masterchef():
    return Contract(rip_usdc().masterchef())