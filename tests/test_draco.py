import brownie
from brownie import Contract
from brownie import config
import math



def test_live(Contract, accounts, whale, wftm, GenericMasterChefStrategy, chain):
    wftm = Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83")
    masterchef = Contract("0xB5cd7B1fD153c6FBf6F5219721a296Fc2b69f2F5")
    pid = 0
    emissionToken = Contract("0x37863ea4bf6ef836bC8bE909221BAF09A2aF43d7")
    
    #new_strat = Contract("0x28F2fB6730d5dbeFc4FF9eB375Bbf33BcB36e774")
    old_strat = Contract("0x28F2fB6730d5dbeFc4FF9eB375Bbf33BcB36e774")
    oldas = old_strat.estimatedTotalAssets()
    strategist = accounts.at(old_strat.strategist(), force=True)

    wftm_vault = Contract("0x0DEC85e74A92c52b7F708c4B10207D9560CEFaf0")
    #t1 = old_strat.clone0xDAOStaker(wftm_vault, strategist, old_strat.rewards(), old_strat.keeper(),
    #    pid,
    #    "Draco WFTM Masterchef",
    #    masterchef,
    #    emissionToken,
    #    wftm,
    #    True, {'from': strategist})

    #strategy = GenericMasterChefStrategy.at(t1.return_value)
    strategy = GenericMasterChefStrategy.at("0x4cF620a388d36Fb527ddc03a515b8677c14A967a")

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
    #new_strat.setUseSpiritOne(True, {'from': strategist})

    
    gov = accounts.at(wftm_vault.governance(), force=True)
    #wftm_vault.addStrategy(strategy, 100, 0, 2 ** 256 - 1, 1_000, {"from": gov})
    #wftm_vault.migrateStrategy(old_strat, new_strat, {'from': gov})
    old_assets = wftm_vault.totalAssets()
    #print(new_strat.estimatedTotalAssets())
    #assert oldas == new_strat.estimatedTotalAssets()
    
    #emission = Contract(new_strat.emissionToken())
    #assert emission.balanceOf(new_strat) > 0
    strategy.harvest({'from': gov})
    strategy.setAutoSell(True, {'from': gov})
    chain.sleep(43200)
    chain.mine(1)

    #t1 = strategy.harvest({'from': strategist})
    strategy.harvest({'from': gov})
    
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

    strategy.emergencyWithdraw({'from': gov})
    assert strategy.estimatedTotalAssets() == wftm.balanceOf(strategy)
    strategy.harvest({'from': gov})
    assert strategy.estimatedTotalAssets() == 0
    print(wftm_vault.strategies(strategy).dict())