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

def calc_price_impact(tokenin, pair, amount):

    token0 = pair.token0()
    first = False
    if token0 == tokenin.address:
        first = True
        print("first")

    (res0, res1, timestamp) = pair.getReserves()
    
    res0temp = res0 if first else res1
    res1 = res1 if first else res0temp
    res0 = res0temp
    amountInWithFee = amount * 0.997

    touchPrice = amountInWithFee * res1/res0  #we get price by inversing
    

    
    numerator = amountInWithFee *res1
    denominator = res0 + amountInWithFee
    realPrice = numerator/denominator

    impact = realPrice/touchPrice

    return (touchPrice, realPrice, impact)
