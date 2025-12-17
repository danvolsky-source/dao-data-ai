# Multi-DAO Data Collection Usage Examples

This document provides examples of how to use the multi-DAO collectors.

## Prerequisites

1. Install dependencies:
```bash
cd data_collection
pip install -r requirements.txt
```

2. Set up environment variables (optional for testing):
```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

## Usage Examples

### 1. Collect Data from All DAOs

Collect both Snapshot and on-chain data from all DAOs:
```bash
cd data_collection/collectors
python multi_dao_collector.py --dao all --type all
```

### 2. Collect Snapshot Data Only

Collect off-chain voting data from Snapshot.org for all DAOs:
```bash
python multi_dao_collector.py --dao all --type snapshot
```

### 3. Collect Data from Specific DAO

#### Optimism
```bash
# All data types
python multi_dao_collector.py --dao optimism --type all

# Snapshot only
python multi_dao_collector.py --dao optimism --type snapshot

# On-chain only
python multi_dao_collector.py --dao optimism --type onchain
```

#### Uniswap
```bash
# All data types
python multi_dao_collector.py --dao uniswap --type all

# Snapshot only
python multi_dao_collector.py --dao uniswap --type snapshot

# On-chain only
python multi_dao_collector.py --dao uniswap --type onchain
```

#### Aave
```bash
# All data types
python multi_dao_collector.py --dao aave --type all

# Snapshot only
python multi_dao_collector.py --dao aave --type snapshot

# On-chain only
python multi_dao_collector.py --dao aave --type onchain
```

#### Arbitrum
```bash
# All data types
python multi_dao_collector.py --dao arbitrum --type all

# Snapshot only
python multi_dao_collector.py --dao arbitrum --type snapshot

# On-chain only
python multi_dao_collector.py --dao arbitrum --type onchain
```

### 4. Run Individual Collectors

You can also run individual collectors directly:

#### Snapshot Collectors
```bash
# Arbitrum
python snapshot_collector.py

# Optimism
python optimism_collector.py

# Uniswap
python uniswap_collector.py

# Aave
python aave_collector.py
```

#### On-chain Collectors
```bash
# Arbitrum
python onchain_collector.py

# Optimism
python optimism_onchain_collector.py

# Uniswap
python uniswap_onchain_collector.py

# Aave
python aave_onchain_collector.py
```

## Without Supabase

The collectors can run without Supabase configured. They will:
- Fetch data from APIs and blockchain
- Print results to console
- Skip database storage

Example output:
```bash
$ python optimism_collector.py
============================================================
Optimism DAO Snapshot Collector
============================================================
Starting collection for optimism.eth...
Stored proposal: 0x123... - Proposal Title...
Supabase not configured - skipping vote collection
Total proposals collected: 50
```

## With Supabase

When Supabase is configured (SUPABASE_URL and SUPABASE_KEY set):
- Data is automatically stored in the database
- Syncs are tracked to avoid duplicates
- Full historical data is collected

## Environment Variables

Required for database storage:
```bash
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_service_role_key
```

Required for on-chain data collection:
```bash
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
OPTIMISM_RPC_URL=https://mainnet.optimism.io
ETHEREUM_RPC_URL=https://eth.llamarpc.com
```

Optional - Use paid RPC providers for better rate limits:
```bash
ARBITRUM_RPC_URL=https://arbitrum-mainnet.infura.io/v3/YOUR_KEY
OPTIMISM_RPC_URL=https://optimism-mainnet.infura.io/v3/YOUR_KEY
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY
```

## Automation

### Cron Job Example

Add to crontab to run daily at 2 AM:
```bash
0 2 * * * cd /path/to/dao-data-ai/data_collection/collectors && python multi_dao_collector.py --dao all --type all >> /var/log/dao-collector.log 2>&1
```

### Docker Example

Create a Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY data_collection/requirements.txt .
RUN pip install -r requirements.txt

COPY data_collection/ .
CMD ["python", "collectors/multi_dao_collector.py", "--dao", "all", "--type", "all"]
```

Build and run:
```bash
docker build -t dao-collector .
docker run -e SUPABASE_URL=xxx -e SUPABASE_KEY=yyy dao-collector
```

## Rate Limits

- **Snapshot API**: 1 request per second (built-in)
- **RPC Endpoints**: Varies by provider
  - Public RPCs: ~100 requests per minute
  - Infura/Alchemy: 100,000+ requests per day
  
The collectors include automatic rate limiting and will retry on failures.

## Troubleshooting

### Issue: Connection timeout
**Solution**: Check your internet connection or try a different RPC endpoint

### Issue: Rate limit exceeded
**Solution**: Wait a few minutes or upgrade to a paid RPC provider

### Issue: Supabase errors
**Solution**: Check your SUPABASE_URL and SUPABASE_KEY are correct

### Issue: No data collected
**Solution**: Ensure the DAO has active proposals. Some DAOs may have limited activity.

## Support

For issues or questions:
- Open an issue on GitHub
- Check the main README.md for general documentation
- Review individual collector code for specific implementation details
