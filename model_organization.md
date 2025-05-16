# Model Organization Guide

## Question Model

The application has a single source of truth for the Question model in `admin/models/question.py`. This model is used throughout the application, including:

- Admin module controllers and views
- User module controllers and views
- API endpoints

### Import Patterns

When importing the Question model, always use the admin module version:

```python
from admin.models.question import Question
```

## Model Sharing Strategy

To avoid model duplication and table name conflicts, we've standardized on a specific approach:

1. **Core Models** are defined in the admin module
   - Question, QuestionGroup, Class, etc.

2. **User-Specific Models** are defined in the user module
   - User, Score, EssayResponse, etc.

3. **Association Tables** are defined in the module where the primary model is defined
   - class_students is defined in the admin module 

## Avoiding SQLAlchemy Errors

Common SQLAlchemy errors related to models include:

1. **Table Already Exists**:
   ```
   sqlalchemy.exc.InvalidRequestError: Table 'question' is already defined for this MetaData instance
   ```
   
   Fix: Ensure each table is only defined once in the application. If you need to redefine a table, add `__table_args__ = {'extend_existing': True}` to the model class.

2. **Foreign Key Relationship Errors**:
   ```
   ArgumentError: Could not locate any simple equality expressions involving locally mapped foreign key columns
   ```
   
   Fix: Use `viewonly=True` for cross-module relationships or define proper foreign key constraints.

## Further Improvements

Consider moving all models to a shared models module to avoid circular imports and duplicated code.
