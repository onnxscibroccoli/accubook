# Accubook Design Foundation

## Origin

HyperCard → Excel/VB AccuLube system (Hingham, MA, on-location oil changes since ~1980s/90s):

- Flyer-style invoice with prices.
- Next scheduled oil change / due date.
- Paid checkbox.
- Lookup by name, phone, address → vehicle + job.
- Print carbon-copy slips.
- Reminders.

This is the standard. Feature count is secondary to workflow fit.

Other experience:

- Jonas Construction: strong scheduler, weak field-tech consumables (forced drop-downs), hard invoice lookup/export.
- Total Office Manager: billing folder patterns, custom lookup software needed.
- AccuLynx: role friction, admin gates prevented fixes.
- Field work (gutters, fencing, roofing, demolition, tree): need materials, measurements, change orders, signatures on phone.

## Data Model (local CSV workspace)

Workspace root:

```
workspace/
  config.json                 # feature flags, custom field order, module settings
  customers.csv
  properties.csv              # or sites
  jobs.csv
  job_lines.csv               # billing lines, materials, free-text notes
  change_orders.csv
  change_order_lines.csv
  pricebook.csv
  inventory_materials.csv     # optional
  inventory_tools.csv         # optional
  job_site_materials.csv      # optional
  vehicles.csv                # optional module
  measurements.csv            # optional (linear ft, etc.)
  photos/                     # job_id/ subdirs
  signatures/                 # job_id or change_order_id
```

### Core Schemas

**customers.csv**

id,name,phone,email,address,notes,created,updated,custom_fields_json

**jobs.csv**

id,customer_id,property_id,title,status,due_date,paid,paid_date,color,notes,created,updated,next_service_due,recurring_interval_months

**job_lines.csv**

id,job_id,order,description,qty,unit,cost,sell_price,type,source_pricebook_id,created

(type: billing | material | note | labor)

**change_orders.csv**

id,job_id,status,delta_total,acknowledged_at,signature_id,created

status: proposed | acknowledged | invoiced

**pricebook.csv**

id,item,unit,cost,sell_price,trade_tag,notes

### Feature Flags (config.json)

```json
{
  "enable_crews": false,
  "enable_inventory": false,
  "enable_recurring_services": true,
  "enable_change_orders": true,
  "enable_signatures": true,
  "enable_vehicles": false,
  "enable_measurements": false,
  "field_order": ["customer", "property", "job", "lines", "photos", "signature"],
  "custom_fields": {}
}
```

Owner can edit flags and field order from UI. No admin role required for solo.

### Key Behaviors

- **Universal search**: scan all CSVs + notes for any term. Return matching customers/jobs/lines.

- **Pricebook type-ahead**: on typing in line description, match item, insert cost + sell_price, allow override or free-text.

- **Change order**: child of job. Add lines → show delta → customer signs on device → status=acknowledged → billable.

- **Signature**: finger capture + optional front-camera frame (user controlled). Store image + timestamp + SHA-256 hash of (document content + signature bytes). Tamper-evident.

- **Recurring**: on job complete, set next_due from interval. Dashboard lists due. Printable slips.

- **Reorderable**: every collection (lines, photos, custom fields) has `order` integer. Long-press to reorder, hide, or move sections.

- **Inventory layers** (flagged): company materials (linked to pricebook), job-site materials, tools (checkout status).

- **Trade modules**: additional CSVs or columns activated by flag. No code fork.

- **Invoice export**: select unpaid → export to folder or share intent (PDF or CSV).

- **Onboarding**: simple questionnaire (checkboxes + short text) sets initial flags and creates starter pricebook/customers.

## Future (not in core)

- P2P sync: main app generates key → share via RCS/email/text → worker app loads key → encrypted job updates peer-to-peer.
- Supplier adapters (SRS, QXO, ABC, Lansing) as optional modules.
- Autonomous migration from other CRMs (Jonas, AccuLynx, etc.) via mapping scripts.

All stays editable by the business owner. No permission gates.
