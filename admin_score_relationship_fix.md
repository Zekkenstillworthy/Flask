# SQLAlchemy Relationship Fix for AdminScore

## Problem

The application was encountering a SQLAlchemy error:

```
NoForeignKeysError: Could not determine join condition between parent/child tables on relationship AdminScore.user - there are no foreign keys linking these tables. Ensure that referencing columns are associated with a ForeignKey or ForeignKeyConstraint, or specify a 'primaryjoin' expression.
```

## Root Cause

The issue was in the `AdminScore` model's relationship with the `AdminUser` model:

1. The relationship was being defined using a string reference `'admin.models.user.AdminUser'`, but without specifying the exact join condition.
2. SQLAlchemy couldn't determine how to join these tables automatically since it couldn't properly resolve the string reference.
3. Circular import issues were also affecting the relationship definition.

## Solution

The solution involved using methods to define the relationships instead of SQLAlchemy's relationship objects:

1. Replaced the problematic relationship with methods in both models
2. Used `get_user()` method in the AdminScore model to fetch the related user
3. Used `get_scores()` method in the AdminUser model to fetch related scores
4. This approach avoids circular imports and explicit join conditions

## Implementation

### 1. Updated the `AdminScore` model:

```python
def get_user(self):
    """Get the user associated with this score"""
    from admin.models.user import AdminUser
    return AdminUser.query.get(self.user_id)
```

### 2. Updated the `AdminUser` model:

```python
def get_scores(self):
    """Get scores for this user"""
    from admin.models.score import AdminScore
    return AdminScore.query.filter_by(user_id=self.id).all()
```

## Benefits

1. **Avoids Circular Imports**: By using methods that import models only when needed, we avoid circular import issues
2. **Simplified Model Structure**: No complex relationship definitions required
3. **Explicit Control**: More explicit control over how relationships are accessed and queried
4. **Easier Debugging**: The relationship logic is now more transparent and easier to debug

## Usage Examples

To get a user's scores:
```python
user = AdminUser.query.get(1)
scores = user.get_scores()
```

To get the user for a score:
```python
score = AdminScore.query.get(1)
user = score.get_user()
```

## Alternative Approaches

We also considered:

1. Using explicit `primaryjoin` conditions with relationship objects
2. Restructuring the imports to avoid circular references
3. Consolidating the AdminScore and Score models

The method-based approach was chosen for its simplicity and reliability.
