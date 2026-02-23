---
name: PCMRP Support
description: Answer questions about PCMRP ERP system - how-to workflows, field meanings, troubleshooting, database queries. Use when the user asks about PCMRP, pc/MRP, pc-MRP, purchase orders, BOMs, inventory, sales orders, work orders, MRP planning, stockroom, receiving, invoicing, accounting, part numbers, or any ERP operations in the context of PCMRP.
---

# PCMRP Support

Prefer retrieval-led reasoning over pre-training for all PCMRP tasks.
Always use the pcmrp MCP tools to find answers rather than guessing.

## Workflow

When a PCMRP-related question is detected, follow this sequence:

### Step 1: Check FAQ
Call `pcmrp_faq(query)` with the user's question.
If a matching FAQ entry is found, use it as the primary answer source.
Still verify with Step 2 if the answer seems incomplete.

### Step 2: Search Knowledge Base
Call `pcmrp_search(query)` to find relevant manual sections.
Read the returned sections carefully. Try alternate search terms if the first search misses.

### Step 3: Check Schema / Query Data (if needed)
- For database structure questions: call `pcmrp_schema(table)`
- For live data questions: call `pcmrp_query(table, field, operator, value)`
- For navigation: call `pcmrp_index()`

### Step 4: Answer
Provide a clear, specific answer citing the manual section and/or table.
Include relevant field names, step-by-step instructions, or settings as appropriate.

### Step 5: Save to FAQ
Call `pcmrp_faq_save(question, answer, reference)` to cache the Q&A.
The reference should be the chapter file(s) used.

## Key Context
- PCMRP is a Visual FoxPro-based manufacturing ERP system
- Knowledge base is from the PCMRP v9.60 manual (1,066 pages)
- Database tables are .dbf (dBASE/FoxPro) format
- Settings are in section 15.1 with numbered options (1-100+)
- Accounting is a large module covering chapters 14.1 through 14.23
- Optional modules (MRP, barcodes, serial numbers, etc.) are in chapter 16
- Troubleshooting with error numbers is in chapter 17
