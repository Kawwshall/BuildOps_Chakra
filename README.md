# Chakra

Factory Operations ERP built on Frappe by BuildOps.

## What it does
- Manage operators, captains, chiefs, and regional leads
- Create factory projects (FF - Factory Functions) with rosters
- Chiefs mark daily attendance
- Auto-calculate payments from attendance
- Operators log in to see their stats and raise discrepancies
- Vendors submit invoices and track payment status

## Roles
- **System Manager** - Full access (admin)
- **FF Chief** - Add operators/captains, mark attendance, view projects
- **FF Operator** - View own profile, attendance history, raise discrepancies
- **FF Vendor** - Submit invoices, track payments

## DocTypes
- **Operator** - People database (operators, captains, chiefs, regional leads)
- **FF Project** - Factory project with team roster and daily rates
- **FF Roster Entry** - Links operators to projects
- **FF Attendance** - Daily attendance marked by chiefs
- **Attendance Discrepancy** - Operator-raised flags for attendance issues
- **Vendor Invoice** - Vendor billing and payment tracking

## Local Setup
This repository contains the custom Frappe app code. To run it locally, install it into an existing Frappe bench and site.

1. Create or open a working Frappe bench on your machine.
2. Clone or copy this repository into the bench `apps/chakra` directory.
3. Install the app on your site with `bench --site <your-site> install-app chakra`.
4. Run `bench --site <your-site> migrate`.
5. Start the stack with `bench start`.

After installation, link each operator login to the new `Linked User` field on the `Operator` DocType so self-service access works correctly.
