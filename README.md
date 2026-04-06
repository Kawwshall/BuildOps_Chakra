# BuildOps Chakra

Factory Operations ERP built on Frappe for BuildOps.

## What it does
- Manage operators, captains, chiefs, and regional leads
- Create factory projects (FF - Factory Functions) with rosters
- Chiefs mark daily attendance
- Auto-calculate payments from attendance
- Operators log in to see their stats and raise discrepancies

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
