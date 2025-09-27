// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/* OpenZeppelin v5 */
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {IERC165} from "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import {IERC4906} from "@openzeppelin/contracts/interfaces/IERC4906.sol";

/* ============================================================
 * DIPDataNFT — minimal ERC721 for dataset licenses (OZ v5 safe)
 * ============================================================*/
contract DIPDataNFT is ERC721, AccessControl, IERC4906 {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    uint256 private _nextTokenId = 1;

    // Optional linkage + per-token metadata
    mapping(uint256 => uint256) public datasetOf;      // tokenId -> datasetId
    mapping(uint256 => string)  private _tokenURIs;    // tokenId -> tokenURI

    event Minted(uint256 indexed tokenId, address indexed to, uint256 indexed datasetId, string tokenUri);

    constructor(address admin) ERC721("DIP DataNFT", "DIPNFT") {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
    }

    /**
     * DAO (minter) mints license NFT to buyer.
     */
    function mintTo(address to, uint256 datasetId, string memory tokenUri)
        external
        onlyRole(MINTER_ROLE)
        returns (uint256 tokenId)
    {
        tokenId = _nextTokenId++;
        _safeMint(to, tokenId);

        datasetOf[tokenId] = datasetId;
        _setTokenURI(tokenId, tokenUri);

        emit Minted(tokenId, to, datasetId, tokenUri);
    }

    /**
     * Admin can fix/refresh metadata
     */
    function setTokenURI(uint256 tokenId, string memory newUri)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        require(_ownerOf(tokenId) != address(0), "nonexistent");
        _setTokenURI(tokenId, newUri);
    }

    /**
     * Optional admin burn
     */
    function adminBurn(uint256 tokenId) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _burn(tokenId);
        if (bytes(_tokenURIs[tokenId]).length != 0) delete _tokenURIs[tokenId];
        if (datasetOf[tokenId] != 0) delete datasetOf[tokenId];
    }

    /* ---------------- Views ---------------- */

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "ERC721: invalid token ID");
        return _tokenURIs[tokenId];
    }

    /* ---------------- Internals ---------------- */

    function _setTokenURI(uint256 tokenId, string memory newUri) internal {
        _tokenURIs[tokenId] = newUri;
        // IERC4906 event for metadata change
        emit MetadataUpdate(tokenId);
    }

    /* ---------------- IERC165 / supportsInterface (OZ v5-safe) ---------------- */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, AccessControl, IERC165)
        returns (bool)
    {
        return
            interfaceId == type(IERC4906).interfaceId ||
            ERC721.supportsInterface(interfaceId) ||
            AccessControl.supportsInterface(interfaceId);
    }
}

/* ---------------- Minimal interfaces for DAO <-> Staking & DataCoin mint ---------------- */
interface IStakingGovBoostView {
    function stakedBalance(address user) external view returns (uint256);
    function notifyGovernanceAction(address user) external;
}

interface IDIPDataCoinMint {
    function mint(address to, uint256 amount) external;
}

/* ============================================================
 * DIPDataDAO — marketplace (no auto-approve, no purchase gating)
 * paymentToken = e.g., LSDC (ERC20)
 * dataCoin     = DIP DataCoin (18 decimals)
 * ============================================================*/
contract DIPDataDAO is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    enum Status { Pending, Approved, Rejected, Paused }

    struct Dataset {
        string cid;           // IPFS/Lighthouse CID
        string title;         // title
        string tokenUri;      // NFT metadata URI
        address creator;      // uploader / seller
        uint256 price;        // in payment token (e.g., LSDC)
        uint8   qualityScore; // informational only
        Status  status;       // lifecycle
        uint256 votes;        // approvals count

        // kept for future flexibility; NOT enforced in purchase()
        bool    tokenGated;
        uint256 minTokenForBuy; // min DataCoin balance (smallest units)
        uint256 minStakeForBuy; // min staked balance (smallest units)
    }

    /// @dev 4-way split, must sum to 10000 (100%)
    struct Split { 
        uint16 creator; 
        uint16 dao; 
        uint16 ops; 
        uint16 rewards; 
    }

    IERC20   public paymentToken;     // e.g., LSDC
    IERC20   public dataCoin;         // DIP DataCoin (18 decimals)
    DIPDataNFT  public dataNft;

    // Voting config
    uint256 public approvalVotes = 1; // demo default = 1 vote approves
    uint256 public minVoteTokenBalance;   // smallest units (0 = disabled)
    uint256 public minVoteStakedBalance;  // smallest units (0 = disabled)
    bool    public voteRequiresStake = false; // if true, require staked >= minVoteStakedBalance

    // Optional staking integration for governance boost
    address public stakingContract; // if set, DAO calls notifyGovernanceAction(voter)

    uint256 public nextDatasetId = 1;

    // Default revenue split: 80% creator, 18% DAO, 2% Ops, 0% Rewards
    Split   public split = Split({ creator: 8000, dao: 1800, ops: 200, rewards: 0 });
    address public daoTreasury;
    address public operationsTreasury;

    // ---- Rewards auto-funding sink (staking) ----
    address public rewardsSink; // if set & token matches, DAO will deposit rewards slice into staking

    // ---- Optional: Creator reward on approval (mint DataCoin once) ----
    IDIPDataCoinMint public dataCoinMinter;      // set to DataCoin (must have MINTER_ROLE granted to DAO)
    uint256          public rewardOnApproval;    // e.g., 1_000e18
    mapping(uint256 => bool) public rewardMinted;

    mapping(uint256 => Dataset) public datasets;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    /* ---------------- Events ---------------- */
    event DatasetSubmitted(uint256 indexed id, address indexed creator, string cid);
    event DatasetVoted(uint256 indexed id, address indexed voter, bool approve, uint256 votes);
    event DatasetStatus(uint256 indexed id, Status status);
    event DatasetPriceUpdated(uint256 indexed id, uint256 price);
    event Purchased(uint256 indexed id, address indexed buyer, uint256 price, uint256 tokenId);
    event PaymentTokenUpdated(address indexed token);
    event DataCoinUpdated(address indexed token);
    event SplitUpdated(uint16 creator, uint16 dao, uint16 ops, uint16 rewards);
    event TreasuriesUpdated(address dao, address ops);
    event StakingConfigured(address staking, bool voteRequiresStake, uint256 minVoteTokenBalance, uint256 minVoteStakedBalance);
    event DataCoinMinterUpdated(address minter);
    event RewardOnApprovalUpdated(uint256 amount);
    event CreatorRewarded(uint256 indexed id, address indexed creator, uint256 amount);
    event RewardsSinkUpdated(address sink);
    event RewardsForwarded(uint256 indexed id, uint256 amount, address sink, bool deposited);

    constructor(
        address _paymentToken,      // e.g., LSDC
        address _dataCoin,          // DIP DataCoin (18 decimals)
        address _dataNft,           // deployed DIPDataNFT
        address _daoTreasury,
        address _operationsTreasury
    ) Ownable(msg.sender) {
        require(_paymentToken != address(0) && _dataCoin != address(0) && _dataNft != address(0), "zero addr");
        paymentToken = IERC20(_paymentToken);
        dataCoin     = IERC20(_dataCoin);
        dataNft      = DIPDataNFT(_dataNft);
        daoTreasury        = _daoTreasury;
        operationsTreasury = _operationsTreasury;
    }

    /* ---------------- Admin ---------------- */
    function setPaymentToken(address token) external onlyOwner {
        require(token != address(0), "zero");
        paymentToken = IERC20(token);
        emit PaymentTokenUpdated(token);
    }

    function setDataCoin(address token) external onlyOwner {
        require(token != address(0), "zero");
        dataCoin = IERC20(token);
        emit DataCoinUpdated(token);
    }

    function setSplit(uint16 c, uint16 d, uint16 o, uint16 r) external onlyOwner {
        require(uint256(c) + d + o + r == 10_000, "split!=100%");
        split = Split(c, d, o, r);
        emit SplitUpdated(c,d,o,r);
    }

    function setTreasuries(address _dao, address _ops) external onlyOwner {
        daoTreasury        = _dao;
        operationsTreasury = _ops;
        emit TreasuriesUpdated(_dao,_ops);
    }

    function setGovernance(uint256 _approvalVotes) external onlyOwner {
        require(_approvalVotes > 0, "zero");
        approvalVotes = _approvalVotes;
    }

    /// @notice Configure voting gate + staking integration (all values in smallest units)
    function configureStakingVoting(
        address _staking,
        bool _voteRequiresStake,
        uint256 _minVoteTokenBalance,
        uint256 _minVoteStakedBalance
    ) external onlyOwner {
        stakingContract      = _staking; // can be zero to disable boost
        voteRequiresStake    = _voteRequiresStake;
        minVoteTokenBalance  = _minVoteTokenBalance;
        minVoteStakedBalance = _minVoteStakedBalance;
        emit StakingConfigured(_staking, _voteRequiresStake, _minVoteTokenBalance, _minVoteStakedBalance);
    }

    /// @notice Set the staking contract that will receive the rewards slice (auto-deposit on purchase)
    function setRewardsSink(address sink) external onlyOwner {
        rewardsSink = sink;
        emit RewardsSinkUpdated(sink);
    }

    /// @notice Set DataCoin minter (must have MINTER_ROLE on DataCoin)
    function setDataCoinMinter(address dc) external onlyOwner {
        dataCoinMinter = IDIPDataCoinMint(dc);
        emit DataCoinMinterUpdated(dc);
    }

    /// @notice Set reward amount minted to creator when dataset gets approved
    function setRewardOnApproval(uint256 amount) external onlyOwner {
        rewardOnApproval = amount;
        emit RewardOnApprovalUpdated(amount);
    }

    /* ---------------- Creator flow ---------------- */
    function submitDataset(
        string memory cid,
        string memory title,
        string memory tokenUri,
        uint256 price,
        uint8   qualityScore,   // informational only; no auto-approval
        bool    tokenGated,     // kept for future; ignored in purchase()
        uint256 minTokenForBuy, // kept for future; ignored in purchase()
        uint256 minStakeForBuy  // kept for future; ignored in purchase()
    ) external returns (uint256 id) {
        require(bytes(cid).length>0 && bytes(title).length>0 && bytes(tokenUri).length>0, "meta");
        id = nextDatasetId++;

        datasets[id] = Dataset({
            cid: cid,
            title: title,
            tokenUri: tokenUri,
            creator: msg.sender,
            price: price,
            qualityScore: qualityScore,
            status: Status.Pending,
            votes: 0,
            tokenGated: tokenGated,
            minTokenForBuy: minTokenForBuy,
            minStakeForBuy: minStakeForBuy
        });

        emit DatasetSubmitted(id, msg.sender, cid);
        emit DatasetStatus(id, Status.Pending);
    }

    function setDatasetPrice(uint256 id, uint256 price) external {
        Dataset storage d = datasets[id];
        require(msg.sender == d.creator || msg.sender == owner(), "forbidden");
        d.price = price;
        emit DatasetPriceUpdated(id, price);
    }

    function pauseDataset(uint256 id, bool pause) external {
        Dataset storage d = datasets[id];
        require(msg.sender == d.creator || msg.sender == owner(), "forbidden");
        d.status = pause ? Status.Paused : Status.Pending; // resume to Pending (needs votes again)
        emit DatasetStatus(id, d.status);
    }

    /* ---------------- Voting ---------------- */
    function vote(uint256 id, bool approve) external {
        Dataset storage d = datasets[id];
        require(d.status == Status.Pending, "not pending");
        require(!hasVoted[id][msg.sender], "voted");

        // Voting gate: either staked balance or token balance (configurable)
        if (voteRequiresStake) {
            require(stakingContract != address(0), "no staking");
            uint256 staked = IStakingGovBoostView(stakingContract).stakedBalance(msg.sender);
            require(staked >= minVoteStakedBalance, "stake too low");
        } else if (minVoteTokenBalance > 0) {
            require(dataCoin.balanceOf(msg.sender) >= minVoteTokenBalance, "balance too low");
        }

        hasVoted[id][msg.sender] = true;

        if (approve) {
            d.votes += 1;
            if (d.votes >= approvalVotes) {
                d.status = Status.Approved;
                emit DatasetStatus(id, Status.Approved);

                // ---- Optional: one-time reward mint to creator on approval ----
                if (!rewardMinted[id] && address(dataCoinMinter) != address(0) && rewardOnApproval > 0) {
                    // Non-blocking: if mint fails (role missing), approval still succeeds
                    try dataCoinMinter.mint(d.creator, rewardOnApproval) {
                        rewardMinted[id] = true;
                        emit CreatorRewarded(id, d.creator, rewardOnApproval);
                    } catch { /* swallow */ }
                }
            }
        }

        // Governance boost for voter (optional; non-blocking)
        if (stakingContract != address(0)) {
            try IStakingGovBoostView(stakingContract).notifyGovernanceAction(msg.sender) {} catch {}
        }

        emit DatasetVoted(id, msg.sender, approve, d.votes);
    }

    /* ---------------- Purchase (NO gating) ---------------- */
    function purchase(uint256 id) external nonReentrant returns (uint256 tokenId) {
        Dataset memory d = datasets[id];
        require(d.status == Status.Approved, "not approved");

        uint256 price = d.price;
        require(price > 0, "price=0");

        // Pull payment in
        paymentToken.safeTransferFrom(msg.sender, address(this), price);

        // Calculate slices
        uint256 c  = (price * split.creator) / 10_000;
        uint256 da = (price * split.dao)     / 10_000;
        uint256 op = (price * split.ops)     / 10_000;
        uint256 rw = price - c - da - op;    // rewards remainder

        // Payout creator / dao / ops
        if (c  > 0) paymentToken.safeTransfer(d.creator, c);
        if (da > 0 && daoTreasury != address(0)) paymentToken.safeTransfer(daoTreasury, da);
        if (op > 0 && operationsTreasury != address(0)) paymentToken.safeTransfer(operationsTreasury, op);

        bool deposited = false;
        if (rw > 0 && rewardsSink != address(0)) {
            // Auto-fund staking pool: approve & call depositRewards()
            try this._forwardRewards(rewardsSink, rw) {
                deposited = true;
            } catch {
                // fallback below
            }
        }
        if (rw > 0 && !deposited) {
            // Fallback: send to DAO treasury if sink missing or deposit failed
            if (daoTreasury != address(0)) {
                paymentToken.safeTransfer(daoTreasury, rw);
            }
        }
        emit RewardsForwarded(id, rw, rewardsSink, deposited);

        // Mint license NFT to buyer
        tokenId = dataNft.mintTo(msg.sender, id, d.tokenUri);
        emit Purchased(id, msg.sender, price, tokenId);
    }

    /// @dev helper to avoid stack-too-deep in purchase()
    function _forwardRewards(address sink, uint256 amount) external {
        require(msg.sender == address(this), "internal only");
        // make allowance for staking to pull
        IERC20(payable(address(paymentToken))).forceApprove(sink, 0);
        IERC20(payable(address(paymentToken))).forceApprove(sink, amount);
        // call deposit on staking (pulls from this DAO)
        (bool ok, ) = sink.call(abi.encodeWithSignature("depositRewards(uint256)", amount));
        require(ok, "deposit fail");
    }
}

/* ============================================================
 * DIPStaking — stake DataCoin (18d), earn LSDC (18d) rewards
 * with governance-boost when voters vote in the DAO
 * ============================================================*/
contract DIPStaking is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    IERC20 public immutable stakeToken;   // DIP DataCoin (18 decimals)
    IERC20 public immutable rewardsToken; // LSDC (18 decimals)

    address public dao; // DIPDataDAO allowed to call notifyGovernanceAction()

    struct Tier {
        string  name;
        uint256 minStake;           // smallest units (e.g., 1000e18)
        uint256 rewardsMultiplier;  // percent, 100 = 1.0x, 150 = 1.5x
    }

    struct User {
        uint256 amount;
        uint256 tierIndex;
        uint256 stakedAt;
        uint256 lastRPT; // last rewardPerToken snapshot
        uint256 boostUntil;
        uint256 boostBps;     // extra rewards in BPS, e.g. 500 = +5% (time-limited)
    }

    mapping(address => User) public users;
    mapping(uint256 => Tier) public tiers; // 0..3

    uint256 public totalStaked;
    uint256 public rewardPerToken; // scaled by 1e18
    uint256 public totalRewardsDistributed;

    uint256 private constant SCALE = 1e18;
    uint256 public constant LOCK_PERIOD = 7 days;

    // Governance boost params
    uint256 public boostDuration = 3 days;
    uint256 public boostPerVoteBps = 500; // +5% per vote
    uint256 public boostMaxBps = 2000;    // cap at +20%

    /* ---------------- Events ---------------- */
    event Staked(address indexed user, uint256 amount, uint256 tierIndex);
    event Unstaked(address indexed user, uint256 amount);
    event RewardsClaimed(address indexed user, uint256 amount);
    event RewardsDeposited(uint256 amount);
    event DaoUpdated(address dao);
    event BoostParams(uint256 duration, uint256 perVoteBps, uint256 maxBps);

    modifier onlyDAO() {
        require(msg.sender == dao, "not dao");
        _;
    }

    constructor(address _stakeToken, address _rewardsToken, address _owner) Ownable(_owner) {
        require(_stakeToken != address(0) && _rewardsToken != address(0), "zero");
        stakeToken   = IERC20(_stakeToken);   // DIP DataCoin (18)
        rewardsToken = IERC20(_rewardsToken); // LSDC (18)

        // Demo-friendly tiers (assume 18 decimals on DataCoin)
        tiers[0] = Tier("Bronze",    1 ether, 110); // +10%
        tiers[1] = Tier("Silver",   5 ether, 125); // +25%
        tiers[2] = Tier("Gold",     10 ether, 150); // +50%
        tiers[3] = Tier("Diamond", 15 ether, 200); // +100%
    }

    /* ---------------- Admin ---------------- */
    function setDAO(address _dao) external onlyOwner {
        dao = _dao;
        emit DaoUpdated(_dao);
    }

    function setBoostParams(uint256 _duration, uint256 _perVoteBps, uint256 _maxBps) external onlyOwner {
        require(_maxBps <= 5000, "too high"); // 50% cap safety
        boostDuration = _duration;
        boostPerVoteBps = _perVoteBps;
        boostMaxBps = _maxBps;
        emit BoostParams(_duration, _perVoteBps, _maxBps);
    }

    function setTier(uint256 idx, string calldata name, uint256 minStake, uint256 rewardsMult) external onlyOwner {
        require(rewardsMult >= 100, "min 1.0x");
        tiers[idx] = Tier(name, minStake, rewardsMult);
    }

    /* ---------------- Staking ---------------- */
    function stake(uint256 amount, uint256 tierIndex) external nonReentrant {
        require(amount > 0, "zero");
        require(tierIndex <= 3, "tier");
        require(amount >= tiers[tierIndex].minStake, "below min");

        _update(msg.sender);

        stakeToken.safeTransferFrom(msg.sender, address(this), amount);

        User storage u = users[msg.sender];
        u.amount += amount;
        u.tierIndex = tierIndex;
        if (u.stakedAt == 0) u.stakedAt = block.timestamp;

        totalStaked += amount;
        emit Staked(msg.sender, amount, tierIndex);
    }

    function unstake(uint256 amount) external nonReentrant {
        User storage u = users[msg.sender];
        require(amount > 0 && u.amount >= amount, "amt");
        require(block.timestamp >= u.stakedAt + LOCK_PERIOD, "locked");

        _update(msg.sender);
        _claim(msg.sender);

        u.amount -= amount;
        totalStaked -= amount;

        stakeToken.safeTransfer(msg.sender, amount);
        emit Unstaked(msg.sender, amount);
    }

    function claimRewards() external nonReentrant {
        _update(msg.sender);
        _claim(msg.sender);
    }

    function depositRewards(uint256 amount) external nonReentrant {
        require(amount > 0, "zero");
        rewardsToken.safeTransferFrom(msg.sender, address(this), amount);
        if (totalStaked > 0) {
            rewardPerToken += (amount * SCALE) / totalStaked;
        }
        totalRewardsDistributed += amount;
        emit RewardsDeposited(amount);
    }

    /* ---------------- DAO hook: grant boost on vote ---------------- */
    function notifyGovernanceAction(address user) external onlyDAO {
        User storage u = users[user];
        // extend or set boost window
        uint256 base = block.timestamp > u.boostUntil ? block.timestamp : u.boostUntil;
        u.boostUntil = base + boostDuration;

        // increment boost bps up to cap
        uint256 next = u.boostBps + boostPerVoteBps;
        u.boostBps = next > boostMaxBps ? boostMaxBps : next;
    }

    /* ---------------- Views used by DAO ---------------- */
    function stakedBalance(address user) external view returns (uint256) {
        return users[user].amount;
    }

    function pendingRewards(address user) public view returns (uint256) {
        User memory u = users[user];
        if (u.amount == 0) return 0;

        uint256 delta = rewardPerToken - u.lastRPT;
        uint256 base = (u.amount * delta) / SCALE;

        // Tier multiplier (percent)
        uint256 tiered = (base * tiers[u.tierIndex].rewardsMultiplier) / 100;

        // Governance boost (bps, time-limited)
        uint256 effBoost = block.timestamp <= u.boostUntil ? u.boostBps : 0;
        uint256 boosted = (tiered * (10_000 + effBoost)) / 10_000;

        return boosted;
    }

    /* ---------------- internals ---------------- */
    function _update(address user) internal {
        User storage u = users[user];
        if (u.lastRPT == 0) {
            u.lastRPT = rewardPerToken;
        }
    }

    function _claim(address user) internal {
        uint256 r = pendingRewards(user);
        users[user].lastRPT = rewardPerToken;
        if (r > 0) {
            rewardsToken.safeTransfer(user, r);
            emit RewardsClaimed(user, r);
        }
    }
}
