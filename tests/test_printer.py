import brownie
from brownie import Contract
from brownie import config
import math



def test_live(Contract, accounts, whale, wftm, GenericMasterChefStrategy, chain):
    masterchef = Contract("0x37EE3CeE5CeAf5B86Ff6bC20005d6B90F6e5549a")
    pid = 0
    emissionToken = Contract("0xea97c7c1c89d4084e0BFB88284FA90243779da9f")
    
    new_strat = Contract("0x28F2fB6730d5dbeFc4FF9eB375Bbf33BcB36e774")
    old_strat = Contract("0xeDC42841C4F98e2b1700970041888452D47f8832")
    oldas = old_strat.estimatedTotalAssets()
    strategist = accounts.at(old_strat.strategist(), force=True)

    wftm_vault = Contract(old_strat.vault())
    #t1 = old_strat.clone0xDAOStaker(wftm_vault, strategist, old_strat.rewards(), old_strat.keeper(),
    #    pid,
    #    "Printer WFTM Masterchef",
    #    emissionToken,
    #    masterchef,
    #    wftm,
    #    False, {'from': strategist})

    #strategy = GenericMasterChefStrategy.at(t1.return_value)

    #strategy = strategist.deploy(
    #    GenericMasterChefStrategy,
    #    wftm_vault,
    #    pid,
    #    "Printer WFTM Masterchef",
    #    masterchef,
    #    emissionToken,
    #    wftm,
    #    True
    #)
    new_strat.setUseSpiritOne(True, {'from': strategist})

    
    gov = accounts.at(wftm_vault.governance(), force=True)
    #wftm_vault.addStrategy(strategy, 400, 0, 2 ** 256 - 1, 1_000, {"from": gov})
    wftm_vault.migrateStrategy(old_strat, new_strat, {'from': gov})
    old_assets = wftm_vault.totalAssets()
    print(new_strat.estimatedTotalAssets())
    assert oldas == new_strat.estimatedTotalAssets()
    
    emission = Contract(new_strat.emissionToken())
    assert emission.balanceOf(new_strat) > 0
    new_strat.harvest({'from': strategist})
    strategy = new_strat
    chain.sleep(43200)
    chain.mine(1)

    #t1 = strategy.harvest({'from': strategist})
    
    token = Contract(wftm_vault.token())

    #t1 = old_strat.clone0xDAOStaker(wftm_vault, strategist, old_strat.rewards(), old_strat.keeper(),
    #    pid,
    #    "Printer WFTM Masterchef",
    #    masterchef,
    #    emissionToken,
    #    wftm,
    #    False, {'from': strategist})
    #strategy2 = GenericMasterChefStrategy.at(t1.return_value)
    #strategy2 = strategist.deploy(
    #    GenericMasterChefStrategy,
    #    wftm_vault,
    #    pid,
    #    "Printer WFTM Masterchef",
    #    masterchef,
    #    emissionToken,
    #    wftm,
    #    True
    #)
    #wftm_vault.migrateStrategy(strategy, strategy2, {'from': gov})

    #assert emissionToken.balanceOf(strategy2) > 0
    #assert strategy2.estimatedTotalAssets() == wftm_vault.strategies(strategy2).dict()["totalDebt"]
    #strategy = strategy2

    chain.sleep(1)

    new_assets = wftm_vault.totalAssets()
    # confirm we made money, or at least that we have about the same
    assert new_assets >= old_assets
    print(
        "\nOld Vault total assets after 1 harvest: ", new_assets / (10 ** token.decimals())
    )
    print(
        "\nVault total assets after 1 harvest: ", new_assets / (10 ** token.decimals())
    )


    # Display estimated APR
    print(
        "\nEstimated APR: ",
        "{:.2%}".format(
            ((new_assets - old_assets) * (365 * 2)) / (strategy.estimatedTotalAssets())
        ),
    )
    apr = ((new_assets - old_assets) * (365 * 2)) / (strategy.estimatedTotalAssets())
    assert apr > 0

    wftm_vault.updateStrategyDebtRatio(strategy, 0, {'from': gov})

    strategy.emergencyWithdraw({'from': strategist})
    assert strategy.estimatedTotalAssets() == wftm.balanceOf(strategy)
    strategy.harvest({'from': strategist})
    assert strategy.estimatedTotalAssets() == 0
    print(wftm_vault.strategies(strategy).dict())