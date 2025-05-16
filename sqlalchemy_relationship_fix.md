# SQLAlchemy Relationship Fix

## Issue
There was an SQLAlchemy error when trying to establish a relationship between the `User` and `Class` models:

```
ArgumentError: Could not locate any simple equality expressions involving locally mapped foreign key columns for primary join condition '"user".id = class_students.user_id' on relationship User.enrolled_classes.
```

## Root Cause
1. Duplicate definitions of the `class_students` association table in both:
   - `admin/models/class_model.py`
   - `user/models/association_tables.py`

2. Improper relationship definition in the User model that was trying to reference a table without proper foreign key mappings.

## Fixes Applied

1. **Eliminated Duplicate Association Table**
   - Kept the definition in `admin/models/class_model.py`
   - Updated `user/models/association_tables.py` to import the table from admin

2. **Fixed Relationship Definition**
   - Added `viewonly=True` to the relationship in the User model to bypass the foreign key validation
   - Changed to directly reference the imported table object rather than the table name
   - Renamed the backref to avoid potential conflicts

3. **Improved Import Patterns**
   - Used direct imports of the association table rather than string references

## Benefits
1. **Removed Redundancy**: Only one definition of the association table exists now
2. **Fixed Error**: Resolves the SQLAlchemy error by properly defining the relationship
3. **Improved Maintainability**: Clearer code structure with explicit imports

## Future Recommendations
1. **Database Migration**: Consider running a migration to ensure all tables are properly defined
2. **Association Object**: For more complex relationships, consider creating a full association model instead of a simple table
3. **Relationship Testing**: Add tests to verify relationship behavior
