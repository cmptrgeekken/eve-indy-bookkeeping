# Industry Bookkeeping for EvE Online

This project takes a bookkeeping approach to measure profits from industry activity.
Costs (mats, fees, ...) are calculated against returns (sell orders, contracts, ...).

## Database Setup

**apis**
* ID
* Owner
* API title
* Char-/Corpname
* Type:char|corp
* Roles:[WalletJournal,WalletTransactions,MarketOrders,IndustryJobs,Research,Contracts,ContractItems]
* Key
* vCode

```json
{
    "owner" : "the account that owns the api",
    "title" : "A title for the api visible to the owner",
    "key" : 123456,
    "vCode" : "code",
    "type" : "corp|char",
    "roles" : [ 
        "WalletJournal", 
        "WalletTransactions", 
        "MarketOrders", 
        "Contracts",
        "IndustryJobs",
        "IndustryJobsHistory",
        "Research"
    ]
}
```

Research to get BPC costs (as they go into the items). Research is not available on corp APIs.

Retrieve type (corp vs char) from `/account/APIKeyInfo.xml.aspx`.