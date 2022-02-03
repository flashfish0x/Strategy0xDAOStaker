import brownie
from brownie import Contract
from brownie import config
import math



def test_live(Contract, accounts, whale, wftm, GenericMasterChefStrategy, chain):
    masterchef = Contract("0x38e5c234738F0BCC48306B00066Bcc108B12dc06")
    pid = 0
    emissionToken = Contract("0xB37fC6cA1156C0bA1daD224dd4373dad384bc6f6")
    
    old_strat = GenericMasterChefStrategy.at('0x2327585bc4E6E505459C61CBF9a358a3558D6600')

    strategist = accounts.at(old_strat.strategist(), force=True)

    wftm_vault = Contract(old_strat.vault())
    tx = old_strat.clone0xDAOStaker(wftm_vault, strategist, old_strat.rewards(), old_strat.keeper(),
        pid,
        "Addy WFTM Masterchef",
        masterchef,
        emissionToken,
        wftm,
        True, {'from': strategist})

    strategy = GenericMasterChefStrategy.at(tx.return_value)

    
    gov = accounts.at(wftm_vault.governance(), force=True)
    wftm_vault.addStrategy(strategy, 100, 0, 2 ** 256 - 1, 1_000, {"from": gov})
    old_assets = wftm_vault.totalAssets()
    strategy.harvest({'from': strategist})
    print(strategy.estimatedTotalAssets())
    chain.sleep(43200)
    chain.mine(1)

    tx = strategy.harvest({'from': strategist})
    token = Contract(wftm_vault.token())
    

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