# Onboarding Questionnaire (rules-based, no LLM required)

Questions that set feature flags and initial structure before the user enters the app.

1. Are you a sole proprietor / just you?  
   - Yes → enable_crews = false  
   - No / planning crews → enable_crews = true (optional)

2. Do you do recurring services (oil changes, gutter cleans, seasonal)?  
   - Yes → enable_recurring_services = true  
   - No → false

3. Do you need change orders / on-site adjustments that become billable?  
   - Yes → enable_change_orders = true

4. Do you want customers to sign on your phone?  
   - Yes → enable_signatures = true

5. Do you track materials / tools inventory?  
   - Yes → enable_inventory = true

6. Do you work with vehicles (mobile mechanic)?  
   - Yes → enable_vehicles = true

7. Do you measure linear footage or areas (gutters, roofing, fencing)?  
   - Yes → enable_measurements = true

8. Common vendors / suppliers you order from? (text, optional)  
   → seeds notes or future adapters

9. Primary trade(s)? (multi-select: auto, gutters, roofing, fencing, tree, HVAC, demolition, other)  
   → sets trade_tag defaults in pricebook, starter items

Result: config.json written, starter pricebook and example customer created, onboarding_completed = true.

All answers are checkboxes or short free text. Editable later from settings.
