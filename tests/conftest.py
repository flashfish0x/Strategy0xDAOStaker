import pytest
from brownie import config, Wei, Contract

# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


# this is the pool ID that we are staking for. 0-3, wftm-mim
@pytest.fixture(scope="module")
def pid():
    pid = 2
    yield pid


# this is the name we want to give our strategy
@pytest.fixture(scope="module")
def strategy_name():
    strategy_name = "Strategy"
    yield strategy_name


@pytest.fixture(scope="module")
def wftm():
    yield Contract("0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83")


@pytest.fixture(scope="module")
def weth():
    yield Contract("0x74b23882a30290451A17c44f4F05243b6b58C76d")

@pytest.fixture(scope="module")
def emissionToken():
    yield Contract("0x112dF7E3b4B7Ab424F07319D4E92F41e6608c48B")


@pytest.fixture(scope="module")
def wbtc():
    yield Contract("0x321162Cd933E2Be498Cd2267a90534A804051b11")


@pytest.fixture(scope="module")
def dai():
    yield Contract("0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E")


@pytest.fixture(scope="module")
def usdc():
    yield Contract("0x04068DA6C83AFCFA0e13ba15A6696662335D5B75")


@pytest.fixture(scope="module")
def mim():
    yield Contract("0x82f0B8B456c1A451378467398982d4834b6829c1")


# Define relevant tokens and contracts in this section
@pytest.fixture(scope="module")
def token(pid, wftm, weth, wbtc, dai, usdc, mim):
    # this should be the address of the ERC-20 used by the strategy/vault
    if pid == 0:
        token = wftm
    elif pid == 1:
        token = weth
    elif pid == 2:
        token = usdc
    yield token


@pytest.fixture(scope="module")
def whale(accounts, pid):
    # Totally in it for the tech
    # Update this with a large holder of your want token (the largest EOA holder of LP)
    if pid == 3:  # WBTC
        whale = accounts.at("0x38aCa5484B8603373Acc6961Ecd57a6a594510A3", force=True)
    elif pid == 5:  # DAI
        whale = accounts.at("0x8CFA87aD11e69E071c40D58d2d1a01F862aE01a8", force=True)
    else:
        whale = accounts.at("0xE04C26444d37fE103B9cc8033c99b09D47056f51", force=True)
    yield whale


# this is the amount of funds we have our whale deposit. adjust this as needed based on their wallet balance
@pytest.fixture(scope="module")
def amount(token, pid):  # use today's exchange rates to have similar $$ amounts
    if pid == 4:  # WBTC
        amount = 380 * (10 ** token.decimals())
    elif pid == 1:  # WETH
        amount = 50 * (10 ** token.decimals())
    elif pid == 0:  # WFTM
        amount = 250_000 * (10 ** token.decimals())
    else:  # stables
        amount = 1_000_000 * (10 ** token.decimals())
    yield amount


# Only worry about changing things above this line, unless you want to make changes to the vault or strategy.
# ----------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def other_vault_strategy():
    yield Contract("0xfF8bb7261E4D51678cB403092Ae219bbEC52aa51")


@pytest.fixture(scope="module")
def reward_token(accounts):
    reward_token = Contract("0xc165d941481e68696f43EE6E99BFB2B23E0E3114")
    yield reward_token


@pytest.fixture(scope="module")
def healthCheck():
    yield Contract("0xf13Cd6887C62B5beC145e30c38c4938c5E627fe0")


# zero address
@pytest.fixture(scope="module")
def zero_address():
    zero_address = "0x0000000000000000000000000000000000000000"
    yield zero_address


# Define any accounts in this section
# for live testing, governance is the strategist MS; we will update this before we endorse
# normal gov is ychad, 0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52
@pytest.fixture(scope="module")
def gov(accounts):
    yield accounts.at("0xC0E2830724C946a6748dDFE09753613cd38f6767", force=True)


@pytest.fixture(scope="module")
def strategist_ms(accounts):
    # like governance, but better
    yield accounts.at("0x72a34AbafAB09b15E7191822A679f28E067C4a16", force=True)


@pytest.fixture(scope="module")
def keeper(accounts):
    yield accounts.at("0xBedf3Cf16ba1FcE6c3B751903Cf77E51d51E05b8", force=True)


@pytest.fixture(scope="module")
def rewards(accounts):
    yield accounts.at("0xBedf3Cf16ba1FcE6c3B751903Cf77E51d51E05b8", force=True)


@pytest.fixture(scope="module")
def guardian(accounts):
    yield accounts[2]


@pytest.fixture(scope="module")
def management(accounts):
    yield accounts[3]


@pytest.fixture(scope="module")
def strategist(accounts):
    yield accounts.at("0xBedf3Cf16ba1FcE6c3B751903Cf77E51d51E05b8", force=True)


# # list any existing strategies here
# @pytest.fixture(scope="module")
# def LiveStrategy_1():
#     yield Contract("0xC1810aa7F733269C39D640f240555d0A4ebF4264")


# use this if you need to deploy the vault
@pytest.fixture(scope="function")
def vault(pm, gov, rewards, guardian, management, token, chain):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian)
    vault.setDepositLimit(2 ** 256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    chain.sleep(1)
    yield vault


# use this if your vault is already deployed
# @pytest.fixture(scope="function")
# def vault(pm, gov, rewards, guardian, management, token, chain):
#     vault = Contract("0x497590d2d57f05cf8B42A36062fA53eBAe283498")
#     yield vault


#  masterchef from ripae
@pytest.fixture(scope="function")
def masterchef(
    Contract
):
    # make sure to include all constructor parameters needed here

    # transfer ownership of the token to our masterchef
    masterchef = Contract("0x42D5Ef67B686934325b100EF056d4bFe2f673f8C")
    yield masterchef


# replace the first value with the name of your strategy
@pytest.fixture(scope="function")
def strategy(
    GenericMasterChefStrategy,
    strategist,
    keeper,
    vault,
    gov,
    emissionToken,
    wftm,
    guardian,
    token,
    healthCheck,
    chain,
    pid,
    strategy_name,
    strategist_ms,
    masterchef,
):
    # make sure to include all constructor parameters needed here
    strategy = strategist.deploy(
        GenericMasterChefStrategy,
        vault,
        pid,
        strategy_name,
        masterchef,
        emissionToken,
        wftm,
        True
    )
    strategy.setKeeper(keeper, {"from": gov})
    # set our management fee to zero so it doesn't mess with our profit checking
    vault.setManagementFee(0, {"from": gov})
    # add our new strategy
    vault.addStrategy(strategy, 10_000, 0, 2 ** 256 - 1, 1_000, {"from": gov})
    strategy.setHealthCheck(healthCheck, {"from": gov})
    strategy.setDoHealthCheck(True, {"from": gov})
    yield strategy


# use this if your strategy is already deployed
# @pytest.fixture(scope="function")
# def strategy():
#     # parameters for this are: strategy, vault, max deposit, minTimePerInvest, slippage protection (10000 = 100% slippage allowed),
#     strategy = Contract("0xC1810aa7F733269C39D640f240555d0A4ebF4264")
#     yield strategy
